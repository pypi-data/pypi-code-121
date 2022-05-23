"""
This module parses and saves a notebook.
These two processes are kept together for a simpler testing and better parallel.

Parsing uses grammar parsing provided by parsimonous package.
You may note grammar_text variable filled with parts of grammar along with code that reconstructs a notebook.

"""

import ast
import re
from pathlib import Path
from platform import python_version
from typing import List, Tuple, Dict

import nbformat
from nbformat import NotebookNode
from parsimonious import ParseError
from parsimonious.grammar import Grammar, NodeVisitor
from tornado.web import HTTPError

from .config import get_storage_for_notebook
from .storage import AbstractStorage, StorageContext
from .utils import remove_suffix


def encode_cell_text(string: str, cell_type='md'):
    assert cell_type in ['md', 'raw']
    encoded = repr(string)[1:-1]  # remove single quotes, this escapes string
    encoded = encoded.replace(r"\'", "'").replace('"', r'\"')
    # replacing \n that is not preceded with one more \ with another real thing
    # should be rewritten with a simple function
    encoded = re.sub(r'(?<!\\)\\n', '\n', encoded)
    assert '"""' not in encoded
    evaluated = ast.literal_eval(f'"""{encoded}\n"""')
    assert evaluated == string + '\n', (string, evaluated, encoded)
    return f'"""{cell_type}\n{encoded}\n"""'


def decode_cell_text(string):
    # parse literal using python built-in method
    string_with_additional_lines = ast.literal_eval(string)
    assert isinstance(string_with_additional_lines, str)
    cell_type, *content = remove_suffix(string_with_additional_lines, '\n').split('\n')
    cell_type = str.strip(cell_type)
    return dict(
        cell_type={'md': 'markdown', 'raw': 'raw'}[cell_type],
        metadata={},
        source='\n'.join(content),
    )


class NewpyterOutputPlaceholder:
    def __init__(self, hashes):
        self.hashes = hashes


class NotebookVisitor(NodeVisitor):
    newline = '\n'

    # grammar is composed line-by-line, each line is kept next to a visitor
    grammar_text = ""
    grammar_text += r'notebook = config cells ~r"(\s*\n)*" ' + newline

    def visit_notebook(self, node, visited_children):
        config, cells, _useless_tail = visited_children
        return {
                   'cells': cells,
                   # inserting metadata for a notebook.
                   # It may be not coinciding with what jupyter considers right
                   # in this case it will constantly report that the notebook is changed
                   # need a better way to handle this in the future
                   'metadata': {'kernelspec': {'display_name': 'Python 3',
                                               'language': 'python',
                                               'name': 'python3'},
                                'language_info': {'codemirror_mode': {'name': 'ipython',
                                                                      'version': 3},
                                                  'file_extension': '.py',
                                                  'mimetype': 'text/x-python',
                                                  'name': 'python',
                                                  'nbconvert_exporter': 'python',
                                                  'pygments_lexer': 'ipython3',
                                                  'version': python_version()}},
                   'nbformat': 4,
                   'nbformat_minor': 0,
               }, config

    grammar_text += r'config = config_line* ' + newline

    def visit_config(self, node, visited_children):
        return [(k, v) for k, v in visited_children]

    grammar_text += r'config_line = "# newpyter." ~r"[a-zA-Z\.]+" ~r" ?: ?" ~r"[^\n]*\n" ' + newline

    def visit_config_line(self, node, visited_children):
        _, key, _, value = visited_children
        return key.text.strip(), value.text.strip()

    grammar_text += r'cells = cell* ' + newline

    def visit_cells(self, node, visited_children):
        return list(visited_children)

    grammar_text += r'cell = comment_like_cell/code_cell' + newline

    def visit_cell(self, node, visited_children):
        return visited_children[0]

    grammar_text += r'code_cell = code_cell_header (out_line/code_line)*' + newline

    def visit_code_cell(self, node, visited_children):
        execution_count, parsed_lines = visited_children
        code = []
        out_hashes = []
        for [[type, content]] in parsed_lines:
            if type == 'code':
                code.append(content)
            else:
                assert type == 'out'
                if content is None:
                    continue
                out_hashes.append(content)

        # last empty line added in newpy just for readability
        code = remove_suffix('\n'.join(code), '\n')

        result = dict(
            cell_type='code',
            outputs=NewpyterOutputPlaceholder(hashes=out_hashes),
            # make trusted by default
            metadata={},
            source=code,
            execution_count=execution_count,
        )

        return result

    grammar_text += r'code_cell_header = ~r"# In\[" exec_code ~r" ?\] ?\n" ' + newline

    def visit_code_cell_header(self, node, visited_children):
        _, exec_code, _ = visited_children
        return exec_code

    grammar_text += r'exec_code = ~r"\d*" ' + newline

    def visit_exec_code(self, node, visited_children):
        content = node.text
        return None if content == "" else int(content)

    grammar_text += r'code_line = !code_cell_header !comment_cell_header !out_line ~r"[^\n]*\n" ' + newline

    def visit_code_line(self, node, visited_children):
        assert isinstance(node.text, str)
        return 'code', node.text.rstrip('\n')

    grammar_text += r'out_line  = ~r"# Out: ?" output_code ~r" ?\n" ' + newline

    def visit_out_line(self, node, visited_children):
        _, output_code, _ = visited_children
        return 'out', output_code

    grammar_text += r'output_code = ("empty" / ~r"[0-9a-f]+") ' + newline

    def visit_output_code(self, node, visited_children):
        content = node.text
        return None if content == 'empty' else content

    grammar_text += r'''
    comment_like_cell = comment_cell_header (!comment_cell_tail ~r"[^\n]*\n")* comment_cell_tail
    comment_cell_header = ~r'""" ?' ("md" / "raw") "\n"
    comment_cell_tail = ~r'""" ?\n+'
    '''.strip("\n ") + newline

    def visit_comment_like_cell(self, node, visited_children):
        return decode_cell_text(node.text)

    def generic_visit(self, node, visited_children):
        """ The generic visit method, applied to everything else """
        return visited_children or node


notebook_grammar = Grammar(NotebookVisitor.grammar_text)


def check_recursively_json(node, transformation):
    """ Traverse parsed json for notebook and apply transformation to each node """
    assert isinstance(node, (int, float, list, dict, str, type(None), NewpyterOutputPlaceholder)), (node, type(node))
    if isinstance(node, list):
        node = [check_recursively_json(x, transformation) for x in node]

    if isinstance(node, dict):
        node = {
            check_recursively_json(k, transformation): check_recursively_json(v, transformation)
            for k, v in node.items()
        }

    return transformation(node)


def recompose_notebook(source: str, notebook_path: str, storage=None) -> NotebookNode:
    try:
        if not source.endswith('\n'):
            source += '\n'
        result_json_with_stubs, config = NotebookVisitor().visit(notebook_grammar.parse(source))
    except ParseError as e:
        raise HTTPError(500, f'Could not parse notebook:\n {e}')
    if storage is None:
        storage = identify_storage_from_config(config, notebook_path=notebook_path)
    result_json = replace_stub_nodes_with_real_outputs(result_json_with_stubs, storage)
    nb = nbformat.from_dict(result_json)
    nbformat.validate(nb)
    return nb


def replace_stub_nodes_with_real_outputs(json, storage):
    # traverse notebook, keep hashes
    hashes = []

    def store_id(node):
        if isinstance(node, NewpyterOutputPlaceholder):
            hashes.extend(node.hashes)
        return node

    result_json = check_recursively_json(json, transformation=store_id)
    # download content for hashes
    hash2json_output = storage.get_decrypted_fragments(hashes)

    # traverse once again, replace hashes with normal outputs
    def replace_with_output(node):
        if isinstance(node, NewpyterOutputPlaceholder):
            result = []
            for hash in node.hashes:
                result.extend(hash2json_output[hash])
            return result
        return node

    result_json = check_recursively_json(result_json, transformation=replace_with_output)
    return result_json


def identify_storage_from_config(config: List[Tuple[str, str]], notebook_path: str):
    config_dict = {}
    for k, v in config:
        config_dict.setdefault(k, []).append(v)

    try:
        version = ast.literal_eval(config_dict.pop('format', ["'v1'"])[0])
        assert version == 'v1', f'version: {version} not recognized'

        storages = config_dict.pop('storage', [])
        if len(config_dict) != 0:
            raise RuntimeError(f'Unknown config params: {config_dict}')

        if len(storages) == 0:
            return get_storage_for_notebook(notebook_filename=Path(notebook_path))
        if len(storages) > 1:
            raise NotImplementedError('Multiple storages not supported yet')

        return get_storage_for_notebook(
            notebook_filename=Path(notebook_path),
            storage_url=ast.literal_eval(storages[0])
        )
    except:
        print(f'Failed to identify storage, \n found config: {config}')
        raise


def collapse_list_of_strings(list_or_str):
    if isinstance(list_or_str, str):
        return list_or_str
    assert isinstance(list_or_str, list)
    return '\n'.join(list_or_str)


def decompose_notebook(notebook: NotebookNode, storage: AbstractStorage) -> str:
    output_lines = []
    output_lines += ["# newpyter.format: 'v1'"]
    if storage.url is not None:
        output_lines += [f'# newpyter.storage: {storage.url!r}']
    with storage.get_upload_context() as storage_context:
        for cell in notebook['cells']:
            output_lines.extend(decompose_cell(cell, storage_context))

    assert all(isinstance(x, str) for x in output_lines)
    return '\n'.join(output_lines) + '\n'


def normalize_cell_outputs(input: List[Dict]) -> List[Dict]:
    if not isinstance(input, List):
        return input
    if any(not isinstance(d, Dict) for d in input):
        return input
    return [
        dict(sorted(d.items())) for d in input
    ]


def decompose_cell(cell, storage_context: StorageContext) -> List[str]:
    cell_type = cell['cell_type']
    cell_output_lines = []
    if cell_type == "markdown":
        cell_output_lines.append(encode_cell_text(collapse_list_of_strings(cell['source']), cell_type='md'))
    elif cell_type == 'raw':
        cell_output_lines.append(encode_cell_text(collapse_list_of_strings(cell['source']), cell_type='raw'))
    else:
        assert cell_type == 'code'
        count = cell.get('execution_count', '')
        assert count is None or isinstance(count, (str, int)), (count, type(count))
        if count is None:
            count = ''
        assert count == '' or isinstance(count, int)

        cell_output_lines.append(f'# In[{count}]')
        if len(cell.get('outputs', [])) > 0:
            outputs = cell['outputs']
            if len(outputs) == 1 and 'newpyter_not_found_hash' in outputs[0].get('metadata', {}):
                # special case when hash was not downloaded, so a special insertion was made
                output_hash = outputs[0]['metadata']['newpyter_not_found_hash']
            else:
                outputs = normalize_cell_outputs(cell['outputs'])
                output_hash = storage_context.store_fragment(outputs)
            cell_output_lines.append(f"# Out: {output_hash}")
        else:
            cell_output_lines.append(f'# Out: empty')

        if isinstance(cell['source'], str):
            cell_output_lines.append(cell['source'])
        else:
            assert isinstance(cell['source'], list)
            cell_output_lines.extend(cell['source'])
        # add an empty line in the end to visually separate from the previous cell
        cell_output_lines.append('')
    return cell_output_lines
