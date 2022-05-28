import numpy as np
import cv2 as cv
import copy
import random
from ..utils.imgUtils import ImgUtils


class Individual(object):
    """
    Класс, представляющий особь
    """
    def __init__(self, *args):
        """
        Конструктор
        :param args: количество парметров конструктора
        """
        # Если параметр 1, то это psf, устанавливаем его и устанавливаем размеры
        if len(args) == 1:
            if isinstance(args[0], np.ndarray):
                self.__psf = args[0].copy()
                if self.__psf.shape[0] != self.__psf.shape[1]:
                    raise AttributeError("Ядро смаза должно иметь одинаковую высоту и ширину".format(type(args[0])))
                self.__psf_size = self.__psf.shape[0]
                self.__score = 0.0
            else:
                raise AttributeError("Получен аргумент типа {}, а должен быть ndarray".format(type(args[0])))

        # Если параметров 2, то это начальный размер psf и boolean 'это линия'
        elif len(args) == 2:
            kernel_size = args[0]
            is_line = args[1]
            if isinstance(kernel_size, int) and isinstance(is_line, bool):
                self.__psf_size = kernel_size
                self.__score = 0.0
                self.__psf = np.zeros((kernel_size, kernel_size))
                if is_line:
                    self.__psf[int(kernel_size / 2) + 1][:] = 1.0
            else:
                raise AttributeError("Получены аргументы типа {} и {}, а должны быть int и bool".format(type(args[0]), type(args[1])))

        self.normalize()

    @property
    def psf(self):
        return self.__psf

    @psf.setter
    def psf(self, psf):
        self.__psf = psf.copy()

    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, score):
        self.__score = score

    @property
    def psf_size(self):
        return self.__psf_size

    def normalize(self):
        """
        Нормализация psf
        """
        self.__psf = ImgUtils.im2double(self.__psf)

    def __get_random_vertical_neighbor(self, row):
        """
        Выбрать индекс случайного соседа по вертикали
        :param row: номер строки элемента, вокруг которого ищется сосед
        :return: случайный индекс
        """
        down_bound = 0
        up_bound = self.__psf.shape[0] - 1

        if row == down_bound:
            return random.choice([row + 1, row + 2, row + 3])
        elif row == up_bound:
            return random.choice([row - 1, row - 2, row - 3])
        else:
            return random.choice([row + 1, row + 2, row + 3, row - 1, row - 2, row - 3])

    def __get_random_horizontal_neighbor(self, col):
        """
        Выбрать индекс случайного соседа по горизонтали
        :param col: номер столбца элемента, вокруг которого ищется сосед
        :return: случайный индекс
        """
        left_bound = 0
        right_bound = self.__psf.shape[1] - 1

        if col == left_bound:
            return random.choice([col + 1, col + 2, col + 3])
        elif col == right_bound:
            return random.choice([col - 1, col - 2, col - 3])
        else:
            return random.choice([col + 1, col + 2, col + 3, col - 1, col - 2, col - 3])

    def get_random_neighbor_position(self, row, col):
        return self.__get_random_vertical_neighbor(row), self.__get_random_horizontal_neighbor(col)

    def __upscale_fill(self, new_psf_size):
        """
        Увеличение размера ядра путем растягивания (масштабирования)
        :param new_psf_size: новый размер ядра
        """
        multiplier = new_psf_size / self.__psf_size
        self.__psf_size = new_psf_size
        self.__psf = copy.deepcopy(cv.resize(self.__psf, None, fx=multiplier, fy=multiplier, interpolation=cv.INTER_LINEAR))

    def __upscale_pad(self, new_psf_size):
        """
        Увеличение размера ядра путем добавления нулей по краям
        :param new_psf_size: новый размер ядра
        """
        result = np.zeros((new_psf_size, new_psf_size), np.float32)
        difference = new_psf_size - self.__psf.shape[0]
        start_pos = int(difference / 2)
        result[start_pos:start_pos + self.__psf.shape[0], start_pos:start_pos + self.__psf_size] = copy.deepcopy(self.__psf)
        self.__psf = copy.deepcopy(result)
        self.__psf_size = new_psf_size
        return result

    def upscale(self, new_psf_size, upscale_type):
        if upscale_type == "pad":
            self.__upscale_pad(new_psf_size)
        elif upscale_type == "fill":
            self.__upscale_fill(new_psf_size)
        else:
            raise AttributeError("Wrong type of upscale type")
        self.normalize()
