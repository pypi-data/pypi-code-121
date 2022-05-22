import numpy as np
from sklearn.decomposition import PCA


class projector(object):
    def __init__(self, pca, mu, n_components=2):
        self.pca = pca
        self.mu = mu
        self.n_components = n_components

    def transform(self,X):
        return self.pca.transform(X)

    def inverse_transform(self,X):
        Xhat=np.dot(X,self.pca.components_)
        return Xhat+self.mu






def learn_projection(X, n_components=2):
    """
    Learn a projection matrix that projects the data in X onto a lower dimensional space.
    """
    pca = PCA(n_components=n_components)
    pca.fit(X)
    return projector(pca,np.mean(X,axis=0),n_components=n_components)






