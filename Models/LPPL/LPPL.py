#!/usr/bin/python3

import random
import numpy as np

#reference: https://arxiv.org/pdf/1003.2920.pdf
def LogPeriodicPowerLaw(series, A, B, Tc, beta, C, omega, phi):
    deltaT = np.power(np.subtract(Tc, series), beta)
    exponential_term = np.multiply(deltaT, B)
    oscillatory_term = np.multiply(np.multiply(deltaT, np.cos(np.add(np.multiply(np.log(deltaT), omega), phi))), C)
    fitted = A + exponential_term + oscillatory_term
    residual = np.subtract(series, fitted)
    return residual

def randomParameters():
    # reference: https://arxiv.org/pdf/1002.1010.pdf
    beta = np.random.uniform(low=0.15, high=0.51, size=1)[0]
    omega = np.random.uniform(low=4.8, high=7.96, size=1)[0]
    phi = np.random.uniform(low=0, high=2*np.pi, size=1)[0]



