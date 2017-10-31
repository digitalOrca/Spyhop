#!/usr/bin/python3

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from Preprocess import Preprocess
from PCAImpl import PCAImpl

class KMeansImpl(KMeans):
    
    def __init__(self, lag=30, density=0.8, dimReductAlgo=None, n_clusters=4, init='k-means++', n_init=10, max_iter=300, tol=0.0001, precompute_distances="auto", verbose=0, random_state=None, copy_x=True, n_jobs=1, algorithm="auto"):
        self.dimReductAlgo = dimReductAlgo
        self.n_clusters = n_clusters # necessary for visualizeCluster
        KMeans.__init__(self, n_clusters=n_clusters, init=init, n_init=n_init, max_iter=max_iter, tol=tol, precompute_distances=precompute_distances, verbose=verbose, random_state=random_state, copy_x=copy_x, n_jobs=n_jobs, algorithm=algorithm)
        self.preprocess = Preprocess(data='fundamental_ratios', lag=lag, density=density)
        
    
    def prepareData(self, lag = True, dset = "all"):
        scaled_data = self.preprocess.getData('scaled', lag=lag, dset=dset)
        if self.dimReductAlgo is None:
            return scaled_data
        if isinstance(self.dimReductAlgo, PCAImpl):
            self.dimReductAlgo.fit(scaled_data)
            f = scaled_data.as_matrix()
            if dset == "validate" or dset == "all":
                c = np.transpose(np.array(self.dimReductAlgo.getComponents()))
            else:
                c = np.transpose(np.array(self.dimReductAlgo.getComponents(0.95)))
            pc = np.matmul(f, c)
            cols = range(self.dimReductAlgo.numPC)
            reducedData = pd.DataFrame(data=pc, index=scaled_data.index, columns=cols)
            #print(reducedData)
            return reducedData
            
            
    def visualizeCluster(self, data):
        dim = len(data.columns)-1
        pltIndex = 1
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
            traindata = trainset
        else:
            traindata = self.prepareData(lag=True, dset="train")
        traindata['label'] = super(KMeansImpl, self).fit_predict(traindata)
        return traindata
        
        
    def validate(self, validateset):
        validateset['label'] = super(KMeansImpl, self).predict(validateset)
        return validateset
        
        
    def train_validate(self):
        trainSet = self.prepareData(lag=True, dset="train")
        validateSet = self.prepareData(lag=True, dset="validate")
        t = self.train(trainset = trainSet)
        v = self.validate(validateset = validateSet)
        return t,v
        
        
    def predict(self):
        df = self.prepareData(lag=False)
        df['label'] = super(KMeansImpl, self).predict(df)
        return df
