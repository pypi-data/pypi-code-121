import hashlib
import json
from copy import deepcopy
from typing import List

from pymbse.optim.design_variable.GeneticDesignVariable import GeneticDesignVariable, GeneticLayerDesignVariable, \
    GeneticBlockDesignVariable, GeneticMultiBlockDesignVariable


class Individual:
    def __init__(self, gen_dvs: List[GeneticDesignVariable]):
        self.gen_dvs = deepcopy(gen_dvs)
        self.score = None
        self.fom = {}

    def generate_random_genes(self) -> None:
        for dv in self.gen_dvs:
            dv.generate_random_gene()

    def is_fom_correct(self):
        return self.fom and all([value is not None for value in self.fom.values()])

    def get_global_dvs(self) -> List[GeneticDesignVariable]:
        return [gen_dv for gen_dv in self.gen_dvs if isinstance(gen_dv, GeneticDesignVariable)]

    def get_layer_dvs(self) -> List[GeneticLayerDesignVariable]:
        return [gen_dv for gen_dv in self.gen_dvs if isinstance(gen_dv, GeneticLayerDesignVariable)]

    def get_block_dvs(self) -> List[GeneticBlockDesignVariable]:
        return [gen_dv for gen_dv in self.gen_dvs if isinstance(gen_dv, GeneticBlockDesignVariable)]

    def get_multiblock_dvs(self) -> List[GeneticMultiBlockDesignVariable]:
        return [gen_dv for gen_dv in self.gen_dvs if isinstance(gen_dv, GeneticMultiBlockDesignVariable)]

    def assemble_chromosome(self) -> List[int]:
        chromosome = []
        for gen_dv in self.gen_dvs:
            chromosome.extend(gen_dv.gene)

        return chromosome

    def sequence_chromosome(self, chromosome: List[int]) -> None:
        index_start = 0
        for gen_dv in self.gen_dvs:
            index_end = index_start + gen_dv.bits
            gen_dv.gene = chromosome[index_start: index_end]
            index_start = index_end

    def __str__(self):
        if self.score is None:
            return f"Individual, score: NaN, chromosome: {self.assemble_chromosome()}"
        else:
            return f"Individual, score: {self.score:.2f}, chromosome: {self.assemble_chromosome()}"

    def dict(self):
        return {"gen_dvs": [gen_dv.__dict__ for gen_dv in self.gen_dvs]}

    def __hash__(self):
        return hashlib.md5(json.dumps(self.dict(), sort_keys=True).encode('utf-8')).hexdigest()