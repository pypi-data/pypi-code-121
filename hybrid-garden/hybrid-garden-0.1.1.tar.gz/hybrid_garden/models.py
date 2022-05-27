def get_available_models():
    
    from sklearn.tree import DecisionTreeClassifier     
    from sklearn.tree import DecisionTreeRegressor 
   

    model_map = {
    # Classifiers
    'classification':{
    'DecisionTreeClassifier': DecisionTreeClassifier(),    
    },
    'regression':{
    # Regressors
    'DecisionTreeRegressor': DecisionTreeRegressor(),   
    }
    }    
    return model_map

def get_model_from_name(model_name, model_map, task='regression'):
    
    return model_map[task][model_name]

def get_models_for_task(model_map, task='regression'):
    
    return model_map[task]        
    
