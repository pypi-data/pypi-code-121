from sklearn.model_selection import cross_validate
from pprint import pprint
import numpy as np

from models import get_available_models
from models import get_models_for_task
from metrics import get_model_scoring_metrics

def initialization(X, y, models=None, fitness_metric=None, template=None):
    
    if isinstance(y[1], float):
        task = 'regression'
    else:
        task = 'classification'
    binary = False
    if task == 'classification' and len(set(y)) == 2:
        binary = True

    model_map = get_available_models()   
        
    models_dict = get_models_for_task(model_map, task=task)
    if not template:
        template='minimum'
    scoring_metrics = get_model_scoring_metrics(task=task, binary= binary, template=template)
    print(scoring_metrics)

    if not fitness_metric:
        if task == 'regression':
            fitness_metric = 'neg_root_mean_squared_error'
        elif binary:
            fitness_metric = 'roc_auc'
        else:
            fitness_metric = 'roc_auc_ovo'


    if not models:
        models = models_dict.keys()

    initial_scores = {}
    for model in models:
        clf = models_dict[model]
        scores = cross_validate(clf, X, y, scoring=scoring_metrics, cv=5, return_train_score=True)
        initial_scores[model] = scores['test_' + fitness_metric]
        pprint('Fitness metric: {fitness_metric}'.format(fitness_metric=fitness_metric))
        pprint('Start fitness score for {model}: {score}'.format(model=model, score=initial_scores[model]))
        pprint('Initial scores:{scores}'.format(scores=scores))
    if task == 'regression':
        best_score_model = min(initial_scores, key= lambda x: np.mean(initial_scores[x]))
    else: 
        best_score_model = max(initial_scores, key= lambda x: np.mean(initial_scores[x]))
    print('Task: {task}'.format(task=task))
    print('For evolution selected model {best_score_model} with score {score}'
                    .format(best_score_model=best_score_model,
                    score=initial_scores[best_score_model]))
    


    return task, best_score_model, models_dict[best_score_model], scoring_metrics, fitness_metric        