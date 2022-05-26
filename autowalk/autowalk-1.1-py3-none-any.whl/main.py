#!/usr/bin/python

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent ))

import argparse
import textwrap

from utils.color import C
from config import CONFIG
from formatter import IndentHelpFormator
from action import (
    JumpBase,
    RemoveConfigAction,
    RangerAction, 
    RangerFileAction,
    RangerPinAction, 
    RangerPinFileAction,
    # JumpAsyncAction, 
    # JumpSyncAction, 
    JumpClearAction, 
    JumpListAction,
    JumpJunkCleanAction,
    CatConfigFile,
    IncrWeightAction,
    DecrWeightAction
)


def main():
    CONFIG.make_config_dict()
    parser = argparse.ArgumentParser(
        # prefix_chars="-",
        add_help=False,
        formatter_class=IndentHelpFormator,
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.indent(f'''
┌─────────── AutoWalk ────────────┐
│   Global Config ~/.autowalk.py  │
 ─────────────────────────────────
''', ""))


    # group_autojump = parser.add_argument_group(
    #     C.purple('Autojump'),
    #     # description="...",
    # )
    # group_ranger = parser.add_argument_group(C.purple('Ranger'))
    # group_ranger.add_argument('-a', '--asyncjump', action=JumpAsyncAction,help=C.green("add weight async (fast but don't show detail)"))
    # group_ranger.add_argument('-s', '--syncjump', action=JumpSyncAction,help=C.green("add weight sync (slow but show detail)"))

    # Global
    parser.add_argument('-h',  action='help',help=f'{C.green("│ GEN  Conf: ")}{C.purple("~/.autowalk.py")}')
    parser.add_argument('-v',  action=CatConfigFile,help=C.green(f'│ VIEW Conf: {C.purple("~/.autowalk.py")}'))
    parser.add_argument('-r',  action=RemoveConfigAction,help=C.red( f'│ RM   Conf: {C.purple("~/.autowalk.py")}'))
    # For Ranger
    parser.add_argument('-m',  action=RangerAction,help=C.green("│ GEN & PRINT   For  Ranger"))
    parser.add_argument('-mf', action=RangerFileAction,help=C.green("│ GEN & WRITE   For  Ranger"))
    # For Ranger With Pinyin
    parser.add_argument('-p',  action=RangerPinAction,help=C.green("│ GEN & PRINT   For  Ranger"))
    parser.add_argument('-pf', action=RangerPinFileAction,help=C.green("│ GEN & WRITE   For  Ranger"))
    # For AotoJump
    parser.add_argument('-l', action=JumpListAction,help=C.green("│ LIST Weight  For Autojump"))
    parser.add_argument('-a', action=JumpBase,help=C.green("│ ADD  Weight  For ListPath"))
    parser.add_argument('-j', action=JumpJunkCleanAction,help=C.green("│ CLEAN  Junk  Path Weights"))
    parser.add_argument('-c', action=JumpClearAction,help=C.red('│ CLEAR All Autojump Weight'))
    parser.add_argument(
        '-i',
        nargs=2,
        required=False, 
        action=IncrWeightAction,
        dest=" ",
        help="│ -i <OnePath>  <OneWeight>"
    )

    parser.add_argument(
        '-d',
        nargs=2,
        required=False, 
        action=DecrWeightAction,
        dest=" ",
        help="│ -d <OnePath>  <OneWeight>"
    )

    parser.parse_args()

if __name__ == '__main__':
    main()  


