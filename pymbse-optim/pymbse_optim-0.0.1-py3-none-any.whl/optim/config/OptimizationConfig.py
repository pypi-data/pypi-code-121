from pydantic.dataclasses import dataclass

import pymbse.commons.json_file as json_file
from pymbse.optim.config.GeneticUpdateOperatorConfig import GeneticUpdateOperatorConfig


@dataclass
class OptimizationConfig:
    """Class for optimization config used for the genetic algorithm.

    Attributes:
       output_folder (float): The path to an output folder
       logger_rel_path (float): The path to the logger csv file
       n_pop (int): The number of individuals, i.e., the population size
       n_gen (int): The number of generations
       r_cross (float): The probability of crossover
       r_mut (float): The probability of mutation
       objectives (list): The list of objective configs
       notebooks (list): The list of notebook configs
       model_creation_type (str): type of model creation: default, programmable, targeted
    """
    n_gen: int
    n_pop: int
    design_variables_rel_path: str
    update_operator_config: GeneticUpdateOperatorConfig

    def __str__(self) -> str:
        return "n_pop: %d\n" \
               "n_gen: %d\n" \
               "design_variables_rel_path: %s\n" \
               "\nupdate_operator_config: \n\n%s" % (
                                                     self.n_pop,
                                                     self.n_gen,
                                                     self.design_variables_rel_path,
                                                     self.update_operator_config)

    @staticmethod
    def initialize_config(json_path: str) -> "OptimizationConfig":
        """ Static method initializing an optimization config from a json file

        :param json_path: a path to a json file with config
        :return: initialized OptimizationConfig instance
        """
        data = json_file.read(json_path)
        return OptimizationConfig(**data)
