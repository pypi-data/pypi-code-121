import copy
import multiprocessing as mp
import time
import yaml
import cv2 as cv
from pathlib import Path
from .population import Population
from ..utils.imgDeconv import ImgDeconv
from ..utils.imgMetrics import SharpnessMetrics
from ..utils.imgMetrics import SimilarityMetrics
from ..utils.imgUtils import ImgUtils
from ..utils.scalePyramid import ScalePyramid
from .crossoverOperators import CrossoverOperators
from .mutationOperators import MutationOperators
from .selectionOperators import SelectionOperators


def fit_range(blurred, deconv_type, similarity_metric_type, sharpness_metric_type, population_range, empty_list):
    for individual in population_range:
        deblurred_image = ImgDeconv.do_deconv(blurred, individual.psf, deconv_type)
        individual.score = SimilarityMetrics.get_similarity(deblurred_image, blurred, similarity_metric_type)
        individual.score += SharpnessMetrics.get_sharpness(deblurred_image, sharpness_metric_type)
        empty_list.append(copy.deepcopy(individual))


def mp_fit(blurred, mp_manager, deconv_type, similarity_metric_type, sharpness_metric_type, all_population_individuals, process_count):
    population_size = len(all_population_individuals)
    population_step = int((population_size - (population_size % process_count)) / process_count)
    fitted_population_mp = mp_manager.list()

    processes = list()

    for i in range(0, process_count, 1):
        if i != process_count - 1:
            processes.append(mp.Process(target=fit_range, args=(copy.deepcopy(blurred), deconv_type, similarity_metric_type, sharpness_metric_type, all_population_individuals[i * population_step: (i + 1) * population_step], fitted_population_mp)))
        else:
            processes.append(mp.Process(target=fit_range, args=(copy.deepcopy(blurred), deconv_type, similarity_metric_type, sharpness_metric_type, all_population_individuals[i * population_step: population_size], fitted_population_mp)))

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    fitted_population = copy.deepcopy(fitted_population_mp)
    fitted_population.sort(key=lambda x: x.score, reverse=True)

    return fitted_population


class GenDeblurrer(object):
    def __init__(self, configuration, mp_manager):
        if type(configuration) is str:
            with open(configuration) as configuration_file:
                configuration = yaml.safe_load(configuration_file)

        # конфигурация селекции
        self.__selection_config = configuration["selection"]
        # конфигурация скрещивания
        self.__crossover_config = configuration["crossover"]
        # конфигурация мутации
        self.__mutation_config = configuration["mutation"]
        # конфигурация пирамиды
        self.__pyramid_config = configuration["pyramid"]
        self.__stagnation_pop_count = configuration["stagnation_population_count"]
        self.__elite_count = configuration["elite_individuals_count"]
        self.__similarity_metric_type = configuration["similarity_metric_type"]
        self.__sharpness_metric_type = configuration["sharpness_metric_type"]
        self.__deconv_type = configuration["deconvolution_type"]
        self.__results_directory_path = configuration["results_directory_path"]

        self.__base_population_size = configuration["base_population_size"]
        self.__multiprocessing_manager = mp_manager
        Path(self.__results_directory_path).mkdir(parents=True, exist_ok=True)

    def __get_best_cpu_count(self):
        # считаем, что выгоднее использовать по времени
        cpu_count = mp.cpu_count()

        start = time.time()
        self.__population.fit(self.__sharpness_metric_type, self.__similarity_metric_type, self.__deconv_type)
        end = time.time()
        single_process_time = end - start

        start = time.time()
        mp_fit(self.__population.current_blurred_image, self.__multiprocessing_manager, self.__deconv_type, self.__similarity_metric_type,
               self.__sharpness_metric_type, self.__population.individuals, int(cpu_count / 4))
        end = time.time()
        mp_quad_time = end - start

        if single_process_time < mp_quad_time:
            cpu_count = 1
        else:
            start = time.time()
            mp_fit(self.__population.current_blurred_image, self.__multiprocessing_manager, self.__deconv_type, self.__similarity_metric_type,
                   self.__sharpness_metric_type, self.__population.individuals, int(cpu_count / 2))
            end = time.time()
            mp_half_time = end - start
            if mp_quad_time < mp_half_time:
                cpu_count = int(cpu_count / 4)
            else:
                cpu_count = int(cpu_count / 2)
        return cpu_count

    def __write_result_for_pyramid_level(self):
        best_result_for_size = ImgDeconv.do_deconv(self.__population.current_blurred_image, self.__population.individuals[0].psf,
                                                   type=self.__deconv_type)
        cv.normalize(best_result_for_size, best_result_for_size, 0.0, 255.0, cv.NORM_MINMAX)

        lel_test = copy.deepcopy(self.__population.individuals[0].psf)
        best_kernel_for_size = cv.resize(lel_test, None, fx=10, fy=10, interpolation=cv.INTER_AREA)
        cv.normalize(best_kernel_for_size, best_kernel_for_size, 0, 255, cv.NORM_MINMAX)

        blurred_normalized = copy.deepcopy(self.__population.current_blurred_image)
        cv.normalize(blurred_normalized, blurred_normalized, 0, 255, cv.NORM_MINMAX)

        result_file_name = "{}/restored_size_{}.jpg".format(self.__results_directory_path, self.__population.current_psf_size)
        blurred_file_name = "{}/blurred_size_{}.jpg".format(self.__results_directory_path, self.__population.current_psf_size)
        kernel_file_name = "{}/kernel_size_{}.jpg".format(self.__results_directory_path, self.__population.current_psf_size)

        cv.imwrite(result_file_name, best_result_for_size)
        cv.imwrite(kernel_file_name, best_kernel_for_size)
        cv.imwrite(blurred_file_name, blurred_normalized)

    def deblur(self, blurred_img):
        blurred_img_gray = ImgUtils.to_grayscale(blurred_img)
        blurred_img_gray = ImgUtils.im2double(blurred_img_gray)
        scale_pyramid = ScalePyramid(blurred_img_gray,
                                     self.__pyramid_config["min_resolution"],
                                     self.__pyramid_config["step"],
                                     self.__pyramid_config["max_resolution"])
        self.__population = Population(scale_pyramid, base_population_size=self.__base_population_size)
        best_quality_in_pop = -10000000000.0
        upscale_flag = 0
        for i in range(0, len(scale_pyramid.psf_sizes), 1):
            pop_count = 0
            cpu_count = self.__get_best_cpu_count()

            while True:
                if upscale_flag == self.__stagnation_pop_count:
                    upscale_flag = 0
                    break
                start = time.time()

                if cpu_count == 1:
                    self.__population.fit(self.__sharpness_metric_type, self.__similarity_metric_type, self.__deconv_type)
                else:
                    self.__population.individuals = copy.deepcopy(mp_fit(self.__population.current_blurred_image, self.__multiprocessing_manager, self.__deconv_type, self.__similarity_metric_type, self.__sharpness_metric_type, self.__population.individuals, cpu_count))

                end = time.time()
                print(f"ELAPSED TIME: {end-start}")
                print(f"best quality in pop: {self.__population.individuals[0].score}, best quality ever: {best_quality_in_pop}")

                if self.__population.individuals[0].score > best_quality_in_pop:
                    best_quality_in_pop = copy.deepcopy(self.__population.individuals[0].score)
                    upscale_flag = 0

                # селекция
                elite_individuals, non_elite_individuals = self.__population.get_elite_non_elite(self.__elite_count)
                self.__selection_config["k"] = len(non_elite_individuals)
                selected_individuals = SelectionOperators.select(non_elite_individuals, self.__selection_config)
                # скрещивание
                crossed_individuals = CrossoverOperators.crossover(selected_individuals, self.__crossover_config)
                # мутация
                mutated_individuals = MutationOperators.mutate(crossed_individuals, self.__mutation_config)

                # обновление особей популяции
                self.__population.individuals.clear()
                self.__population.individuals.extend(copy.deepcopy(mutated_individuals))
                self.__population.individuals.extend(copy.deepcopy(elite_individuals))
                upscale_flag += 1
                pop_count += 1

            # апскейлим
            if i != len(scale_pyramid.psf_sizes) - 1:
                self.__write_result_for_pyramid_level()

                best_quality_in_pop = -10000000000.0
                self.__population.upscale(self.__pyramid_config["upscale_type"])

            if i == len(scale_pyramid.psf_sizes) - 1:
                self.__write_result_for_pyramid_level()

        return ImgDeconv.do_deconv(blurred_img,
                                   self.__population.individuals[0].psf,
                                   self.__deconv_type, K=1.0),\
               self.__population.individuals[0].psf
