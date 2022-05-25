from dataclasses import dataclass
from typing import List

from pymbse.optim.config.GeneticUpdateOperatorConfig import GeneticUpdateOperatorConfig
from pymbse.optim.design_variable.Individual import Individual
from pymbse.optim.genetic.crossover_operators import CrossOverOperator, CrossOverOperatorFactory
from pymbse.optim.genetic.mutation_operators import MutationOperator, MutationOperatorFactory
from pymbse.optim.genetic.selection_operators import SelectionOperator, SelectionOperatorFactory


@dataclass
class UpdateOperator:
    selection_operator: SelectionOperator
    mutation_operator: MutationOperator
    crossover_operator: CrossOverOperator

    def update_generation(self, individuals: List[Individual]) -> List[Individual]:
        """ Method updating generation of individuals representing candidate solutions. The update consists of applying
        the following genetic operators:
        - application of elitism (if n_elite > 0), i.e., direct propagation of best n_elite individuals to the next
        iteration of the algorithm
        - tournament selection (with given tournament size, k_selection) of parents for mating
        - crossover of pairs of parents to produce a pair of children; crossover happens with a certain probability
        - mutation with a given probability

        :param individuals: list of individuals with candidate solutions. Each candidate is represented as a bitstring
        :return: a new generation of individuals after applying genetic operators to the input generation
        """
        assert len(individuals) % 2 == 0, 'The size of the population has to be an odd number'

        # select parents
        n_pop = len(individuals)
        selected = [self.selection_operator.select(individuals) for _ in range(n_pop)]
        # create the next generation
        children: List[Individual] = self.crossover_and_mutation(selected)
        # return updated population
        return children

    def crossover_and_mutation(self, selected: List[Individual]) -> List[Individual]:
        children: List[Individual] = []
        for i in range(0, len(selected), 2):
            # get selected parents in pairs
            p1, p2 = selected[i], selected[i + 1]
            # crossover and mutation
            for child in self.crossover_operator.crossover(p1, p2):
                # mutation
                child = self.mutation_operator.mutate(child)
                # store for next generation
                children.append(child)
        return children


@dataclass
class ElitismUpdateOperator(UpdateOperator):
    n_elite: int

    def update_generation(self, individuals: List[Individual]) -> List[Individual]:
        """ Method updating generation of individuals representing candidate solutions. The update consists of applying
        the following genetic operators:
        - application of elitism (if n_elite > 0), i.e., direct propagation of best n_elite individuals to the next
        iteration of the algorithm
        - tournament selection (with given tournament size, k_selection) of parents for mating
        - crossover of pairs of parents to produce a pair of children; crossover happens with a certain probability
        - mutation with a given probability

        :param individuals: list of individuals with candidate solutions. Each candidate is represented as a bitstring
        :return: a new generation of individuals after applying genetic operators to the input generation
        """
        assert len(individuals) % 2 == 0, 'The size of the population has to be an odd number'

        # select parents
        n_pop = len(individuals)
        individuals_sorted = sorted(individuals, key=lambda individual: individual.score)
        individuals_elite = individuals_sorted[:self.n_elite]
        # all individuals are taken for selection so that the best ones participate too
        selected = [self.selection_operator.select(individuals) for _ in range(n_pop - self.n_elite)]
        # create the next generation
        children = self.crossover_and_mutation(selected)
        # return updated population
        return individuals_elite + children


type_to_update_factory_class = {"default": UpdateOperator,
                                "elitism": ElitismUpdateOperator}


class UpdateOperatorFactory:
    @staticmethod
    def build(config: GeneticUpdateOperatorConfig):
        selection_operator = SelectionOperatorFactory.build(config.selection_operator)
        mutation_operator = MutationOperatorFactory.build(config.mutation_operator)
        crossover_operator = CrossOverOperatorFactory.build(config.crossover_operator)
        UpdateOperatorClass = type_to_update_factory_class[config.type]
        return UpdateOperatorClass(selection_operator=selection_operator,
                                   mutation_operator=mutation_operator,
                                   crossover_operator=crossover_operator,
                                   **config.params)
