from . import Node, Collection, Empty, Comment

def _open(el):
    label = [el.tag]
    for k, v in el.attrib.items():
        label.append(f'{k}="{v}"' if v != "" else k)
    return " ".join(label)


def _write(write, el, indent, level, end):
    ind = level*indent
    if isinstance(el, Node):
        write(f"{ind}<{_open(el)}>{el.text}</{el.tag}>{end}")
    elif isinstance(el, Collection):
        write(f"{ind}<{_open(el)}>{end}")
        for child in el:
            _write(write, child, indent, level+1, end)
        write(f"{ind}</{el.tag}>{end}")
    elif isinstance(el, Empty):
        write(f"{ind}<{_open(el)} />{end}")
    elif isinstance(el, Comment):
        write(f"{ind}<!-- {el.text} -->")
    else:
        raise TypeError


def tostring(el, level=0, indent="  ", end="\n"):
    import io
    stream = io.StringIO()
    _write(stream.write, el, indent, level, end)
    return stream.getvalue()


def treeprint(el, level=0, indent="  ", end="\n"):
    import sys
    _write(sys.stdout.write, el, indent, level, end)
    sys.stdout.flush()
