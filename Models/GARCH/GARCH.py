#!/usr/bin/python3

import numpy as np
from Preprocess import Preprocess

def GARCH(resi, omega, alpha, beta):
    
    assert omega > 0
    assert np.amin(alpha) > 0
    assert np.amin(beta) > 0
    assert np.sum(alpha) + np.sum(beta) < 1
    
    size = resi.size
    lag = beta.size
    vari = np.zeros(shape=size)
    # initialize variance as the overall residual series variance
    vari[0] = np.var(resi, axis=0)
    for v in range(size-1):
        vari[v+1] += omega
        for i in alpha.size:
            # reduce order if necessary
            if v-i-1 >= 0:
                vari[v] += alpha[i]　* np.power(resi[v-i-1], 2)
        for j in beta.size:
            # reduce order if necessary
            if v-j-1 >= 0:
                vari[v] += beta[j] * vari[v-j-1]
    return vari
    
    
class GARCH:
    
    def __init__(self, omega, alpha, beta):
        self.omega = omega
        self.alpha = alpha
        self.beta = beta
        self.preprocess = Preprocess(data='open_close', lag=lag)
        
    def prepareData(self, lag):
        return self.preprocess.getData()
        
    
        
        
    
        
    
    
    
