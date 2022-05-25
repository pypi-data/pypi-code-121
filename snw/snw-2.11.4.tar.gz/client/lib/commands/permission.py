from prettytable import PrettyTable

import lib.utils as utils


def list_permission(args, auth):
    res = None
    is_json = args.display == "JSON"
    if args.subcmd == 'list':
        status_code, result = utils.permission_list(args.url, auth)
        if status_code != 200:
            raise RuntimeError(result)
        if not is_json:
            res = PrettyTable(["ID", "Name", "Description"])
            for r in result:
                if "entity_code" in r:
                    r["name"] = r["entity_code"] + ":" + r["name"]
                res.add_row([r["id"], r["name"], r["description"]])
        else:
            res = result
    return res
