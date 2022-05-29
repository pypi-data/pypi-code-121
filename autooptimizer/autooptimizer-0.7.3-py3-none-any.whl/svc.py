from sklearn.svm import SVC
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler
import numpy as np
import warnings
warnings.simplefilter("ignore")

def svc(x,y):
    xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.3, random_state=1
                                                   ,shuffle=True)
    ss=StandardScaler()
    xtrain=ss.fit_transform(xtrain)
    xtest=ss.fit_transform(xtest)
    parameters={'kernel':['rbf','sigmoid','poly','linear'],
                'C':[np.arange(1,10,1),100,1000,1e5],
                'degree':np.arange(0,11,1),
                'gamma':['scale','auto',0.1, 1, 10, 100]}
    main_model = SVC()
    scv_model = RandomizedSearchCV(main_model, parameters, cv=10)
    best_params = np.array([])
    best_score = np.array([])
    for i in range(x.ndim*2):
        scv_model.fit(xtrain, ytrain)
        best_params = np.append(best_params, scv_model.best_params_)
        best_score = np.append(best_score, scv_model.best_score_)

    best_index = np.argmax(best_score)
    print('The best accuracy depends on you dataset is {}%'
          .format(round(best_score[best_index]*100,2)))
    print('The parameters are: ')
    print(best_params[best_index])
