#!/usr/bin/python3

import numpy as np
from scipy import optimize

#reference: https://arxiv.org/pdf/1003.2920.pdf
def LogPeriodicPowerLaw(series, A, B, Tc, beta, C, omega, phi):
    dT = np.subtract(Tc, series)
    exponential_term = np.multiply(np.power(dT, beta), B)
    periodic_term = np.cos(np.add(np.multiply(np.log(dT), omega), phi))
    oscillatory_term = np.multiply(periodic_term, C)
    fitted = A + np.multiply(exponential_term, np.add(oscillatory_term, 1))
    residual = np.subtract(series, fitted)  # use raw price, not log price (10)
    return residual

def precompute_constant(series, omega, Tc, beta, phi):
    dT = np.subtract(Tc, series)
    exponential_term = np.power(dT, beta)
    periodic_term = np.cos(np.add(np.multiply(np.log(dT), omega), phi))
    return exponential_term, periodic_term

def lppl_eval(params, series, exponential_term, periodic_term):
    A = params[0]
    B = params[1]
    C = params[2]
    fitted = A + np.multiply(np.multiply(exponential_term, B), np.add(np.multiply(periodic_term, C), 1))
    residual = np.subtract(series, fitted)  # use raw price, not log price (10)
    rmse = np.sum(np.power(residual, 2))
    return rmse

def optimize_ABC(series, omega, Tc, beta, phi):
    exponential_term, periodic_term = precompute_constant(series, omega, Tc, beta, phi)
    params0 = [0, 0, 0]  # TODO: FIND A GOOD INITIAL GUESS
    opt = optimize.fmin(func=lppl_eval, x0=params0, args=(exponential_term, periodic_term,), xtol=0.0001, disp=False)
    xopt = opt[0]
    fopt = opt[1]
    return xopt, fopt

def search_beta_phi(omega, Tc, grid_size=20):
    pass



