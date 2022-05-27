import warnings
from copy import deepcopy

from pymbse.optim.cache_database_api import get_max_optimization_ix
from pymbse.optim.config.OptimizationConfig import OptimizationConfig
from pymbse.optim.design_variable.DesignVariableFactory import init_genetic_design_variables_with_csv
from pymbse.optim.design_variable.Individual import Individual
from pymbse.optim.genetic.update_operators import UpdateOperatorFactory


class GeneticOptimizationBuilder:

    @classmethod
    def build(cls, config: OptimizationConfig, ip_with_port_cache: str = ''):
        update_operator = UpdateOperatorFactory.build(config.update_operator_config)
        design_variables = init_genetic_design_variables_with_csv(config.design_variables_rel_path)
        return GeneticOptimization(n_pop=config.n_pop,
                                   n_gen=config.n_gen,
                                   update_operator=update_operator,
                                   design_variables=design_variables,
                                   ip_with_port_cache=ip_with_port_cache)


class GeneticOptimization:
    """ A GeneticOptimization class implementing a basic genetic optimization algorithm.

    """
    ip_with_port_cache = ""
    optimization_ix = None

    def __init__(self,
                 n_pop,
                 n_gen,
                 update_operator,
                 design_variables,
                 ip_with_port_cache='') -> None:
        """ Constructor of a RoxieGeneticOptimization instance

        """
        self.individuals = []

        self.n_pop = n_pop
        self.n_gen = n_gen

        self.update_operator = update_operator
        self.design_variables = design_variables

        if ip_with_port_cache != '':
            GeneticOptimization.ip_with_port_cache = ip_with_port_cache
            self.optimization_ix = get_max_optimization_ix(ip_with_port_cache) + 1
            print('The optimization index is: %d.' % self.optimization_ix)

    def optimize(self) -> None:
        """ Method executing the main optimization loop of the genetic algorithm

        """
        # enumerate generations
        for gen in range(self.n_gen):
            print('Generation:', gen)
            self.initialize_or_execute(gen)
            self.display_scores()
            self.individuals = self.update_operator.update_generation(self.individuals)

    def initialize_or_execute(self, gen):
        if gen == 0:
            while len(self.individuals) < self.n_pop:
                individual = Individual(self.design_variables)
                individual = self.generate_random_individual(individual)
                individual = self.execute_model(individual, self.optimization_ix, gen, len(self.individuals))

                if individual.is_fom_correct():
                    self.individuals.append(individual)
        else:
            self.individuals = [self.execute_model(individual, self.optimization_ix, gen, individual_index)
                                for individual_index, individual in enumerate(self.individuals)]

    @staticmethod
    def generate_random_individual(individual: Individual) -> Individual:
        individual_copy = deepcopy(individual)
        individual_copy.generate_random_genes()
        return individual_copy

    @classmethod
    def execute_model(cls,
                      individual: Individual,
                      optimization_ix: int,
                      generation_ix: int,
                      individual_ix: int
                      ) -> Individual:
        individual_out = deepcopy(individual)
        try:
            artefacts = GeneticOptimization.execute_value_model_with_pymbse(individual,
                                                                            optimization_ix,
                                                                            generation_ix,
                                                                            individual_ix)
            individual_out.score = artefacts['value']
            individual_out.fom = {key:artefacts[key] for key in artefacts if key != 'value'}
        except Exception as exc:
            print('Error while executing an individual.')
            warnings.warn(exc)
            individual_out.score = None
            individual_out.artefacts = {'value': None}

        print(generation_ix, individual_ix, individual_out.fom, individual_out.score)

        return individual_out

    @staticmethod
    def execute_value_model_with_pymbse(individual, optimization_ix, generation_ix, individual_ix) -> dict:
        value = sum([gen_dv.value ** 2 for gen_dv in individual.gen_dvs])
        return {'value': value}

    def display_scores(self):
        individuals_sorted = sorted(self.individuals, key=lambda individual: individual.score)
        scores = [individual.score for individual in individuals_sorted]
        print(scores)
