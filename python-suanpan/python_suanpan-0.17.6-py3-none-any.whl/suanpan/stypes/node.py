import abc


class NodeT(object):
    @property
    @abc.abstractmethod
    def info(self):
        """the `info` of the node"""
        ...

    @property
    @abc.abstractmethod
    def inputs(self):
        """the `inputs` of the node"""
        ...

    @property
    @abc.abstractmethod
    def ins(self):
        """the `inputs` of the node, alias of `inputs`"""
        ...

    @property
    @abc.abstractmethod
    def outputs(self):
        """the `outputs` of the node"""
        ...

    @property
    @abc.abstractmethod
    def outs(self):
        """the `outputs` of the node, alias of `outputs`"""
        ...

    @property
    @abc.abstractmethod
    def params(self):
        """the `params` of the node"""
        ...

    @property
    @abc.abstractmethod
    def inargs(self):
        """a list of inputs"""
        ...

    @property
    @abc.abstractmethod
    def outargs(self):
        """a list of outputs"""
        ...

    @abc.abstractmethod
    def json(self):
        """json object of node"""
        ...
