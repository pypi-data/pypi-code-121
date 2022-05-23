from ewokscore.task import Task
from ewokscore.tests.examples.tasks.sumlist import SumList
import numpy


class PrintSum(Task, input_names=["sum"]):
    def run(self):
        if self.inputs.sum is None:
            raise ValueError("'value' should be provided")
        print("input value is", self.inputs.sum)


class SumList1(SumList):
    # as each OW request his own Task we need to create this "dummy class"
    pass


class SumList2(SumList):
    # as each OW request his own Task we need to create this "dummy class"
    pass


class SumList3(SumList):
    # as each OW request his own Task we need to create this "dummy class"
    pass


class GenerateList(Task, input_names=["length"], output_names=["list"]):
    def run(self):
        if self.inputs.length is None:
            raise ValueError("length should be provided")
        self.outputs.list = numpy.random.random(self.inputs.length) * 100.0
