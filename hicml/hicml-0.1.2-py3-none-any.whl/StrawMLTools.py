import gc
import threading
import time
import tensorflow as tf
import numpy as np
import hicstraw
from concurrent.futures import ThreadPoolExecutor

from hicml.NonMaxSuppression import Handler
from hicml.PredictionHandler import find_bound_in_connected_components, find_max_in_connected_components
from hicml.DataStructures import LockedList, AggregatedMatrix


class DeploySpears:
    def __init__(self, all_model_sets: list, batch_size: int, num_straw_workers: int, filepath: str,
                 resolution: int, max_examples_in_ram: int, matrix_width: int, threshold: float,
                 out_files: list, preprocess_method,
                 use_arithmetic_mean: bool = False, norm: str = "KR",
                 num_output_channels: int = 3, chromosome_subset: list = None,
                 use_multithreading: bool = True):
        self.__straw_data_list = LockedList()
        self.__coords_list = LockedList()
        self.__prediction_list = LockedList()
        self.__straw_worker_done_counter = LockedList()
        self.__production_done = threading.Event()
        self.__prediction_done = threading.Event()
        self.__lock = threading.Lock()
        self.__all_model_sets = all_model_sets
        self.__use_arithmetic_mean = use_arithmetic_mean
        self.__batch_size = batch_size
        self.__num_straw_workers = num_straw_workers
        self.__num_total_workers = num_straw_workers + 3
        self.__hic_file = filepath
        self.__resolution = resolution
        self.__limit = max_examples_in_ram
        self.__width = matrix_width
        self.__threshold = threshold
        self.__norm = norm
        self.__out_files = out_files
        self.__num_output_channels = num_output_channels
        self.__preprocess_input = preprocess_method
        self.__nms_handlers = []
        for k in range(num_output_channels + 1):
            self.__nms_handlers.append(Handler())
        self.__mzd_dict, self.__num_total_slices = self.fill_out_all_indices(filepath, resolution, norm,
                                                                             chromosome_subset)
        if use_multithreading:
            self.__predict_from_model()
        else:
            self.__predict_from_model_single_thread()

    def grab_region(self, chrom1, cx1, cx2, cy1, cy2):
        mzd = self.__mzd_dict[chrom1]
        return mzd.getRecordsAsMatrix(cx1, cx2, cy1, cy2)

    def __predict_from_model(self):
        results = []
        with ThreadPoolExecutor(max_workers=self.__num_total_workers) as executor:
            for i in range(self.__num_straw_workers):
                results.append(executor.submit(self.get_all_data_slices))
            results.append(executor.submit(self.run_model_predictions))
            results.append(executor.submit(self.generate_bedpe_annotation))
            print('All jobs submitted', flush=True)
        for res in results:
            if not res.running():
                res.result()
        return results

    def handle_predictions(self, current_size, prediction, section):
        for k in range(current_size):
            self.__prediction_list.append((prediction[k, :, :, :], section[k][1]))

    def run_model_predictions(self):
        print('run models')
        num_done_counter = 0.0
        while not (self.__production_done.is_set() and self.get_num_data_points() == 0):
            section = self.__straw_data_list.get_amount_and_clear(self.__batch_size)
            current_size = len(section)
            if current_size == 0:
                time.sleep(2)
                continue

            raw_hic_input = np.zeros((current_size, self.get_width(), self.get_width(), 3))
            for k in range(current_size):
                raw_hic_input[k, :, :, :] = section[k][0]
            raw_hic_input = tf.constant(raw_hic_input)
            agg_matrix = AggregatedMatrix((current_size, self.get_width(), self.get_width(),
                                           self.__num_output_channels + 1), self.__use_arithmetic_mean)
            for p in range(len(self.__all_model_sets)):
                for model in self.__all_model_sets[p]:
                    agg_matrix.aggregate(model.predict(raw_hic_input), p)
            result = agg_matrix.get_final_result()

            self.handle_predictions(current_size, result, section)
            num_done_counter += current_size
            print('Progress ', 100. * (num_done_counter / self.__num_total_slices), '%  done', flush=True)
        time.sleep(2)
        self.__prediction_done.set()

    def get_data_from_coordinates(self, coordinates, resolution):
        (chrom1, x1, y1) = coordinates
        cx1 = x1 * resolution
        cx2 = (x1 + self.get_width() - 1) * resolution
        cy1 = y1 * resolution
        cy2 = (y1 + self.get_width() - 1) * resolution
        return self.grab_region(chrom1, cx1, cx2, cy1, cy2)

    def fill_out_all_indices(self, hic_file_path, resolution, norm, chromosome_subset):
        hic_file_obj = hicstraw.HiCFile(hic_file_path)
        chrom_dot_sizes = hic_file_obj.getChromosomes()
        num_total_slices = 0
        chromosomes_to_use = []
        if chromosome_subset is not None:
            for chromS in chromosome_subset:
                chromosomes_to_use.append(chromS.lower())

        for chromosome in chrom_dot_sizes:
            chrom = chromosome.name
            if chrom.lower() == 'all':
                continue
            if len(chromosomes_to_use) > 0 and chrom.lower() not in chromosomes_to_use:
                continue
            max_bin = chromosome.length // resolution + 1
            exceed_boundaries_limit = max_bin - self.get_width()
            buffer = 50
            near_diag_distance = 1500 - self.get_width()
            temp = []
            if resolution >= 10000:
                for x1 in range(0, exceed_boundaries_limit, self.get_width() - buffer):
                    for y1 in range(x1, exceed_boundaries_limit, self.get_width() - buffer):
                        temp.append((chrom, x1, y1))
                        if x1 == y1:
                            num_total_slices += 1
                        else:
                            num_total_slices += 2
            else:
                for x1 in range(0, exceed_boundaries_limit, self.get_width() - buffer):
                    for y1 in range(x1, min(x1 + near_diag_distance, exceed_boundaries_limit),
                                    self.get_width() - buffer):
                        temp.append((chrom, x1, y1))
                        if x1 == y1:
                            num_total_slices += 1
                        else:
                            num_total_slices += 2
            temp.append((chrom, exceed_boundaries_limit, exceed_boundaries_limit))
            num_total_slices += 1
            self.populate_coordinates(temp)
            del temp
        print('Near Diagonal Values populated', flush=True)
        gc.collect()

        matrices = {}
        for chromosome in chrom_dot_sizes:
            chrom = chromosome.name
            if chrom.lower() == 'all':
                continue
            if len(chromosomes_to_use) > 0 and chrom.lower() not in chromosomes_to_use:
                continue
            print('Getting mzd for', chrom, resolution, flush=True)
            matrices[chrom] = hic_file_obj.getMatrixZoomData(chrom, chrom, "observed", norm, "BP", resolution)
        return matrices, num_total_slices

    def generate_bedpe_annotation(self):
        print('generate')
        skip_counter = 0
        while not (self.__prediction_done.is_set() and self.get_num_predictions() == 0):
            section = self.__prediction_list.get_all_and_clear()
            current_size = len(section)

            if current_size == 0:
                skip_counter += 1
                time.sleep(5)
                continue

            for k in range(current_size):
                self.write_prediction_to_nms_handler(section[k])

        print('Starting NMS', flush=True)
        for k in range(self.__num_output_channels + 1):
            self.__nms_handlers[k].do_nms_and_print_to_file(self.__out_files[k])

    def get_all_data_slices(self):
        print('slices')
        while self.get_num_coordinates() > 0:
            coordinates = self.__coords_list.get_amount_and_clear(1)[0]
            if coordinates is None:
                continue
            while self.get_num_data_points() > self.get_limit():
                time.sleep(2)
            matrix = self.get_data_from_coordinates(coordinates, self.__resolution)
            if matrix is None or not (type(matrix) is np.ndarray):
                continue
            self.__straw_data_list.append((self.__preprocess_input(matrix.copy()), coordinates))
            (chrom1, x1, y1) = coordinates
            if x1 != y1:
                self.__straw_data_list.append((self.__preprocess_input(matrix.T), (chrom1, y1, x1)))
            del matrix
            gc.collect()
        with self.__lock:
            self.__straw_worker_done_counter.append(1)
            if self.__straw_worker_done_counter.len() == self.__num_straw_workers:
                self.__production_done.set()
                print("DONE GETTING ALL REGIONS VIA STRAW!!!", flush=True)

    def write_prediction_to_nms_handler(self, section):
        prediction = section[0]
        prediction[prediction < self.get_threshold()] = 0
        chrom1 = section[1][0]
        x1 = int(section[1][1])
        y1 = int(section[1][2])
        for k in range(self.__num_output_channels + 1):
            if k == 2 and self.__num_output_channels == 3:
                find_bound_in_connected_components(prediction[:, :, k], chrom1, x1, y1,
                                                   self.__nms_handlers[k], self.__resolution)
            else:
                find_max_in_connected_components(prediction[:, :, k], chrom1, x1, y1,
                                                 self.__nms_handlers[k], self.__resolution,
                                                 ignore_on_diagonal=(k == 0))  # for loops

    def get_threshold(self):
        return self.__threshold

    def get_width(self):
        return self.__width

    def get_limit(self):
        return self.__limit

    def get_num_coordinates(self):
        return self.__coords_list.len()

    def get_num_data_points(self):
        return self.__straw_data_list.len()

    def get_num_predictions(self):
        return self.__prediction_list.len()

    def populate_coordinates(self, coords):
        self.__coords_list.extend(coords)

    def __predict_from_model_single_thread(self):
        while self.get_num_coordinates() > 0:
            coordinates = self.__coords_list.get_amount_and_clear(1)[0]
            if coordinates is None:
                continue
            matrix = self.get_data_from_coordinates(coordinates, self.__resolution)
            if matrix is None or not (type(matrix) is np.ndarray):
                continue

            section = (self.__preprocess_input(matrix.copy()), coordinates)
            (chrom1, x1, y1) = coordinates
            section_t = (self.__preprocess_input(matrix.T), (chrom1, y1, x1))

            raw_hic_input = np.zeros((2, self.get_width(), self.get_width(), 3))
            raw_hic_input[0, :, :, :] = section[0]
            raw_hic_input[1, :, :, :] = section_t[0]
            raw_hic_input = tf.constant(raw_hic_input)
            agg_matrix = AggregatedMatrix((2, self.get_width(), self.get_width(),
                                           self.__num_output_channels + 1), self.__use_arithmetic_mean)
            for p in range(len(self.__all_model_sets)):
                for model in self.__all_model_sets[p]:
                    agg_matrix.aggregate(model.predict(raw_hic_input), p)
            prediction = agg_matrix.get_final_result()

            self.write_prediction_to_nms_handler((prediction[0, :, :, :], section[1]))
            self.write_prediction_to_nms_handler((prediction[1, :, :, :], section_t[1]))

        print('Starting NMS', flush=True)
        for k in range(self.__num_output_channels + 1):
            self.__nms_handlers[k].do_nms_and_print_to_file(self.__out_files[k])
