# -*- coding: utf-8 -*-
import os.path
import sys

from .biz.sync import *


def execute():
    # sys.setdefaultencoding("utf-8")
    init(is_debug_mode())
    args = sys.argv
    d("execute invoke, args:" + str(args))
    base_dir = os.path.abspath(".")
    arg_len = len(args)
    if arg_len > 3:
        e("sorry, incorrect number of parameters. ")
        e("please checkout something useful by '--help'.")
        return
    # 未输入参数，默认更新当前目录层级的协议
    if arg_len <= 1:
        sync_dir(base_dir)
        return
    option = args[1]
    if option == "--help" or option == "-h":
        _print_help()
        return
    if option == "--version" or option == "-v":
        _print_version()
        return
    if option.startswith("--set-"):
        k = option.replace("--set-", "")
        v = args[2]
        setup_config(k, v)
        return
    if option == "-f" or option == "--feat":
        sync_demand(args[2])
        return
    if option == "-n" or option == "--name":
        sync_names(args[2])
        return
    if option == "-u" or option == "--update":
        sync_dir(base_dir)
        return
    w("输入的参数暂不支持，请输入--help查看")


def _print_help():
    print("pcs-get [option] <param_value>")
    print("options:")
    print("     none,               - 无选项，更新当前目录层级已存在的协议")
    print("     -u, --update,       - 更新当前目录层级已存在的协议")
    print("     -f, --feat,         - 按需求编号同步协议")
    print("     -n, --name,         - 按协议名称同步协议，如有多个协议名按英文逗号拼接")
    print("     --set-token,        - 可选项，协议管理系统的csrftoken, 用于维持登录状态，可从浏览器开发者工具中查看Header获取")
    print("     --set-session,      - 可选项，协议管理系统的sessionid, 用于维持登录状态，可从浏览器开发者工具中查看Header获取")
    print("     --set-user,         - 可选项，用户名（oa账号），用于cookie过期时的自动登录")
    print("     --set-password,     - 可选项，密码，用于cookie过期时的自动登录")
    print("     --set-lang,         - 协议文件格式，可选：java(默认), kotlin, kotlin-marshallize(TODO)，swift(TODO), oc(TODO)")
    print("     -h, --help,         - 帮助")
    print("     -v, --version,      - 版本")


def _print_version():
    print("0.9.15")
    print("2022-05-05")
    print("based on Python3.8")


if __name__ == '__main__':
    execute()
