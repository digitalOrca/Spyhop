#!/usr/bin/python3

import sys
import numpy as np
from Preprocess import Preprocess
import matplotlib.pyplot as plt

# reference: https://arxiv.org/pdf/1003.2920.pdf
# https://arxiv.org/pdf/1002.1010.pdf

def get_series(benchmark="snp500"):
    preprocess = Preprocess(lag=360)
    index_series = preprocess.retrieve_benchmark(benchmark)
    return index_series["close"]


def precompute_constant(series, omega, Tc, beta, phi):
    dT = [d+Tc for d in list(range(len(series), 0, -1))]
    f = np.power(dT, beta)
    g = np.multiply(f, np.cos(np.add(np.multiply(np.log(dT), omega), phi)))
    return f, g


def eval_lppl(series, Tc, omega, beta, phi):
    f, g = precompute_constant(series, omega, Tc, beta, phi)
    y = series
    n = len(series)
    y_matrix = np.array([y.sum(), np.multiply(y, f).sum(), np.multiply(y, g).sum()])
    x_matrix = np.array([[n,       f.sum(),                 g.sum()],
                         [f.sum(), np.multiply(f, f).sum(), np.multiply(f, g).sum()],
                         [g.sum(), np.multiply(f, g).sum(), np.multiply(g, g).sum()]])
    try:
        opt_abc = np.dot(np.linalg.inv(x_matrix), y_matrix)
    except:
        return None
    fit = np.add(opt_abc[0], np.add(np.multiply(opt_abc[1], f), np.multiply(opt_abc[2], g)))
    return fit


def optimize_ABC(series, omega, Tc, beta, phi):
    f, g = precompute_constant(series, omega, Tc, beta, phi)
    #y = np.add(A, np.add(np.multiply(B, f), np.multiply(C, g)))
    y = series
    n = len(series)
    y_matrix = np.array([y.sum(), np.multiply(y, f).sum(), np.multiply(y, g).sum()])
    x_matrix = np.array([[n,       f.sum(),                 g.sum()],
                         [f.sum(), np.multiply(f, f).sum(), np.multiply(f, g).sum()],
                         [g.sum(), np.multiply(f, g).sum(), np.multiply(g, g).sum()]])
    try:
        opt_abc = np.dot(np.linalg.inv(x_matrix), y_matrix)
    except:
        return [0,0,0], sys.maxsize
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
            xopt, fopt = optimize_ABC(series, omega, Tc, beta, phi)
            if fopt < opt_mse:
                opt_mse = fopt
                opt_abc = xopt
                opt_beta = beta
                opt_phi = phi
    return opt_mse, opt_abc, opt_beta, opt_phi


def search_omega_tc(series, Tc_grid=259, omega_grid=50, Tc_range=[1, 260], omega_range=[4.8, 7.92], fig=None, ax=None):
    fit_abc = []
    fit_Tc, fit_omega, fit_beta, fit_phi = 0, 0, 0, 0
    fit_mse = sys.maxsize
    count_Tc = 0
    best_fit = series
    x = range(len(series))
    for Tc in [i * (Tc_range[1]-Tc_range[0])/Tc_grid for i in range(Tc_grid)]:
        count_Tc += 1
        count_omega = 0
        for omega in [i * (omega_range[1] - omega_range[0])/omega_grid for i in range(omega_grid)]:
            count_omega += 1
            print("optimizing >> Tc:%s, omega:%s" % (count_Tc, count_omega))
            print("    current best--> MSE:%s, Tc:%s, omega:%s, beta:%s, phi:%s"
                  % (fit_mse, fit_Tc, fit_omega, fit_beta, fit_phi))
            opt_mse, opt_abc, opt_beta, opt_phi = search_beta_phi(series, omega, Tc)

            fit = eval_lppl(series, Tc, omega, opt_beta, opt_phi)
            if fit is not None:
                ax1.clear()
                ax1.plot(x, series, 'b--')
                ax1.plot(x, fit, 'r--')
                ax1.plot(x, best_fit, 'g--')
                plt.pause(0.01)

            if opt_mse < fit_mse:
                fit_mse = opt_mse
                fit_Tc = Tc
                fit_omega = omega
                fit_abc = opt_abc
                fit_beta = opt_beta
                fit_phi = opt_phi
                if fit is not None:
                    best_fit = fit

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





