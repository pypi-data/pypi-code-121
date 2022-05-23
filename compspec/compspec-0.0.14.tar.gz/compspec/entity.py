__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"


class Counter:
    """
    A simple counter (iterator) that will yield the next number with some prefix.
    """

    def __init__(self, prefix="id"):
        self.prefix = prefix

    def __next__(self):
        self.count += 1
        return "%s%s" % (self.prefix, self.count)

    def __iter__(self):
        # Actually start counting at 0
        self.count = -1
        return self


def get_counter(prefix="id"):
    """
    Return an iterable counter.
    """
    counter = Counter(prefix)
    return iter(counter)


class relation:
    """
    A relation in a graph.
    """

    def __init__(self, fromid, toid, relation="has"):
        self.fromid = fromid
        self.toid = toid
        self.relation = relation

    def __iter__(self):
        return iter((self.fromid, self.relation, self.toid))

    def to_dict(self):
        return {"fromid": self.fromid, "relation": self.relation, "toid": self.toid}

    def __str__(self):
        return f"{self.fromid}.{self.relation}:{self.toid}"

    def __repr__(self):
        return str(self)

    @property
    def args(self):
        return self.fromid, self.relation, self.toid


class node:
    """
    A node in a graph.
    """

    def __init__(self, nodeid, name, value, is_connector=False):
        self.nodeid = nodeid
        self.name = name
        self.value = value
        self.is_connector = is_connector

    def __str__(self):
        return f"{self.nodeid}.{self.name}:{self.value}"

    def describe(self):
        return f"{self.name}:{self.value}"

    def __iter__(self):
        return iter((self.nodeid, self.name, self.value))

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {"nodeid": self.nodeid, "name": self.name, "value": self.value}

    @property
    def args(self):
        return self.nodeid, self.name, self.value
