from typing import List, Set


def generate_nodes_data_file(dist: str, all_nodes, args):
    all_content: List[str] = []
    imports: Set[str] = set()
    enums_cache: Set[str] = set()
    enums: List[str] = []
    nodes_data: List[str] = []
    node_names: List[str] = []

    for node in all_nodes:
        imports.add('from dataclasses import dataclass\n')
        node_name = node['name'].replace(' ', '')
        node_names.append(node_name)
        nodes_data.append(f"@dataclass\nclass {node_name}:\n")
        node_props = node['properties']

        for prop in node_props:
            p_type = handle_prop(enums_cache, enums, imports, args, node_name, prop)
            nodes_data.append(f"{tab}{prop['name']}: {p_type}\n")

        nodes_data.append(f"{tab}type: NodeType\n\n\n")

    enums.append(f"class NodeType(Enum):\n")
    for e_val in node_names:
        enums.append('%s%s = "%s"\n' % (tab, e_val, e_val))
    enums.append(f"\n\n")

    complex_node_data_type = generate_complex_type(imports, node_names)

    all_content.extend(imports)
    all_content.append('\n\n')
    all_content.extend(enums)
    all_content.extend(nodes_data)
    all_content.append(complex_node_data_type)

    full_text = ''.join(all_content)
    with open(f'{dist}nodedata.py', "w") as p_file:
        p_file.write(full_text)


def generate_complex_type(imports: Set[str], node_names: List[str]) -> str:
    imports.add('from typing import Union\n')
    lines: List[str] = ['@dataclass\nclass NodeDataTypes:\n']
    c_line = f"{tab}props: Union["
    for name in node_names:
        if len(c_line) + len(name) < line_length:
            c_line = f"{c_line}{name}, "
        else:
            lines.append(f"{c_line}\n")
            c_line = f"{union_prop_tab}{name}, "
    lines.append(f"{c_line[0: len(c_line) - 2]}]\n")
    return ''.join(lines)


def handle_prop(enums_cache: Set[str], enums: List[str], imports: Set[str],
                args, node_name: str, prop: dict) -> str:
    if prop['type'] == 'select':
        if prop['name'] in args['arg_group']:
            p_name = args['arg_group'][prop['name']]
            enum_values = args['arg_values'][p_name]
        else:
            p_name = prop['name']
            enum_values = prop['values']
        p_type = ''.join(word.title() for word in p_name.split('_')) + 'Enum'
        if p_name not in enums_cache:
            imports.add('from enum import Enum\n')
            enums_cache.add(p_name)
            enums.append(f"class {p_type}(Enum):\n")
            for e_val in enum_values:
                enums.append('%s%s = "%s"\n' % (tab, e_val, e_val))
            enums.append("\n\n")
        return p_type

    if prop['type'] == 'NoneType':
        return 'int' if is_one_dimension(node_name) else 'List[int]'

    if prop['type'] == 'tuple':
        imports.add('from typing import List\n')
        return 'List[int]'

    return prop['type']


def is_one_dimension(node_name):
    return '1D' in node_name


tab = ' ' * 4
union_prop_tab = ' ' * 17
line_length = 120
