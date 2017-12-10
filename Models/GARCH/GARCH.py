#!/usr/bin/python3

import numpy as np

def GARCH(resi, omega, alpha, beta):
    #TODO condition check
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
    
    
