import getopt
import sys

import dataclasses
import json
import os
import re
from dataclasses import dataclass

from lark import Lark, Tree

struct_member_type_pattern = re.compile(r'^#: (int|string|address)$')
function_inputs_pattern = re.compile(r'^#: \((.*?)\)')
function_outputs_pattern = re.compile(r'^#: .* -> \((.*)\)')


@dataclass
class Parameter:
    type: str
    name: str


@dataclass
class Struct:
    name: str
    members: list
    type: str = "struct"


@dataclass
class Function:
    name: str
    inputs: list
    outputs: list
    type: str = "function"


grammar_file = os.path.join(os.path.dirname(__file__), "cairo.ebnf")
parser = Lark(
    open(grammar_file, "r").read(),
    start="cairo_file",
    lexer="basic",
    parser="lalr",
    propagate_positions=True
)


def parse_parameter_hint(comment):
    if comment is None:
        return comment
    # TODO we want to throw decent errors using the parse token
    matches = struct_member_type_pattern.match(comment)
    if matches is None:
        return None

    return matches.group(1)


def get_struct_members(tree: Tree):
    members = []
    for child in tree.children:
        if isinstance(child, Tree) and child.data == 'commented_code_element':

            name = child.children[0].children[0].children[0].children[0].value
            original_type = child.children[0].children[0].children[1].data
            if original_type == 'type_struct':
                original_type = child.children[0].children[0].children[1].children[0].children[0].value
            elif original_type == 'type_felt':
                original_type = 'string'

            type_hint = parse_parameter_hint(child.children[1].value if child.children[1] is not None else None)
            type = type_hint if type_hint is not None else original_type

            members.append(Parameter(
                name=name,
                type=type
            ))
    return members


def handle_struct(tree: Tree):
    name = ''
    members = []
    for child in tree.children:
        if isinstance(child, Tree) and child.data == 'identifier_def':
            name = child.children[0].value
        if isinstance(child, Tree) and child.data == 'code_block':
            members += get_struct_members(child)
    return Struct(name=name, members=members)


def get_function_parameters(comment, pattern):
    if comment is None:
        return comment

    matches = pattern.match(comment)
    if matches is None:
        return None

    parameters = []
    raw_inputs = matches.group(1).split(',')
    for raw_input in raw_inputs:
        name, type = raw_input.split(":")
        parameters.append(Parameter(name=name.strip(), type=type.strip()))

    return parameters


def handle_function(tree: Tree):
    name = ''
    inputs = []
    outputs = []
    for child in tree.children:
        if isinstance(child, Tree) and child.data == 'identifier_def':
            name = child.children[0].value
        if isinstance(child, Tree) and child.data == 'code_block':
            type_hint = child.children[0].children[1].value
            inputs += get_function_parameters(type_hint, function_inputs_pattern)
            outputs += get_function_parameters(type_hint, function_outputs_pattern)
            pass
    return Function(name=name, inputs=inputs, outputs=outputs)


def parse(text):
    parse_tree: Tree = parser.parse(text)

    structs = []
    functions = []

    for node in parse_tree.iter_subtrees():
        if node.data == 'code_element_struct':
            structs.append(handle_struct(node))
        if node.data == 'code_element_function':
            functions.append(handle_function(node))

    structs = [dataclasses.asdict(s) for s in structs]
    functions = [dataclasses.asdict(f) for f in functions]

    return json.dumps(structs + functions)


def generate(inputfile, outputfile):
    input = open(inputfile, "r")
    fileContents = input.read()
    result = parse(fileContents)
    output = open(outputfile, "a")
    output.write(result)
    input.close()
    output.close()


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    input_file = ''
    output_file = ''
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input=", "output="])
    except getopt.GetoptError:
        print("test.py -i <inputfile> -o <outputfile>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("test.py -i <inputfile> -o <outputfile>")
            sys.exit()
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg
        else:
            print('cairo_type_hints.py --help')
            sys.exit(2)

    if input_file == "":
        print("Input file not set")
        sys.exit(2)

    if output_file == "":
        print("Output file not set")
        sys.exit(2)

    generate(input_file, output_file)


if __name__ == "__main__":
    sys.exit(main())
