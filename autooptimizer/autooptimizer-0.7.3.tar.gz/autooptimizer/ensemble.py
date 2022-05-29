from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier
from sklearn.model_selection import train_test_split, RandomizedSearchCV
import numpy as np
import warnings
warnings.simplefilter('ignore')

def randomforestclassifier(x, y, scoring='roc_auc_ovo'):
    xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.3, random_state=4, shuffle=True)
    parameters = {'n_estimators': np.arange(10,100,5),'max_depth':np.arange(1,10,1),
                 'criterion':['entropy','gini'], 'random_state':[1,3,4,11,14,20,43]}
    main_model = RandomForestClassifier()
    best_params = np.array([])
    best_score = np.array([])
    for cv in range(4, x.shape[1]+1):
        svc_model = RandomizedSearchCV(main_model, parameters, scoring=scoring, cv=cv)
        svc_model.fit(xtrain, ytrain)
        if svc_model.best_score_!=1.:
            best_params = np.append(best_params, svc_model.best_params_)
            best_score = np.append(best_score, svc_model.best_score_)
    best_index = np.argmax(best_score)
    print('The best accuracy in terms of {0} metric is {1}%'.format(scoring, round(best_score[best_index]*100,2)))
    hyperparameters = best_params[best_index]
    return RandomForestClassifier(n_estimators=hyperparameters['n_estimators'], max_depth=hyperparameters['max_depth'],
                                 criterion=hyperparameters['criterion'], random_state=hyperparameters['random_state'])

def gradientboostingclassifier(x, y, scoring='roc_auc_ovo'):
    xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.3, random_state=4, shuffle=True)
    parameters = {'loss':['deviance', 'exponential'], 'learning_rate':np.arange(0.1,2, 0.2), 
                  'n_estimators':np.arange(10,100,5),
                  'max_depth':np.arange(1,10,1), 'max_features':['auto','sqrt','log2'], 
                  'criterion':['friedman_mse','squared_error', 'mse','mae']}
    main_model = GradientBoostingClassifier()
    best_params = np.array([])
    best_score = np.array([])
    for cv in range(4, 11):
        svc_model = RandomizedSearchCV(main_model, parameters, scoring=scoring, cv=cv)
        svc_model.fit(xtrain, ytrain)
        if svc_model.best_score_ != 1.:
            best_params = np.append(best_params, svc_model.best_params_) 
            best_score = np.append(best_score, svc_model.best_score_)
    best_index = np.argmax(best_score)
    print('The best accuracy in terms of {0} metric is {1}%'.format(scoring, round(best_score[best_index]*100,2)))
    hyperparameters = best_params[best_index]
    return GradientBoostingClassifier(loss=hyperparameters['loss'], learning_rate=hyperparameters['learning_rate'],
                                n_estimators=hyperparameters['n_estimators'], max_depth=hyperparameters['max_depth'],
                                max_features=hyperparameters['max_features'], criterion=hyperparameters['criterion'])

def adaboostclassifier(x, y, scoring='roc_auc_ovo'):
    xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.3, random_state=4, shuffle=True)
    parameters = {'base_estimator':[None], 'n_estimators': np.arange(10,100,2), 'learning_rate': np.arange(0.1,2, 0.2),
                  'algorithm': ['SAMME'], 'random_state':[1,3,4,11,14,20,43],}
    main_model = AdaBoostClassifier()
    best_params = np.array([])
    best_score = np.array([])
    for cv in range(4,11):
        svc_model = RandomizedSearchCV(main_model, parameters, scoring=scoring)
        svc_model.fit(xtrain, ytrain)
        if svc_model.best_score_ != 1.:
            best_params = np.append(best_params, svc_model.best_params_)
            best_score = np.append(best_score, svc_model.best_score_)
    best_index = np.argmax(best_score)
    print('The best accuracy in terms of {0} metric is {1}%'.format(scoring, round(best_score[best_index]*100,2)))
    hyperparameters = best_params[best_index]
    return AdaBoostClassifier(base_estimator=hyperparameters['base_estimator'], n_estimators=hyperparameters['n_estimators'],
                              learning_rate=hyperparameters['learning_rate'], random_state=hyperparameters['random_state'])
