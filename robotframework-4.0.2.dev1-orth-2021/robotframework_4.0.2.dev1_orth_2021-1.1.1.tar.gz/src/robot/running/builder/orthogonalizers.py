import json
import os
import sys

from robot.parsing import ModelTransformer
from robot.parsing.model.blocks import TestCase
from robot.parsing.model.statements import TestCaseName

from robot.errors import VariableError

from ast import literal_eval
from copy import deepcopy
import re

from robot.running.builder.genWriter import CaseWriter, VariableWriter, KeywordWriter, SettingWriter


def find_orthogonal_identifier(raw):
    """Get valid orthogonal identifier

    $${VARNAME} -> VARNAME

    Args:
        raw: Raw identifier with `$${}`

    Returns:
        Variable name if raw identifier is valid, otherwise `None`
    """
    res = re.findall(r"[$]{2}\{([^{}]+)\}", raw)
    return res


def parse_orthogonal_factors(orth_dict, target_keys):
    """Get orthogonal factors those presented in `target_keys`

    orth_dict:
    {
        'ANIMAL': '["cat", "dog"],
        'COLOR': '["red", "green", "blue"]'
    }
    target_keys:
    {'COLOR', 'ANIMAL'}
    ->
    [[('ANIMAL', 'cat'), ('ANIMAL', 'dog')],
     [('COLOR', 'red'), ('COLOR', 'green'), ('COLOR', 'blue')]]

    Args:
        orth_dict: AST `TestCaseSection` node
        target_keys: A set contains orthgonal factors those would be called in cases

    Returns:
        List of tuples, each tuple contains orthogonal factor name and value
    """

    global value
    value = set()
    for target_keys_one in target_keys:
        target_keys_include = re.findall(r"\[.*\]", target_keys_one)
        if target_keys_include:
            for keys_dict in target_keys_include:
                target_keys_one = "".join(target_keys_one)
                value.add(target_keys_one.replace(f'{keys_dict}', ''))
    # print(value)
    for item in value:
        target_keys.add(item)

    if not orth_dict:
        return []
    orth_pairs = []

    for name in orth_dict:
        if name not in target_keys:
            continue
        # 取出正交中的值
        args = literal_eval(orth_dict[name])
        gp = []
        for i in args:
            gp.append((name, i))
        # 拆解之后放到orth_pairs中
        orth_pairs.append(gp)
    return orth_pairs


def generate_orthogonal_chunks(orth_dict, target_keys):
    def _product(args, **kwds):
        """Generate orthogonal matrix

        _product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
        _product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
        """
        pools = list(map(tuple, args)) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x + [y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)

    serialized_ofs = parse_orthogonal_factors(orth_dict, target_keys)
    # print(serialized_ofs)
    return [x for x in _product(serialized_ofs)]


def get_template_cases(node):
    raw = []
    for case in node.body:
        name = case.header.tokens[0]
        raw.append((name, case.body))
    # print(raw)
    return raw


class OrthogonalTestGenerator(ModelTransformer):

    def __init__(self, out_dir, file, model):
        self._orth_dict = {}

        self.out_dir = out_dir
        self.file = file
        if not file:
            path = out_dir
        else:
            path = out_dir + "/" + file
        if os.path.exists(path):
            os.remove(path)
        self.model = model
        self.get_key_section(model.sections)

    def get_key_section(self, body):
        # print(type(body))
        for index, section in enumerate(body):
            if "Orthogonal" in str(section):
                self.visit_OrthogonalSection(body[index])
            elif "Variable" in str(section):
                self.visit_VariableSection(body[index])
            elif "TestCase" in str(section):
                self.visit_TestCaseSection(body[index])
            elif "Keyword" in str(section):
                self.visit_KeywordSection(body[index])
            elif "Setting" in str(section):
                self.visit_SettingSection(body[index])

    def visit_SettingSection(self, node):
        SettingWriter(node, self.out_dir, self.file)

    def visit_OrthogonalSection(self, node):
        for factor in node.body:
            try:
                self._orth_dict[factor.tokens[0].value] = factor.tokens[1].value
            except:
                print('文件中*** Settings*** | *** Variables *** | *** Test Cases *** | *** Keywords *** 等格式有误')
                sys.exit(1)

    def visit_TestCaseSection(self, node):
        global new_case_name
        template_cases = get_template_cases(node)
        # 得到测试套件中的测试用例
        for name, body in template_cases:
            count = 1
            case_name = name.value
            # 存放正交的名称
            orth_vars = set()
            get_orthogonal_variable(body, orth_vars)
            check_orthogonal_variables(orth_vars, self._orth_dict)
            vars_for_new_cases = generate_orthogonal_chunks(
                self._orth_dict, orth_vars)

            if not vars_for_new_cases[0]:
                new_body = deepcopy(body)
                new_case = TestCase(
                    header=TestCaseName.from_params(case_name),
                    body=new_body,
                )
                node.body.insert(0, new_case)
                continue

            # Each chunk generates a new sub case
            for chunk in vars_for_new_cases:
                new_body = deepcopy(body)
                pairs = {}
                for kv in chunk:
                    pairs[kv[0]] = kv[1]

                new_case_name = replace_orthogonal_identifier(
                    new_body, pairs, count, case_name)
                new_case = TestCase(
                    header=TestCaseName.from_params(new_case_name),
                    body=new_body,
                )
                # print(new_case)
                node.body.insert(0, new_case)
                count += 1

        for _ in range(len(template_cases)):
            node.body.pop()
        node.body.reverse()
        # Case
        CaseWriter(node, self.out_dir, self._orth_dict, self.file)
        # if node:
        # return self.generic_visit(node)

    def visit_VariableSection(self, node):
        VariableWriter(node, self.out_dir, self.file)

    def visit_KeywordSection(self, node):
        KeywordWriter(node, self.out_dir, self.file)


def check_orthogonal_variables(var_list, orth_dict):
    global orth_dict_in_key, orth_dict_value_list, val_dict_key
    val_dict_key = set()
    for orth_dict_key in orth_dict:
        orth_dict_value = orth_dict[orth_dict_key]

        val_dict = re.findall(r"\{.*\}", orth_dict_value)
        # str -> dict
        if val_dict:
            orth_dict_value_list = eval(orth_dict_value)
            for dict in orth_dict_value_list:
                # save value_in_kay
                for key in dict:
                    val_dict_key.add(key)
    # print(val_dict_key)
    for var in var_list:

        res = re.findall(r"\[\'.*\'\]", var)
        if res:
            res = "".join(res)
            res = eval(res)
            # var = "".join(var)
            var = var.replace(f"{res}", "")
            for dict_var in res:
                if not dict_var in val_dict_key and not var in orth_dict:
                    raise VariableError(f"Undefined orthogonal variable: $${{{var}}}")
        else:
            if not var in orth_dict:
                raise VariableError(f"Undefined orthogonal variable: $${{{var}}}")


def get_orthogonal_variable(body, orth_vars):
    if isinstance(body, list):
        for item in body:
            get_orthogonal_variable(item, orth_vars)
    if hasattr(body, "body"):
        get_orthogonal_variable(body.body, orth_vars)
    if hasattr(body, "orelse"):
        get_orthogonal_variable(body.orelse, orth_vars)
    if hasattr(body, "header"):
        get_orthogonal_variable(body.header, orth_vars)
    if hasattr(body, "tokens"):
        # 如果找到了$${}相应的名称，放到orath_vars
        for token in body:
            oi_list = find_orthogonal_identifier(token.value)
            if oi_list:
                [orth_vars.add(x) for x in oi_list]


def replace_orthogonal_identifier(body, pairs, count, raw_name):
    global orth_value_key, oi_list_include, item
    oi_list_include = []
    case_name = deepcopy(raw_name)
    if isinstance(body, list):
        for item in body:
            case_name = replace_orthogonal_identifier(item, pairs, count,
                                                      raw_name)
    if hasattr(body, "body"):
        case_name = replace_orthogonal_identifier(body.body, pairs, count,
                                                  raw_name)
    if hasattr(body, "orelse"):
        case_name = replace_orthogonal_identifier(body.orelse, pairs, count,
                                                  raw_name)
    if hasattr(body, "header"):
        case_name = replace_orthogonal_identifier(body.header, pairs, count,
                                                  raw_name)
    if hasattr(body, "tokens"):

        # print(type(pairs))
        for pairs_key in pairs:
            # dict -> str
            if (isinstance(pairs[pairs_key], dict)):
                pairs_dict = pairs[pairs_key]
                # pairs[pairs_key] = ','.join(pairs[pairs_key])
                pairs[pairs_key] = json.dumps(pairs_dict, ensure_ascii=False)
        subcase_ident = "@%".join([x for x in pairs.values()])
        case_name = f'{count}.{raw_name}@%{subcase_ident}'
        for token in body:
            oi_list = find_orthogonal_identifier(token.value)
            # search $${}
            if oi_list:
                for item in oi_list:
                    item_str = "".join(item).replace('\\\'', '\'')
                    if re.findall(r"(\[.*\])", item_str, re.M | re.I):
                        oi_list_include = re.findall(r"(\[.*\])", item_str, re.M | re.I)

                    for key in pairs:
                        # search $${xxx['yyy']}
                        if oi_list_include:
                            for orth_value_key in oi_list_include:
                                orth_value_key = "".join(orth_value_key).strip().strip('[]\'')
                                # print(pairs[key])
                            if ":" in pairs[key] and orth_value_key in pairs[key]:
                                orth_value_dict = pairs[key]
                                orth_value_dict = eval(orth_value_dict)
                                token.value = token.value.replace(f"$${{{item}}}",
                                                                  orth_value_dict[orth_value_key])
                                break
                        else:
                            token.value = token.value.replace(f"$${{{key}}}", pairs[key])

    return case_name


