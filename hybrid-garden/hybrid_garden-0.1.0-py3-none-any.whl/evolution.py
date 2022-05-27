import numpy as np
import pandas as pd
import sklearn
import pygad

import multiprocessing

import time
import uuid
import pickle
import os

import randomname
from sklearn.model_selection import cross_validate
from pprint import pprint
from datetime import date
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from initialization import initialization
from utils import save_model
from params import prepare_params
import config as cfg

WORK_DIR = cfg.WORK_DIR
MODELS_DIR = cfg.MODELS_DIR
METADATA_DIR = cfg.METADATA_DIR


model_params_lst = {}
model_params ={}




def evolution(X, y, models=None, task=None, num_generations=3):
    
    

    def fitness_func(solution, solution_idx):

        # global model, task, model_params, model_params_lst, X
        # print(model_params_lst)
        # print(model_params[task])
        params = dict()
        if solution_idx:
            rand_state = solution_idx + 4576
        else:
            rand_state = 4576 
        params['random_state'] = rand_state

        for i, param in enumerate(model_params_lst):
            # print(model_params[param][solution[i]])
            params[param] = model_params[param][solution[i]] 

        gen_idx = len(model_params_lst)-1
        selected_features = list(set(solution[gen_idx:]))
        

        clf = model.set_params(**params)
        # fitness = np.mean(cross_validate(clf, X[:,selected_features], y, cv=5))
        scores = cross_validate(clf, X[:,selected_features], y, scoring=scoring, 
                                cv=5, return_train_score=True)
        fitness = np.mean(scores['test_' + fitness_metric])
        # fitness = 1.0 / (np.abs(output - 1) + 0.000001)
        save_model(clf, model_name, solution, solution_idx, fitness, scores, selected_features, gen_idx, current_run_id)
        return fitness

    solution_fitness_gen = []
    solution_idx_gen = []
    solution_gen = []
    def on_generation(ga_instance):
        print("Generation : ", ga_instance.generations_completed)
        solution, solution_fitness, solution_idx = ga_instance.best_solution()
        # solution_gen.append(solution)
        # solution_idx_gen.append(solution_idx)
        # solution_fitness_gen.append(solution_fitness)    
        print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))  
    # global pool
    # global model_params_lst
    # global model_params
    # global gene_space
    # global model
    
    
    if not models:
        models = ['DecisionTreeClassifier']
    task, model_name, model, scoring, fitness_metric = initialization(X, y, models)
    model, model_params, model_params_lst, gene_space = prepare_params(model_name,
                                                                        model, X, 
                                                                        task)
    # print(model_params, model_params_lst) 
                                                
    num_genes = len(gene_space)
    num_mutations_high = int(num_genes / 2)
    num_mutations_low = int(num_mutations_high / 3)
    gene_type = np.int8
    start_time = time.time()

    current_run_id = ('{random_name}-{start_time}'
                .format(start_time=date.fromtimestamp(start_time).strftime('%d-%m-%y'),                                            
                                                random_name = randomname.get_name()))
        
    Path(os.path.join(MODELS_DIR,'{current_run_id}'.format(current_run_id=current_run_id))).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(METADATA_DIR,'{current_run_id}'.format(current_run_id=current_run_id))).mkdir(parents=True, exist_ok=True)   
    print('Current experiment:', current_run_id)                                            
    ga_instance = pygad.GA(num_generations=num_generations,
                        fitness_func=fitness_func,
                        num_parents_mating=40,
                        parent_selection_type="tournament",
                        K_tournament=10,
                        sol_per_pop=60,                        
                        keep_parents = 1,
                        num_genes=num_genes,
                        gene_space=gene_space,
                        gene_type=gene_type,
                        mutation_type="adaptive",
                        mutation_num_genes=(num_mutations_high, num_mutations_low),
                        on_generation=on_generation, 
                        save_solutions=False,
                        save_best_solutions=False,
                        stop_criteria=["saturate_20"])
    
   
        
    ga_instance.run()

    solution, solution_fitness, solution_idx = ga_instance.best_solution()

    print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))
    print("Index of the best solution : {solution_idx}".format(solution_idx=solution_idx))

    print("--- %s seconds ---" % (time.time() - start_time))


    # After the generations complete, some plots are showed that summarize how the outputs/fitness values evolve over generations.
    ga_instance.plot_result(title="Iteration vs. Fitness", linewidth=4)

    print("Number of generations passed is {generations_completed}".format(generations_completed=ga_instance.generations_completed))
    # #  Saving the GA instance.
    # filename = os.path.join(WORK_DIR,'{current_run_id}'.format(current_run_id=current_run_id)) # The filename to which the instance is saved. The name is without extension.
    # ga_instance.save(filename=filename)
    return current_run_id, solution, solution_fitness, solution_idx

# Loading the saved GA instance.
# loaded_ga_instance = pygad.load(filename=filename)
# loaded_ga_instance.plot_fitness()

# if '__name__' == '__main__':
#     evolution(X, y, models=None)
