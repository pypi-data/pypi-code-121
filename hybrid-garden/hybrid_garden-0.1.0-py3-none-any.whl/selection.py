import pandas as pd
import numpy as np
import os
import pickle
from pathlib import Path

import config as cfg


MODELS_DIR = cfg.MODELS_DIR
METADATA_DIR = cfg.METADATA_DIR
REPORTS_DIR = cfg.REPORTS_DIR

def _create_plane_meta(nested_meta):
    plane_meta = {}
    for k, v in nested_meta.items():
        if k != 'scores':
            plane_meta[k] = v
        else:
            for item in nested_meta['scores']:
                plane_meta[item] = np.mean(nested_meta['scores'][item])
    return plane_meta

def get_trees(current_run_id, n_trees, fitness_thresh):
    
    global MODELS_DIR
    global METADATA_DIR
    global REPORTS_DIR
    
    if current_run_id not in MODELS_DIR:
        MODELS_DIR = os.path.join(MODELS_DIR, '{current_run_id}'.format(current_run_id=current_run_id))
        if not os.path.isdir(MODELS_DIR):     
            Path(MODELS_DIR).mkdir(parents=True, exist_ok=True)
        REPORTS_DIR = os.path.join(REPORTS_DIR, '{current_run_id}'.format(current_run_id=current_run_id))
        if not os.path.isdir(REPORTS_DIR):     
            Path(REPORTS_DIR).mkdir(parents=True, exist_ok=True)
        METADATA_DIR = os.path.join(METADATA_DIR, '{current_run_id}'.format(current_run_id=current_run_id))
        if not os.path.isdir(METADATA_DIR):     
            Path(METADATA_DIR).mkdir(parents=True, exist_ok=True)

    
    meta_files = [name for name in os.listdir(METADATA_DIR) if os.path.isfile(os.path.join(METADATA_DIR, name))]
    
    all_metas = []
    for filename in meta_files:
        with open(os.path.join(METADATA_DIR, filename), 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            meta = pickle.load(f)
            all_metas.append(meta)

    solutions = [(tuple(meta['solution']), meta['fitness'], meta['model_id'])  for meta in all_metas if meta['fitness'] > fitness_thresh]
    solutions_df = pd.DataFrame(solutions, columns=['solution', 'fitness','model_id'])
    solutions_df = solutions_df.sort_values('fitness', ascending=False).drop_duplicates('solution').sort_index()
    selected_models = solutions_df.model_id.to_list()
    del solutions_df

    unique_meta = [_create_plane_meta(meta) for meta in all_metas if meta['model_id'] in selected_models]
    unique_meta_df = pd.DataFrame(unique_meta)
    
    precision_mask = unique_meta_df.columns[unique_meta_df.columns.str.startswith('test_precision')].values[0]
    recall_mask = unique_meta_df.columns[unique_meta_df.columns.str.startswith('test_recall')].values[0]
    
    best_fitness_list = unique_meta_df.sort_values(['fitness', precision_mask], ascending=False)[:n_trees].model_id.to_list()
    best_precisions_list = unique_meta_df.sort_values([precision_mask, 'fitness'], ascending=False)[:n_trees].model_id.to_list()
    best_recalls_list = unique_meta_df.sort_values([recall_mask, 'fitness'], ascending=False)[:n_trees].model_id.to_list()
    
    best_unique = set(best_fitness_list + best_precisions_list + best_recalls_list)
    unique_meta_df = unique_meta_df.loc[unique_meta_df.model_id.isin(best_unique)]
    unique_meta_df.to_csv(os.path.join(REPORTS_DIR, 'best_models_{current_run_id}.csv'.format(current_run_id=current_run_id)))

    selected_metas = [meta for meta in all_metas if meta['model_id'] in best_unique]
    del all_metas
    
    best_models = []
    for item in selected_metas:    
        with open(item['file_path'], 'rb') as f:
            # The protocol version used is detected automatically, so we do not
            # have to specify it.
            model = pickle.load(f)
            best_models.append(model)

    return (best_models, selected_metas)

def get_best_tree(trees, best_solution, solution_idx):

    
    for tree, meta in trees:
        if (meta['solution'] == best_solution).all() and (meta['solution_idx'] == solution_idx).all():
            best_tree = tree
            best_meta = meta    
            return (best_tree, best_meta)

