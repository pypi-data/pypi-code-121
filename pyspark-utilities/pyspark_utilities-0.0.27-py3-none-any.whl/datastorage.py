from abc import ABC


class DataStorage(ABC):

    def __init__(self, args, spark):

        self.args = args
        self.spark = spark

    # abstract method
    def load_dataset(self, read_all=True):
        pass

    # abstract method
    def save_dataset(self, df, output_dest):
        pass
