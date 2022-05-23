import json
import geodesic.config as config
import geodesic.oauth as oauth
import argparse


def authenticate_command(args):
    auth = oauth.AuthManager()
    auth.authenticate()


def get_command(args):
    cm = config.ConfigManager()

    if args.resource == 'clusters':
        clusters, active = cm.list_configs()
        for cluster in clusters:
            if cluster == active:
                print(f"[*] {cluster}")
            else:
                print(f"[ ] {cluster}")
    elif args.resource == 'active-config':
        cfg = cm.get_active_config()
        print(json.dumps(cfg.to_dict(), indent=4, sort_keys=True))


def set_command(args):
    cm = config.ConfigManager()

    if args.resource == 'cluster':
        active = args.value
        cm.set_active_config(active)


def make_parser():
    parser = argparse.ArgumentParser(prog="geodesic")
    parser.set_defaults(func=lambda args: parser.print_help())

    subparsers = parser.add_subparsers(
        title="subcommand",
        description="valid subcommands",
        help="which action to run"
    )

    parser_authenticate = subparsers.add_parser("authenticate", help="authenticate your account for use with this API")
    parser_authenticate.set_defaults(func=authenticate_command)

    parser_get = subparsers.add_parser("get", help="get resource")
    parser_get.add_argument(
        "resource",
        choices=['clusters', 'active-config'],
        help="get specified resource. Output depends on the requested resource"
    )
    parser_get.set_defaults(func=get_command)

    parser_set = subparsers.add_parser("set", help="set resource")
    parser_set.add_argument(
        "resource",
        choices=['cluster'],
        type=str,
        help="resources to set"
    )
    parser_set.add_argument(
        "value",
        type=str,
        help="resource value to set (e.g. cluster name)"
    )
    parser_set.set_defaults(func=set_command)
    return parser


def main():
    args = make_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
