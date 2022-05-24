import sys
import os
import socket
from tkinter import Tk, messagebox

from .logging import log, print_t, print_e


def get_sys_process_name():
    fnam, _ = os.path.splitext(os.path.basename(sys.argv[0]))
    return fnam


def build_file_name(fnam):
    fnam = "~" + os.sep + "." + fnam + "_socket"

    fnam = os.path.expanduser(fnam)
    fnam = os.path.expandvars(fnam)
    fnam = os.path.abspath(fnam)
    return fnam


def create_socket(port=0):

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        serversocket.bind((socket.gethostname(), port))
    except socket.error as err:
        print_e(err)
        return

    port = serversocket.getsockname()

    # become a server socket
    serversocket.listen(5)

    return serversocket


def check_instance(info_name=None, pnam=None, showmbox=True):

    if info_name == None:
        info_name = get_sys_process_name()
    if pnam == None:
        pnam = build_file_name(info_name)

    port = 0
    try:
        print_t("reading last known socket", pnam)
        with open(pnam) as f:
            port = f.read()
            port = port.strip()
            port = int(port)
            print_t("last known port", port)
    except Exception as ex:
        print_e("app-socket read", ex)

    print_t("try port", port)
    sock = create_socket(port)

    if sock == None:
        print_t("port in use !!!")
        if showmbox:
            root = Tk()
            root.withdraw()
            messagebox.showerror(
                "check task manager",
                f"there is already an instance {info_name} running!",
            )
        return
    else:
        print_t("port not in use")

    sock.close()

    sock = create_socket()

    _, port = sock.getsockname()
    print_t("new free port", port)

    try:
        print_t("writing last known socket", pnam)
        with open(pnam, "w") as f:
            f.write(str(port))
    except Exception as ex:
        print_e("app-socket write", ex)

    return sock, port
