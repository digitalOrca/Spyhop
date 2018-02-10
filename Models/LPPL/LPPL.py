#!/usr/bin/python3

import random
import numpy as np

#reference: https://arxiv.org/pdf/1003.2920.pdf
def LogPeriodicPowerLaw(series, A, B, Tc, m, C, omega, phi):
    deltaT = np.power(np.subtract(Tc, series), m)
    oscillatory_term = np.multiply(np.multiply(deltaT, np.cos(np.add(np.multiply(np.log(deltaT), omega), phi))), C)
    exponential_term = np.multiply(deltaT, B)
    fitted = A + exponential_term + oscillatory_term
    residual = np.subtract(series, fitted)
    return residual

def randomParameters():
    # B>0
    # 0 < m < 1
    # T > n
    m = random.uniform(0, 1)


