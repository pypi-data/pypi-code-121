# -*- coding: utf-8 -*-

import sys
import tuxsuite.cli.colors as colors
from tuxsuite.cli.requests import get


LIMIT = 50


def datediff(one, two):
    if one is None:
        return two

    if one == two:
        return f"{colors.white}{two}{colors.reset}"

    index = 0
    for (o, t) in zip(one, two):
        if o != t:
            break
        index += 1

    return f"{colors.white}{two[0:index]}{colors.reset}{two[index:]}"


def fetch_next(cmd_cls, cfg, url, next_token, limit):
    ret = get(cfg, url, params={"start": next_token})
    cmd_name = url.split("/")[-1]
    next_token = ret.json()["next"]
    res = [cmd_cls.new(**r) for r in ret.json()["results"][:limit]]
    if next_token:
        input(f"\nPress [ENTER] to see next list of {cmd_name}, or Ctrl-C to quit:\n")
    else:
        sys.exit(0)
    return (res, next_token)
