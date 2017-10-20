#!/usr/bin/python

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from Preprocess import Preprocess
from PCAImpl import PCAImpl

class KMeanImpl:
    
    def __init__(self, dimReductAlgo=None, lag=30, density=0.8, init='k-means++', n_clusters=4, max_iter = 300, algorithm='auto', tol=1e-4, verbose=False):
        if dimReductAlgo == "PCA":
            self.dimReductImpl = PCAImpl()
        else:
            self.dimReductImpl = None
        self.cluster_weight = []
        self.n_clusters = n_clusters
        self.kmean = KMeans(init=init, n_clusters=n_clusters, max_iter = max_iter, algorithm=algorithm, tol=tol, verbose=verbose)
        self.preprocess = Preprocess(data='fundamental_ratios', lag=lag, density=density)
        
    
    def prepareData(self, lag = True, dset = "all"):
        scaled_data = self.preprocess.getData('scaled', lag=lag, dset=dset)
        if self.dimReductImpl is None:
            return scaled_data
        if isinstance(self.dimReductImpl, PCAImpl):
            self.dimReductImpl.fit(scaled_data)
            f = scaled_data.as_matrix()
            if dset == "validate":
                c = np.transpose(np.array(self.dimReductImpl.getComponents()))
            else:
                c = np.transpose(np.array(self.dimReductImpl.getComponents(0.95)))
            pc = np.matmul(f, c)
            cols = range(self.dimReductImpl.numPC)
            reducedData = pd.DataFrame(data=pc, index=scaled_data.index, columns=cols)
            print reducedData
            return reducedData
            
            
    def visualizeCluster(self, data):
        dim = len(data.columns)-1
        pltIndex = 1
        print data
        for colx in data.columns:
            if colx == 'label':
                continue
            for coly in data.columns:
                if coly == 'label':
                    continue
                plt.subplot(dim, dim, pltIndex)
                pltIndex += 1
                if colx >= coly:
                    continue
                for label in range(self.n_clusters):
                    x = (data[data['label']==label])[colx]
                    y = (data[data['label']==label])[coly]
                    plt.xlabel(colx)
                    plt.ylabel(coly)
                    plt.scatter(x, y)
        plt.show()    
        
        
    def train(self, trainset=None):
        if trainset is not None:
            data = trainset
        else:
            data = self.prepareData(lag=True, dset="train")
        data['label'] = self.kmean.fit_predict(data)
        return data
        
        
    def validate(self, validateset):
        validateset['label'] = self.kmean.predict(validateset)
        return validateset
        
        
    def train_validate(self):
        trainSet = self.prepareData(lag=True, dset="train")
        validateSet = self.prepareData(lag=True, dset="validate")
        t = self.train(trainset = trainSet)
        v = self.validate(validateset = validateSet)
        return t,v
        
        
    def predict(self):
        df = self.prepareData(lag=False)
        df['label'] = self.kmean.predict(df)
        return df
