import threading
import numpy as np


class LockedList(list):
    def __init__(self):
        super().__init__()
        self.__lock = threading.Lock()

    def append(self, item):
        self.__lock.acquire()
        super().append(item)
        self.__lock.release()

    def extend(self, item):
        self.__lock.acquire()
        super().extend(item)
        self.__lock.release()

    def len(self):
        self.__lock.acquire()
        temp_length = len(self)
        self.__lock.release()
        return temp_length

    def get_amount_and_clear(self, amount):
        self.__lock.acquire()
        if len(self) > amount:
            temp_list = self[:amount]
            del self[:amount]
        else:
            temp_list = self[:len(self)]
            self.clear()
        self.__lock.release()
        return temp_list

    def get_all_and_clear(self):
        self.__lock.acquire()
        temp_list = self[:len(self)]
        self.clear()
        self.__lock.release()
        return temp_list


class AggregatedMatrix:
    def __init__(self, shape, use_arithmetic_mean: bool = False):
        self.__use_arithmetic_mean = use_arithmetic_mean
        self.__num_aggregations = 0
        if self.__use_arithmetic_mean:
            self.__matrix = np.zeros(shape)
        else:
            self.__matrix = np.ones(shape)

    def aggregate(self, matrix, index):
        if self.__use_arithmetic_mean:
            self.__matrix[:, :, :, index] = self.__matrix[:, :, :, index] + matrix[:, :, :, 0]
        else:
            self.__matrix[:, :, :, index] = np.multiply(self.__matrix[:, :, :, index], matrix[:, :, :, 0])
        if index == 0:
            self.__num_aggregations += 1

    def __calc_loop_domains(self):
        self.__matrix[:, :, :, -1] = np.sqrt(self.__matrix[:, :, :, 0] * self.__matrix[:, :, :, 1])

    def get_final_result(self):
        if self.__use_arithmetic_mean:
            self.__matrix = self.__matrix / self.__num_aggregations
        else:
            self.__matrix = np.power(self.__matrix, 1.0 / self.__num_aggregations)
        self.__calc_loop_domains()
        return self.__matrix
