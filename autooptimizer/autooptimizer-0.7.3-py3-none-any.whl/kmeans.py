from sklearn.cluster import KMeans
from sklearn import metrics
import numpy as np
import matplotlib.pyplot as plt

def kmeans(x):
    calinski_harabasz_score = np.array([])
    for i in range(2,20):
        model = KMeans(n_clusters=i).fit(x)
        label = model.labels_
        calinski_harabasz_score = np.append(calinski_harabasz_score
                                            ,metrics.calinski_harabasz_score(x, label))
    best_score = np.argmax(calinski_harabasz_score)
    best_proba = calinski_harabasz_score[best_score]
    plt.style.use("fivethirtyeight")
    plt.figure(dpi=80, figsize=(9,5))
    plt.title('Model evaluation result')
    plt.grid()
    plt.margins(0.05)
    plt.xlabel('Number of clusters', fontsize=12, color='red')
    plt.ylabel('Score of evaluation', fontsize=12, color='red')
    plt.xticks(range(2, 20))
    plt.yticks()
    plt.annotate('Optimal clustering', xytext=(best_score+2, best_proba)
                 ,xy=(best_score+2, best_proba), fontsize=9, arrowprops={'color':'violet'})
    plt.plot(range(2,20),calinski_harabasz_score,ls='--',marker='x',lw=2,label='calinski score')
    plt.grid()
    plt.legend(loc='best')
    plt.show()
