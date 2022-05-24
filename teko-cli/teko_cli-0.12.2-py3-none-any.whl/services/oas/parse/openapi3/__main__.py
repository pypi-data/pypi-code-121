import sys
import yaml

from object_base import Map
from .openapi import OpenAPI
from pprint import pprint


def main():
    specfile = sys.argv[1]

    with open(specfile) as f:
        spec = yaml.safe_load(f.read())

    o = OpenAPI(spec, validate=True)
    print(o.__slots__)
    # for item in o.__slots__:
    #     if hasattr(getattr(o, item), '__slots__'):
    #         print_class_object()
    #     else:
    #         print(item, end=" ")
    #         # print(type(getattr(o, item)), end=" ")
    #         print(getattr(o, item))
    # print(o.__slots__)
    # attrs = vars(o)
    # print(', '.join("%s: %s" % item for item in attrs.items()))
    # regions = o.call_getRegions()
    # print(regions)
    errors = o.errors()

    if errors:
        # print errors
        for e in errors:
            print('{}: {}'.format('.'.join(e.path), e.message[:300]))
        print()
        print('{} errors'.format(len(errors)))
        sys.exit(1) # exit with error status
    else:
        print('OK')


if __name__ == '__main__':
    main()
