import shutil
import bs4

def _not_empty(iterable):
    try:
        next(iterable)
        return True
    except StopIteration:
        return False

def limit_width(text, maxwidth):
    if maxwidth is None: maxwidth = shutil.get_terminal_size().columns
    if maxwidth == 0: maxwidth = 1_000_000_000
    return '\n'.join(line[:maxwidth] for line in text.split('\n'))


def repr_node(node):
    if isinstance(node, str): return repr(node)
    ret = '<{node.name}'.format(node=node)
    if 'id' in node.attrs: ret += ' id="{}"'.format(node.attrs["id"])
    if 'class' in node.attrs: ret += ' class="{}"'.format(" ".join(node.attrs["class"]))
    for k,v in node.attrs.items():
        if k not in ('id','class'): ret += ' {k}="{v}"'.format(**locals())
    return ret + '>'


def render_tree(node, depth=1):
    ret = repr_node(node)
    if isinstance(node, bs4.element.Tag) and _not_empty(node.children):
        if depth >= 1:
            for child in node.children:
                for line in render_tree(child, depth=depth-1).split('\n'): ret += '\n   ' + line
        else:
            num_descendants = sum(1 for _ in node.descendants)
            ret += '\n   ... {num_descendants}'.format(**locals())
    return ret
def print_tree(node, depth=1, maxwidth=None):
    print(limit_width(render_tree(node, depth), maxwidth))

def render_ancestors(node):
    if node.parent is None: return ''
    return render_ancestors(node.parent) + '\n' + repr_node(node)
def get_leaf_nodes_containing_text(soup, text):
    for node in soup.descendants:
        if isinstance(node, str) and not isinstance(node, bs4.element.Doctype) and text in node:
            yield node
def find_paths_to_text(soup, text, maxwidth=None):
    for node in soup.descendants:
        if isinstance(node, str) and not isinstance(node, bs4.element.Doctype) and text in node:
            print(limit_width(render_ancestors(node), maxwidth))
            print()

if __name__ == '__main__':
    from bs4 import BeautifulSoup
    from kpa.http_utils import cached_get
    soup = BeautifulSoup(cached_get('https://google.com').text, 'lxml')
    print_tree(soup.select_one('html'), depth=3)
