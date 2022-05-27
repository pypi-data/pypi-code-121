import numpy as np

def get_model_params(model_name, task='regression'):
    model_params = {
        'regression':{
        'DecisionTreeRegressor':{
            'criterion': ['gini', 'entropy', 'log_loss'],
                'max_features':[0.3, 0.4, 0.5, 'log2', 'sqrt', None],
                'max_depth': [4, 5, 6, 7, 8, 9, 10, 11],
                'min_impurity_decrease': [0, 0.001, 0.01, 0.1, 0.2]
                },   
        },   
     
         'classification':{             
              'DecisionTreeClassifier':{
                'criterion': ['gini', 'entropy'],
                'max_features':[0.3, 0.4, 0.5, 'log2', 'sqrt', None],
                'max_depth': [4, 5, 6, 7, 8, 9, 10, 11],
                'min_impurity_decrease': [0, 0.001, 0.01, 0.1, 0.2]
                },        
            }
    }

    return model_params[task][model_name]

def create_model_gene_space(model_params_dict):

    model_params_list = []
    model_gene_space = []
    for k, v in model_params_dict.items():
        model_params_list.append(k)
        model_gene_space.append(list(range(len(v))))

    return model_params_list, model_gene_space
        
def create_feature_gene_space(X):
    return [list(np.arange(X.shape[1])) for _ in  range(X.shape[1])]

def prepare_params(model_name, model, X, task='regression'):

    model_params = []
    model_params = get_model_params(model_name, task)
    # print(model_params)
    if model_params:
        model_params_lst, gene_space = create_model_gene_space(model_params)
        f_gene_space = create_feature_gene_space(X)
        gene_space.extend(f_gene_space)
    else:
        return None
    return  model, model_params, model_params_lst, gene_space