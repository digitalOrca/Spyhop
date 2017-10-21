#!/usr/bin/python

from sklearn.decomposition import PCA
from Preprocess import Preprocess

class PCAImpl(PCA):

    def __init__(self, density=0.8, retention = 0.95, n_components=None, copy=True,\
                                        whiten=False, svd_solver='auto', tol=0.0, \
                                        iterated_power='auto', random_state=None):
                                        
        PCA.__init__(self, n_components=n_components, copy=copy, whiten=whiten, \
                                        svd_solver=svd_solver, tol=tol, \
                                        iterated_power=iterated_power, \
                                        random_state=random_state)
        self.preprocess = Preprocess(data='fundamental_ratios', density=density)
        self.retention = retention
        self.numPC = 0
    
    def getComponents(self, retention=None):
        if retention is not None:
            self.numPC = sum(i > (1.0-self.retention) for i in self.explained_variance_ratio_)
        return self.components_[:self.numPC]
