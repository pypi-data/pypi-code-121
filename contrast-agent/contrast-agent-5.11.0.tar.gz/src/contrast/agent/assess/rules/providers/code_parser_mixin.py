# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import ast
from inspect import getsourcefile
from contrast.utils.decorators import fail_quietly
from contrast.utils.module_parser import get_ast_parsed_code


class CodeParserMixin(object):
    @fail_quietly("Unable to ast parse module")
    def find_hardcoded_str(self, cls_or_module, attribute_name, code_ast):
        """
        Checks the code ast to determine if the attribute has been
        assigned to a "true" hardcoded value (string, byte, etc)
        or if it has been assigned to a function that **evaluates**
        to a "true" hardcoded value.

        For reference:
                PRIVATE_KEY = "badbad" // is a real vulnerability

                PRIVATE_KEY = os.environ.get("secret") // not a vulnerability

        We use the suggested way to parse ast nodes, by implementing
        a NodeVisitor to look for assignment nodes that assign to
        string values and relying on ast.visit to do the node traversal.

        :param cls_or_module: class or module with code to parse
        :param attribute_name: attribute of the class or module to check for
        :param code_ast: ast tree representation of code in module.
            We return it and pass it back to this method for the next call
            to prevent parsing the module more than once.
        :return:
            1. bool determining if attribute_name is found to be assigned
                to a hardcoded str value
            2. the module str of code
        """
        if not code_ast:
            path = getsourcefile(cls_or_module)
            code_ast = get_ast_parsed_code(path)

        # must use a mutable type to be able to
        # update it in a lower scope. This is needed
        # because visit_Assign cannot return a value
        hardcoded_value = []

        class AssignToStr(ast.NodeVisitor):
            VALID_VALUE_TYPES = (
                ast.Str,
                ast.IfExp,
                ast.Bytes,
            )

            def visit_Assign(self, node):
                """
                An ast Assign node represents code that assigns values.
                This node has one or many targets but one value (what
                the targets get assigned to).
                https://greentreesnakes.readthedocs.io/en/latest/nodes.html#Assign

                We look if any of the targets have an id that matches
                the attribute_name If so, we check the node's value (which
                is equivalent to the attribute value) to see if it's a str type.
                """
                for target in node.targets:
                    if not isinstance(target, ast.Name):
                        # TODO: PYT-912 handle for assignment to class/instance
                        # such as self.key = ...
                        # which would be different target types
                        continue

                    if target.id == attribute_name:
                        if isinstance(node.value, self.VALID_VALUE_TYPES):
                            hardcoded_value.append(target)
                        break

        AssignToStr().visit(code_ast)

        hardcoded_found = bool(hardcoded_value)

        return hardcoded_found, code_ast
