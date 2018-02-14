#!/usr/bin/python3

import sys
import numpy as np
from Preprocess import Preprocess
from scipy import optimize


def get_series(benchmark="snp500"):
    preprocess = Preprocess(lag=360)
    index_series = preprocess.retrieve_benchmark(benchmark)
    return index_series["close"]


# reference: https://arxiv.org/pdf/1003.2920.pdf
# https://arxiv.org/pdf/1002.1010.pdf
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
    mse = np.sum(np.power(residual, 2))
    return mse


def optimize_ABC(series, omega, Tc, beta, phi):
    exponential_term, periodic_term = precompute_constant(series, omega, Tc, beta, phi)
    params0 = [0, 0, 0]  # TODO: FIND A GOOD INITIAL GUESS
    opt = optimize.fmin(func=lppl_eval, x0=params0, args=(exponential_term, periodic_term,), xtol=0.0001, disp=False)
    xopt = opt[0]
    fopt = opt[1]
    return xopt, fopt


def search_beta_phi(series, omega, Tc, grid_size=21, beta_range=[0.15, 0.51], phi_range=[0, 6.28]):
    opt_beta, opt_phi = 0, 0
    opt_mse = sys.maxsize
    for beta in [i * (beta_range[1]-beta_range[0])/grid_size for i in range(grid_size)]:
        for phi in [i * (phi_range[1] - phi_range[0]) / grid_size for i in range(grid_size)]:
            xopt, fopt = optimize_ABC(series, omega, Tc, beta, phi)
            if fopt < opt_mse:
                opt_mse = fopt
                opt_beta = beta
                opt_phi = phi
    return opt_mse, opt_beta, opt_phi


def search_omega_tc(series, grid_size=21, Tc_range=[1, 260], omega_range=[4.8, 7.92]):
    fit_Tc, fit_omega, fit_beta, fit_phi = 0, 0, 0, 0
    fit_mse = sys.maxsize
    for Tc in [i * (Tc_range[1]-Tc_range[0])/grid_size for i in range(grid_size)]:
        for omega in [i * (omega_range[1] - omega_range[0]) / grid_size for i in range(grid_size)]:
            opt_mse, opt_beta, opt_phi = search_beta_phi(series, omega, Tc)
            if opt_mse < fit_mse:
                fit_mse = opt_mse
                fit_Tc = Tc
                fit_omega = omega
                fit_beta = opt_beta
                fit_phi = opt_phi
    return fit_mse, fit_Tc, fit_omega, fit_beta, fit_phi






