from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import RandomizedSearchCV, train_test_split
import numpy as np

def decisiontreeclassifier(x, y, scoring='roc_auc_ovo'):
    xtrain,xtest,ytrain,ytest = train_test_split(x, y, test_size=0.3, random_state=4, shuffle=True)
    parameters = {'max_depth':range(1,10,1), 'random_state':range(1,50,1), 'max_features':['auto', 'sqrt', 'log2'],
                'splitter':['best', 'random'], 'criterion':['gini', 'entropy']}
    main_model = DecisionTreeClassifier()
    best_params = np.array([])
    best_score = np.array([])
    for cv in range(4, x.shape[1]+1):
        scv_model = RandomizedSearchCV(main_model,parameters, scoring=scoring, cv=cv)
        scv_model.fit(xtrain,ytrain)
        if scv_model.best_score_ != 1.:
            best_params=np.append(best_params,scv_model.best_params_)
            best_score=np.append(best_score,scv_model.best_score_)
    best_index = np.argmax(best_score)
    print('The best accuracy in terms of {0} metric is {1}%'.format(scoring, round(best_score[best_index]*100,2)))
    hyperparameter =  best_params[best_index]
    return DecisionTreeClassifier(max_depth=hyperparameter['max_depth'] , random_state=hyperparameter['random_state'], 
                                max_features=hyperparameter['max_features'], splitter=hyperparameter['splitter'],
                                criterion=hyperparameter['criterion'])
