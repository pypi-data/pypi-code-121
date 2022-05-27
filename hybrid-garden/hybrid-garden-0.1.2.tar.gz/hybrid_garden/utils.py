import os
import pickle
from pathlib import Path

import uuid
from . import config as cfg



MODELS_DIR = cfg.MODELS_DIR
METADATA_DIR = cfg.METADATA_DIR

def save_model(clf, model_name, solution, solution_idx, fitness, scores, selected_features, gen_idx, current_run_id):
    
    global MODELS_DIR
    global METADATA_DIR
    
    model_id = uuid.uuid4().hex
    
    if current_run_id not in MODELS_DIR:
        MODELS_DIR = os.path.join(MODELS_DIR, '{current_run_id}'.format(current_run_id=current_run_id))
        if not os.path.isdir(MODELS_DIR):     
            Path(MODELS_DIR).mkdir(parents=True, exist_ok=True)
        
        METADATA_DIR = os.path.join(METADATA_DIR, '{current_run_id}'.format(current_run_id=current_run_id))
        if not os.path.isdir(METADATA_DIR):     
            Path(METADATA_DIR).mkdir(parents=True, exist_ok=True)
    file_name = '{model_name}_{fitness:.2f}_{model_id}.pickle'.format(                                                
                                                model_name=model_name,
                                                fitness=fitness,
                                                model_id=model_id)
    
    FILE_PATH = os.path.join(MODELS_DIR, file_name)
    META_PATH = os.path.join(METADATA_DIR, file_name)
    model_meta = {}
    model_meta = {'current_run_id': current_run_id,
                'model_id': model_id,
                'model_name': model_name,
                'file_path':  FILE_PATH,
                'solution': solution,
                'solution_idx': solution_idx,
                'fitness': fitness,                
                'scores': scores,
                'selected_features': selected_features,
                'gen_idx': gen_idx}
    with open(FILE_PATH, 'wb') as handle:
        pickle.dump(clf, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open(META_PATH, 'wb') as handle:
        pickle.dump(model_meta, handle, protocol=pickle.HIGHEST_PROTOCOL)
