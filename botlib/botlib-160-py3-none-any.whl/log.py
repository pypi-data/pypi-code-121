# This file is placed in the Public Domain.


"enter txt"


from .obj import Class, Object


class Log(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


Class.add(Log)