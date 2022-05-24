import os
import time

from collections import ChainMap

from .logging import log, print_t, print_e

from .xgui_util import send_keys, send_combined
from .replacer import replace_str

DELAY_STD = 150

send_seq_delay = DELAY_STD


# todo
# replace with builder design pattern


def send_seq(seq, interval=100 / 1000, interval_key=100 / 1000, chunk=5):
    ks = ""
    for s in seq:

        if len(ks) > 0:
            print_t("send_seq_delay", send_seq_delay)
            time.sleep(send_seq_delay / 1000)

        if type(s) == str:
            ks = str(s)
        else:
            ks = s.execute()

        if type(ks) == tuple:
            hotk, ch = ks
            send_combined(hotk, ch)
            continue

        if len(ks) > 0:
            send_keys(
                ks,
                interval=interval_key,
                chunk=chunk,
            )


class LoginParam(object):
    def __init__(self, name, autofill, url=None):
        self.name = name
        self.autofill = autofill
        self.url = url

    def __repr__(self):
        return (
            self.__class__.__name__
            + " "
            + ", ".join([self.name, str(self.autofill), str(self.url)])
        )

    def urltype(self):
        pos = self.url.find("/")
        if pos >= 0:
            return self.url[:pos]


def splitcomment(line):
    pos = line.find("#")
    if pos >= 0:
        return line[:pos].strip()
    return line


class KeyExcutor(object):
    def __init__(self):
        self.para = None

    def param(self, p, cfg=None):
        return self

    def execute(self):
        return ""

    def __str__(self):
        return self.execute()


class Tab(KeyExcutor):
    def param(self, p, cfg=None):
        if len(p) == 0:
            p = 1
        else:
            p = int(p)
        self.para = p
        return self

    def execute(self):
        s = ""
        for i in range(0, self.para):
            s += "\t"
        return s


class SelectAll(KeyExcutor):
    def execute(self):
        return ("ctrl", "a")


class Env(KeyExcutor):
    def param(self, p, cfg=None):
        if len(p) == 0:
            p = None
        self.para = p if p != None else "HOME"
        return self

    def execute(self):
        try:
            return os.environ[self.para]
        except:
            return f"UNKOWN-{self.para}"


class Delay(KeyExcutor):
    def param(self, p, cfg=None):
        print_t("delay")
        if len(p) == 0:
            p = None

        self.para = int(p) if p != None else 0

        print_t("delaying", self.para)

        return self

    def execute(self):
        print_t("delay", self.para)
        time.sleep(self.para / 1000)
        return ""


class NewDelay(KeyExcutor):
    def param(self, p, cfg=None):
        if len(p) == 0:
            p = None
        self.para = int(p) if p != None else DELAY_STD
        return self

    def execute(self):
        global send_seq_delay
        send_seq_delay = self.para
        return ""


class Autofill(object):
    def __init__(self, autofill):
        autofill = map(lambda x: splitcomment(x.strip()), autofill)
        autofill = list(filter(lambda x: len(x) > 0, autofill))

        self.autofill = autofill
        self.predef = {
            "ENTER": "\n",
            "TAB": Tab,
            "SELALL": SelectAll,
            "ENV": Env,
            "DELAY": Delay,
            "DELAYSTD": NewDelay,
        }

    def __repr__(self):
        return self.__class__.__name__ + " " + str(self.autofill)

    def get_seq(self, *para):
        cm = ChainMap(self.predef, *para)
        seq = []
        for line in self.autofill:
            if line.startswith("{") and line.endswith("}"):

                keynam, *val = line[1:-1].split()
                val = " ".join(val)

                v = cm[keynam] if keynam in cm else f"!!!UNKNOWN-{keynam}!!!"
                if type(v) != str:
                    val_r = replace_str(val, cm.maps)
                    v = v().param(val_r)
                else:
                    v = replace_str(v, cm.maps)

                seq.append(v)
            else:
                if line.startswith("\\"):
                    line = line[1:]
                seq.append(line)
        return seq
