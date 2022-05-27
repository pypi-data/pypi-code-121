import attr

@attr.s
class Node:
    id: str = attr.ib(default=None)
    type: str = attr.ib(default=None)
    meta: dict = attr.ib(default=None)

    def __eq__(self, __o: object) -> bool:
        return self.id == __o.id


@attr.s
class DataNode(Node):
    pass


@attr.s
class JobNode(Node):
    pass