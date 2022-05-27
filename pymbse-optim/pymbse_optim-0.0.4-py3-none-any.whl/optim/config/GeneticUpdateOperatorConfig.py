from pydantic.dataclasses import dataclass


@dataclass
class OperatorConfig:
    type: str
    params: dict


@dataclass
class GeneticUpdateOperatorConfig:
    type: str
    params: dict
    mutation_operator: OperatorConfig
    selection_operator: OperatorConfig
    crossover_operator: OperatorConfig

    def __str__(self) -> str:
        return "type: %s\n" \
               "params: %s\n" \
               "mutation_operator: %s\n" \
               "selection_operator: %s\n" \
               "crossover_operator: %s\n" % (self.type,
                                             self.params,
                                             self.mutation_operator,
                                             self.selection_operator,
                                             self.crossover_operator)

    @staticmethod
    def initialize_config(config_dct: dict) -> "GeneticUpdateOperatorConfig":
        return GeneticUpdateOperatorConfig(**config_dct)
