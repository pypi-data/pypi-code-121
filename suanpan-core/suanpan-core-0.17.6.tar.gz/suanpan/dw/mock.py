class DataWarehouse(object):
    def __init__(self, *args, **kwargs):
        pass

    def readTable(self, table, **kwargs):
        raise NotImplementedError("Must install python with Table support")

    def writeTable(self, table, data, **kwargs):
        raise NotImplementedError("Must install python with Table support")
