from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV,train_test_split
import numpy as np
import warnings
warnings.simplefilter('ignore')

def logisticregression(x, y, scoring='roc_auc_ovo'):
    xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.3, random_state=4, shuffle=True)
    l0_parameters = {'penalty':['l1','l2','elasticnet', 'none'],
                'C':[np.arange(0.1,10,0.1),1,10,100,1000],
                'random_state':range(1,50),
                'solver':['saga'],
                'max_iter':[1,10,100]}
    l1_parameters = {'penalty':['l1','l2'],
                'C':[np.arange(0.1,10,0.1),1,10,100,1000],
                'random_state':range(1,50),
                'solver':['liblinear'],
                'max_iter':[1,10,100]}
    l2_parameters = {'penalty':['l2', 'none'],
                'C':[np.arange(0.1,1,0.1),1,10,100,1000],
                'random_state':range(1,50),
                'solver':['newton-cg', 'lbfgs', 'sag',],
                'max_iter':[1,10,100]}
    main_model = LogisticRegression()
    scv_model1 = RandomizedSearchCV(main_model, l0_parameters, scoring=scoring, cv=4)
    scv_model2 = RandomizedSearchCV(main_model, l1_parameters, scoring=scoring, cv=8)
    scv_model3 = RandomizedSearchCV(main_model, l2_parameters, scoring=scoring, cv=10)
    models = [scv_model1, scv_model2, scv_model3, scv_model1, scv_model2, scv_model3]
    best_params = np.array([])
    best_score = np.array([])
    for i in range(6):
        models[i].fit(xtrain, ytrain)
        if models[i].best_score_ !=1.:
            best_params = np.append(best_params, models[i].best_params_)
            best_score = np.append(best_score, models[i].best_score_)
    best_index = np.argmax(best_score)
    print('The best accuracy depends on you dataset is {}%'.format(round(best_score[best_index]*100, 2)))
    hyperparameter =  best_params[best_index]
    return LogisticRegression(solver=hyperparameter['solver'] , random_state=hyperparameter['random_state'], 
                                penalty=hyperparameter['penalty'], max_iter=hyperparameter['max_iter'],
                                C=hyperparameter['C'])
