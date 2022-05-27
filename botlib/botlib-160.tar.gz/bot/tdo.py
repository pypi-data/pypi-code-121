# This file is placed in the Public Domain.


"todo"


from .obj import Class, Object


class Todo(Object):

    def __init__(self):
        super().__init__()
        self.txt = ""


Class.add(Todo)