import cv2 as cv
from .imgUtils import ImgUtils


class ScalePyramid(object):
    """
    Класс пирамиды четких и размытых изображений разного разрешения
    self.sizes - список размеров ядра (разрешения функции искажения)
    self.images - мапа. Ключ - разрешение ядра. Значение - tuple (четкое изображение, размытое изображение)
    """

    def __init__(self, blurred_img, min_psf_size=3, step=2, max_psf_size=23):
        """
        Конструктор
        :param blurred_img: размытое изображение
        :param min_psf_size: минимальное разрешение ядра
        :param step: приращение разрешения ядра при переходе на новый уровень пирамиды
        :param max_psf_size: максимальный размер ядра
        """
        self.__get_sizes(min_psf_size, step, max_psf_size)
        self.__build(blurred_img, max_psf_size)

    @property
    def psf_sizes(self):
        """
        Получить все размеры ядер
        :return:
        """
        return self.__psf_sizes

    @property
    def images(self):
        """
        Получить мапу с изображениями
        :return: мапа
        """
        return self.__images

    def __build(self, blurred_img, max_resolution):
        """
        Построить пирамиду
        :param blurred_img: искаженное изображение
        :param max_resolution: максимальный размер ядра (разрешение функции искажения)
        """
        self.__images = dict()
        for size in self.__psf_sizes:
            multiplier = size / max_resolution
            if multiplier != 1:
                blurred_resized = cv.resize(blurred_img, None, fx=multiplier, fy=multiplier, interpolation=cv.INTER_AREA)
            else:
                blurred_resized = blurred_img.copy()
            blurred_resized = ImgUtils.im2double(blurred_resized)
            self.__images[size] = blurred_resized

    def __get_sizes(self, min_psf_size, step, max_psf_size):
        """
        Получить размеры ядра
        :param min_psf_size: минимальный размер ядра (разрешение функции искажения)
        :param step: приращение разрешения ядра при переходе на новый уровень пирамиды
        :param max_psf_size: максимальный размер ядра (разрешение функции искажения)
        """
        self.__psf_sizes = list()
        current_kernel_size = min_psf_size
        while current_kernel_size <= max_psf_size:
            self.__psf_sizes.append(current_kernel_size)
            current_kernel_size += step

        if self.__psf_sizes[len(self.__psf_sizes) - 1] < max_psf_size:
            self.__psf_sizes.append(max_psf_size)