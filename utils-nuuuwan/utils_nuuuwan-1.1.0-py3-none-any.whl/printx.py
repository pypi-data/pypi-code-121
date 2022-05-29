import json


def print_json(d):
    print(json.dumps(d, indent=2))


if __name__ == '__main__':
    print_json(dict(name='Albert Einstein', age=6))
