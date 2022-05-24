# https://stackoverflow.com/questions/41353989/convert-yaml-multi-line-values-to-folded-block-scalar-style
import click
import ruamel.yaml
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString, preserve_literal


def walk_tree(base):

    def test_wrap(v):
        v = v.replace('\r\n', '\n').replace('\r', '\n').strip()
        return v if len(v) < 72 else preserve_literal(v)

    if isinstance(base, dict):
        for k in base:
            v = base[k]
            if isinstance(v, str) and '\n' in v:
                base[k] = test_wrap(v)
            else:
                walk_tree(v)
    elif isinstance(base, list):
        for idx, elem in enumerate(base):
            if isinstance(elem, str) and '\n' in elem:
                base[idx] = test_wrap(elem)
            else:
                walk_tree(elem)


@click.command()
@click.option('-o', '--output')
@click.argument('path')
def main(path, output):
    yaml = YAML(typ='safe')
    with open(path, "r") as fi:
        data = yaml.load(fi)
    walk_tree(data)
    with open(output, "w") as fo:
        yaml.dump(data, fo)


if __name__ == '__main__':
    main()
