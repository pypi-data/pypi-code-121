from lnrun.config import load_config
from lnrun.set_config import keys


def main(_: bool = False) -> None:
    config = load_config()
    print('configs:')
    for k in keys.keys():
        if k in config:
            print(f'\t{k}: {keys[k]}\n\t\tvalue: {config[k]}')
        else:
            print(f'\t{k}: {keys[k]}\n\t\tvalue: None')


if __name__ == '__main__':
    main()
