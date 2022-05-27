import argparse
from uuid import uuid4


def parseArgs():
    # 获取脚本参数
    ap = argparse.ArgumentParser(
        prog="trickle",
        description="Post your trickle by shell"
    )
    ap.add_argument("send", type=str, nargs="+", help="your trickle content")
    ap.add_argument("-e", "--endpoint", type=str, default="", help="trickle intg endpoint")
    ap.add_argument("-t", "--token", type=str, default='', help="your trickle account token")

    args = vars(ap.parse_args())
    return args


def get_uuid():
    return str(uuid4())