import argparse

from lnrun.config import load_config, write_config

keys = {
    'script_path': 'GAS web app path',
    'send_errors': 'Capture errors will record stderr so no stderr output in terminal. (note: tqdm use stderr to print prograss bar)',
    'verbose': 'show log from curl',
}


def parse_args(additional: bool = False) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    if additional:
        parser.add_argument('COMMAND', help='command to use')
    parser.add_argument('key', help='key')
    parser.add_argument('value', help='value')
    return parser.parse_args()


def main(additional: bool = False) -> None:
    args = parse_args(additional)
    config = load_config()
    if args.key not in keys:
        print(f'key: {args.key} not exist. available options:')
        for k in keys.keys():
            print(f'{k}: {keys[k]}')
        exit()

    config[args.key] = args.value
    print(f'set {args.key} to {args.value}')
    write_config(config)


if __name__ == '__main__':
    main()
