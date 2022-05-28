import numpy as np
import copy
import random


class MutationOperators(object):
    """
    Обычное скрещивание
    """
    @staticmethod
    def __random_mutation(individuals, probability):
        mutated_individuals = copy.deepcopy(individuals)

        for individual in mutated_individuals:
            psf_size = individual.psf_size
            for row in range(0, psf_size, 1):
                for col in range(0, psf_size, 1):
                    if random.random() < probability:
                        individual.psf[col, row] += random.uniform(-5.0, 5.0)
                        if individual.psf[col, row] < 0.0:
                            individual.psf[col, row] = 0.0
                        elif individual.psf[col, row] > 1.0:
                            individual.psf[col, row] = 1.0
            individual.normalize()

        return mutated_individuals

    @staticmethod
    def __smart_mutation(individuals, probability, pos_probability):
        """
        Умная мутация особи
        :param individuals - мутируемые особи
        :param probability: вероятность мутирования
        :param pos_prob: вероятность добавления рандомного значения к гену, если меньше, то вычитание
        """
        mutated_individuals = copy.deepcopy(individuals)
        for individual in mutated_individuals:
            bright_pixels = np.argwhere(individual.psf > 0.1)
            for position in bright_pixels:
                if random.random() < probability:
                    random_neighbor_position = individual.get_random_neighbor_position(position[0], position[1])

                    if random.random() < pos_probability:
                        try:
                            individual.psf[random_neighbor_position[0], random_neighbor_position[1]] += random.uniform(0.1,
                                                                                                                   1.0)
                            if individual.psf[random_neighbor_position[0], random_neighbor_position[1]] > 1.0:
                                individual.psf[random_neighbor_position[0], random_neighbor_position[1]] = 1.0
                        except IndexError:
                            individual.psf[position[0], position[1]] += random.uniform(0.1, 1.0)
                            if individual.psf[position[0], position[1]] > 1.0:
                                individual.psf[position[0], position[1]] = 1.0
                    else:
                        individual.psf[position[0], position[1]] -= random.uniform(0.1, 1.0)
                        if individual.psf[position[0], position[1]] < 0:
                            individual.psf[position[0], position[1]] = 0
                    break
            individual.normalize()

        return mutated_individuals

    @staticmethod
    def mutate(individuals, mutation_args):
        try:
            type = mutation_args["type"]
            probability = mutation_args["probability"]
            if not isinstance(type, str) and not isinstance(probability, float):
                raise AttributeError("Mutation type should be string and prob should be float")
        except KeyError:
            raise AttributeError("Define mutation type and probability")

        if type == "smart":
            try:
                pos_probability = mutation_args["positive_mutation_probability"]
                if not isinstance(pos_probability, float):
                    raise AttributeError("positive_mutation_probability type should be string and prob should be float")
            except KeyError:
                raise AttributeError("Define pos_probability for smart_mutation")
            return MutationOperators.__smart_mutation(individuals, probability, pos_probability=pos_probability)
        elif type == "random":
            return MutationOperators.__random_mutation(individuals, probability)
