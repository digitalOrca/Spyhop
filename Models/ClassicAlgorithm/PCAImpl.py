#!/usr/bin/python

from sklearn.decomposition import PCA
from Preprocess import Preprocess

class PCAImpl:

    def __init__(self, density=0.8, n_components=None, copy=True, whiten=False,\
                                        svd_solver='auto', tol=0.0, \
                                        iterated_power='auto', random_state=None):
        self.pca = PCA(n_components=n_components, copy=copy, whiten=whiten, \
                                        svd_solver=svd_solver, tol=tol, \
                                        iterated_power=iterated_power, \
                                        random_state=random_state)
        self.preprocess = Preprocess(data='fundamental_ratios', density=density)
        self.numPC = 0


    def fit(self, data):
        return self.pca.fit(data)
        

    def getComponents(self, retention=None):
        if retention is not None:
            varRatio = self.pca.explained_variance_ratio_
            self.numPC = sum(i > (1.0-retention) for i in varRatio)
        return self.pca.components_[:self.numPC]
