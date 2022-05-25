import argparse
from .generator import init
from .io import update_grader_and_notebook_version, update_notebook_version, tag_notebook
from .config import Config


def parse_dlai_grader_args():
    parser = argparse.ArgumentParser(
        description="Helper library to build automatic graders for DLAI courses."
    )
    parser.add_argument(
        "-i",
        "--init",
        action="store_true",
        help="Initialize a grader workspace with common files and directories.",
    )
    parser.add_argument(
        "-u",
        "--upgrade",
        action="store_true",
        help="Upgrade the grader and notebook version.",
    )
    parser.add_argument(
        "-v",
        "--versioning",
        action="store_true",
        help="Add version to notebook metadata that matches current grader version.",
    )
    parser.add_argument(
        "-t",
        "--tag",
        action="store_true",
        help="Add graded tag to all code cells of notebook.",
    )
    args = parser.parse_args()

    if args.init:
        init()
    elif args.upgrade:
        update_grader_and_notebook_version()
    elif args.versioning:
        c = Config()
        update_notebook_version("./mount/submission.ipynb", c.latest_version)
    elif args.tag:
        tag_notebook("./mount/submission.ipynb")

