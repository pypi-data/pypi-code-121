#!/usr/bin/env python
# Created by "Thieu" at 11:14, 01/03/2022 ----------%                                                                               
#       Email: nguyenthieu2102@gmail.com            %                                                    
#       Github: https://github.com/thieu1995        %                         
# --------------------------------------------------%

from opfunu.cec_basic.cec2014_nobias import *
from mealpy.evolutionary_based import GA
from mealpy.human_based import BRO
from mealpy.math_based import GBO
from mealpy.math_based import CGO
from mealpy.utils.problem import Problem
import numpy as np

def fitness(solution):
    return np.sum(solution**2)

problem_dict1 = {
    "fit_func": fitness,
    "lb": [-3, -5, -10, -10, ],
    "ub": [5, 10, 100, 30, ],
    "minmax": "min",
    "verbose": True,
}

term_dict = {
    "mode": "FE",
    "quantity": 4000  # 100000 number of function evaluation
}

### Your parameter problem can be an instane of Problem class or just dict like above
model6 = GA.BaseGA(problem_dict1, epoch=1000, pop_size=50, pc=0.9, pm=0.05, crossover="arithmetic",
                   selection="tournament", k_way=0.3, mutation_multipoints=True, mutation="flip")
model6.solve()
