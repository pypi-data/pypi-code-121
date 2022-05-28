import cv2 as cv
import numpy as np
import copy
from skimage import restoration
from .imgUtils import ImgUtils


class ImgDeconv(object):
    @staticmethod
    def __do_RL_deconv_1c(img, psf, iterations, clip=False):
        """
        Метод Люси-Ричардсона для 1 канала
        :param img: изображение
        :param psf: функция искажения
        :param iterations: количество итераций
        :param clip: см. в skimage.restoration.richardson_lucy
        :return: результат
        """
        if len(img.shape) == 2:
            image_ = np.float32(img)
            cv.normalize(image_, image_, 0.0, 1.0, cv.NORM_MINMAX)
            result = restoration.richardson_lucy(image_, psf.copy(), iterations=iterations, clip=clip,
                                                 filter_epsilon=0.01)
            result = ImgUtils.im2double(result)
            return result
        else:
            raise AttributeError("Wrong image format, image should be grayscale")

    @staticmethod
    def __do_RL_deconv(img, psf, iterations, clip):
        """
        Метод Люси-Ричардсона для любого количества каналов
        :param img: изображение
        :param psf: функция искажения
        :param iterations: количество итераций
        :param clip: см. в skimage.restoration.richardson_lucy
        :return: результат
        """
        image_ = np.float32(img)
        channels = list(cv.split(image_))
        channels[:] = [ImgDeconv.__do_RL_deconv_1c(channel, psf.copy(), iterations, clip) for channel in channels]
        result = cv.merge(channels)
        result = ImgUtils.im2double(result)
        return result

    @staticmethod
    def __do_wiener_deconv_1c(img, psf, K):
        """
        Фильтр Винера для одного канала
        :param img: фильтруемое изображение
        :param psf: функция искажения
        :param K: константа сигнал-шум
        :return: результат фильтрации
        """
        dummy = np.copy(img)
        dummy = np.fft.fft2(dummy)
        kernel = ImgUtils.pad_to_shape(psf, img.shape)
        kernel = np.fft.fft2(kernel)
        kernel = np.conj(kernel) / (np.abs(kernel) ** 2 + K)
        dummy = dummy * kernel
        dummy = np.abs(np.fft.ifft2(dummy))
        result = np.zeros(dummy.shape)
        result = np.float32(result)
        dummy = np.float32(dummy)
        cv.normalize(dummy, result, 0.0, 1.0, cv.NORM_MINMAX)
        return np.fft.fftshift(result)

    @staticmethod
    def __do_wiener_deconv(img, psf, K):
        """
        :param self:
        :param psf:
        :param K:
        :return:
        """
        image_ = np.float32(img)
        channels = list(cv.split(image_))
        channels[:] = [ImgDeconv.__do_wiener_deconv_1c(channel, psf.copy(), K) for channel in channels]
        result = cv.merge(channels)
        result = ImgUtils.im2double(result)
        return result

    @staticmethod
    def __do_divide_deconv(img, psf):
        image_cpy = copy.deepcopy(img)
        image_fft = np.fft.fft2(image_cpy)

        psf_cpy = copy.deepcopy(psf)
        psf_cpy = ImgUtils.pad_to_shape(psf, img.shape)
        psf_fft = np.fft.fft2(psf_cpy)

        result_psf = image_fft / psf_fft
        result = np.abs(np.fft.ifft2(result_psf))
        result_normalized = np.zeros(result.shape, np.float32)
        cv.normalize(result, result_normalized, 0.0, 1.0, cv.NORM_MINMAX)
        return result_normalized

    @staticmethod
    def do_deconv(image, psf, type, **kwargs):
        if type == "wiener":
            if len(kwargs) == 0:
                K = 1.0
            elif len(kwargs) == 1:
                try:
                    K = kwargs['K']
                    if not isinstance(K, float):
                        raise AttributeError("Wrong types of arguments")
                except KeyError:
                    raise AttributeError("Pass 'K' for wiener filter")
            else:
                raise AttributeError("Pass only K for wiener filter")
            return ImgDeconv.__do_wiener_deconv(image, psf, K=K)

        elif type == "LR":
            if len(kwargs) == 0:
                iterations = 10
                clip = True
            elif len(kwargs) == 2:
                try:
                    iterations = kwargs['iterations']
                    clip = kwargs['clip']
                    if not isinstance(iterations, int) or not isinstance(clip, bool):
                        raise AttributeError("Wrong types of arguments")
                except KeyError:
                    raise AttributeError("Pass iterations (int) and clip (bool)")
            else:
                raise AttributeError("Wrong number of arguments")
            return ImgDeconv.__do_RL_deconv(image, psf, iterations=iterations, clip=clip)

        elif type == "divide":
            return ImgDeconv.__do_divide_deconv(image, psf)