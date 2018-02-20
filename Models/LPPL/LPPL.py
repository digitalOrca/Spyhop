#!/usr/bin/python3

import sys
import numpy as np
import pandas as pd
from Preprocess import Preprocess
import matplotlib.pyplot as plt

# reference: https://arxiv.org/pdf/1003.2920.pdf
# https://arxiv.org/pdf/1002.1010.pdf


def get_series(benchmark="snp500"):
    #preprocess = Preprocess(lag=360)
    #index_series = preprocess.retrieve_benchmark(benchmark)
    #return index_series["close"]
    #--------------------------------------------------------
    return pd.read_csv("/home/meng/Downloads/SP500.csv")["Close"]


def precompute_constant(length, omega, Tc, beta, phi):
    dT = [d+Tc for d in list(range(int(length), 0, -1))]
    f = np.power(dT, beta)
    g = np.multiply(f, np.cos(np.add(np.multiply(np.log(dT), omega), phi)))
    return f, g


def compute_abc(y, f, g, n):
    y_matrix = np.array([y.sum(), np.multiply(y, f).sum(), np.multiply(y, g).sum()])
    x_matrix = np.array([[n, f.sum(), g.sum()],
                         [f.sum(), np.multiply(f, f).sum(), np.multiply(f, g).sum()],
                         [g.sum(), np.multiply(f, g).sum(), np.multiply(g, g).sum()]])
    try:
        return np.dot(np.linalg.inv(x_matrix), y_matrix)
    except:
        return None


def eval_lppl(series, Tc, omega, beta, phi):
    f, g = precompute_constant(len(series), omega, Tc, beta, phi)
    y = series
    n = len(series)
    opt_abc = compute_abc(y, f, g, n)
    if opt_abc is None:
        return None
    fit = np.add(opt_abc[0], np.add(np.multiply(opt_abc[1], f), np.multiply(opt_abc[2], g)))
    return fit


def extended_fit(series, abc, Tc, omega, beta, phi):
    f, g = precompute_constant(len(series)+Tc, omega, Tc, beta, phi)
    ext_fit = np.add(abc[0], np.add(np.multiply(abc[1], f), np.multiply(abc[2], g)))
    return ext_fit


def optimize_abc(series, omega, Tc, beta, phi):
    f, g = precompute_constant(len(series), omega, Tc, beta, phi)
    y = series
    n = len(series)
    opt_abc = compute_abc(y, f, g, n)
    if opt_abc is None:
        return [0, 0, 0], sys.maxsize
    fit = np.add(opt_abc[0], np.add(np.multiply(opt_abc[1], f), np.multiply(opt_abc[2], g)))
    residual = np.subtract(series, fit)  # use raw price, not log price (10)
    mse = np.sum(np.power(residual, 2))
    return opt_abc, mse


def search_beta_phi(series, omega, Tc, beta_grid=50, phi_grid=50, beta_range=[0.15, 0.51], phi_range=[0, 6.28]):
    opt_beta, opt_phi = 0, 0
    opt_mse = sys.maxsize
    opt_abc = []
    for beta in [i * (beta_range[1]-beta_range[0])/beta_grid for i in range(beta_grid)]:
        for phi in [i * (phi_range[1] - phi_range[0])/phi_grid for i in range(phi_grid)]:
            xopt, fopt = optimize_abc(series, omega, Tc, beta, phi)
            if fopt < opt_mse:
                opt_mse = fopt
                opt_abc = xopt
                opt_beta = beta
                opt_phi = phi
    return opt_mse, opt_abc, opt_beta, opt_phi


def search_omega_tc(series, Tc_grid=259, omega_grid=50, beta_grid=50, phi_grid=50,
                    Tc_range=[1, 260], omega_range=[4.8, 7.92], beta_range=[0.15, 0.51], phi_range=[0, 6.28],
                    fig=None, ax=None):
    fit_abc = []
    fit_Tc, fit_omega, fit_beta, fit_phi = 0, 0, 0, 0
    fit_mse = sys.maxsize
    best_fit = series
    x = range(len(series))
    for Tc in [i * (Tc_range[1]-Tc_range[0])/Tc_grid + Tc_range[0] for i in range(Tc_grid)]:
        for beta in [(i+1) * (beta_range[1] - beta_range[0]) / beta_grid + beta_range[0] for i in range(beta_grid)]:
            for omega in [i * (omega_range[1] - omega_range[0]) / omega_grid + omega_range[0] for i in range(omega_grid)]:
                for phi in [i * (phi_range[1] - phi_range[0]) / phi_grid + phi_range[0] for i in range(phi_grid)]:
                    print("optimizing >>> Tc:%s, beta:%s, omega:%s, phi:%s" % (Tc, beta, omega, phi))
                    #print("    current best--> MSE:%s, Tc:%s, omega:%s, beta:%s, phi:%s"
                    #      % (fit_mse, fit_Tc, fit_omega, fit_beta, fit_phi))
                    sys.stdout.flush()
                    abc, mse = optimize_abc(series, omega, Tc, beta, phi)
                    fit = extended_fit(series, abc, Tc, omega, beta, phi)

                    if mse < fit_mse:
                        fit_mse = mse
                        fit_Tc = Tc
                        fit_omega = omega
                        fit_abc = abc
                        fit_beta = beta
                        fit_phi = phi
                        if fit is not None:
                            best_fit = fit

                    if fit is not None and fig is not None:
                        ax.clear()
                        ax.plot(x, series, 'b--')
                        ax.plot(range(len(fit)), fit, 'r--')
                        ax.plot(range(len(best_fit)), best_fit, 'g--')
                        #ax.set_ylim([np.min(series)-100, np.max(series)+100])
                        plt.pause(0.001)

    return fit_mse, fit_abc, fit_Tc, fit_omega, fit_beta, fit_phi


if __name__ == "__main__":
    series = get_series(benchmark="snp500").values
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    fit_mse, fit_abc, fit_Tc, fit_omega, fit_beta, fit_phi = search_omega_tc(series=series, fig=fig, ax=ax1)
    print("MSE:", fit_mse)
    print("A:", fit_abc[0])
    print("B:", fit_abc[1])
    print("C:", fit_abc[2])
    print("Tc:", fit_Tc)
    print("omega:", fit_omega)
    print("beta:", fit_beta)
    print("phi:", fit_phi)





