from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from mlxtend.plotting import plot_decision_regions
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.simplefilter('ignore')

def logreg(x, y):
    xtrain, xtest, ytrain, ytest = train_test_split(x, y, test_size=0.3, random_state=4
                                                   ,shuffle=True)
    parameters={'penalty':['l1','l2','elasticnet', 'none'],
                'C':[np.arange(0.1,10,0.1),1,10,100,1000],
                'random_state':range(1,50),
                'solver':['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
                'max_iter':[1,10,100]}

    main_model = LogisticRegression()
    scv_model = RandomizedSearchCV(main_model, parameters, cv=10)
    best_params = np.array([])
    best_score = np.array([])
    for i in range(x.ndim*3):
        scv_model.fit(xtrain, ytrain)
        best_params = np.append(best_params, scv_model.best_params_)
        best_score = np.append(best_score, scv_model.best_score_)

    best_index = np.argmax(best_score)
    print('The best accuracy depends on you dataset is {}%'
          .format(round(best_score[best_index]*100, 2)))
    print('The parameters are: ')
    print(best_params[best_index])
    
    def plotting(xtrain,ytrain):
        plt.title('LogisticRgression Decision Region Boundary')
        plot_decision_regions(xtrain, ytrain, clf=scv_model, zoom_factor=2)
        plt.show()
    plotting(xtrain, ytrain)
