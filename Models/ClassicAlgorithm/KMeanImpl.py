#!/usr/bin/python

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from Preprocess import Preprocess
from PCAImpl import PCAImpl

class KMeanImpl:
    
    def __init__(self, lag=30, density=0.8, n_clusters=4):
        self.cluster_weight = []
        self.n_clusters = n_clusters
        self.kmean = KMeans(n_clusters=n_clusters, n_init=10, algorithm='auto')
        self.preprocess = Preprocess(data='fundamental_ratios', lag=lag, density=density)
        
    
    def getData(self, dimReduction = None):
        scaled_data = self.preprocess.getData('scaled')
        if dimReduction is None:
            return scaled_data
        if dimReduction == 'PCA':
            PCA = PCAImpl()
            PCA.fit(scaled_data)
            f = scaled_data.as_matrix()
            c = np.transpose(np.array(PCA.getComponents(0.05)))
            pc = np.matmul(f, c)
            cols = range(PCA.numPC)
            reducedData = pd.DataFrame(data=pc, index=scaled_data.index, columns=cols)
            print reducedData
            return reducedData
        
        
    def fit_predict(self, df):
        km = KMeans(init='k-means++', n_clusters=self.n_clusters, max_iter = 300, algorithm='full', tol=1e-4, verbose=True)
        print df
        df['label'] = km.fit_predict(df)
        print df.columns
        return df
        
    
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


kmc = KMeanImpl()
data = kmc.getData(dimReduction='PCA')
data2 = kmc.fit_predict(data)
#print data2[data2['label'] == 3]
#print data.shape
kmc.visualizeCluster(data)


#k = KMeans(init='random', n_clusters=50, max_iter = 300, algorithm='full', tol=1e-25, verbose=True)
#p = k.fit_predict(data.as_matrix())
#for i in p:
#    print i
