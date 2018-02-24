#!/usr/bin/python3

import sys
import numpy as np
import pandas as pd
from Preprocess import Preprocess
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity

# reference: https://arxiv.org/pdf/1003.2920.pdf
# https://arxiv.org/pdf/1002.1010.pdf


def get_series(benchmark="snp500"):
    #preprocess = Preprocess(lag=360)
    #index_series = preprocess.retrieve_benchmark(benchmark)
    #return index_series["close"]
    #--------------------------------------------------------
    return pd.read_csv("/home/meng/Downloads/SP500.csv")["Close"]


def segment_series(series, num_segments=100):
    progression = []
    n = len(series)
    baseline = series[:int(n/2)]
    extended = series[int(n/2):]
    progression.append(baseline)
    for i in range(1, num_segments+1):
        ext = extended[:int((i/num_segments)*len(extended))]
        new_series = np.concatenate((baseline, ext), axis=0)
        progression.append(new_series)
    return progression


def precompute_constant(length, omega, Tc, beta, phi):
    dT = [d+Tc for d in list(range(int(length), 0, -1))]
    f = np.power(dT, beta)
    g = np.multiply(f, np.cos(np.add(np.multiply(np.log(dT), omega), phi)))
    return f, g


def extended_fit(series, abc, Tc, omega, beta, phi):
    f, g = precompute_constant(len(series)+Tc, omega, Tc, beta, phi)
    ext_fit = np.add(abc[0], np.add(np.multiply(abc[1], f), np.multiply(abc[2], g)))
    return ext_fit


def optimize_abc(series, omega, Tc, beta, phi):
    f, g = precompute_constant(len(series), omega, Tc, beta, phi)
    y = series
    n = len(series)
    y_matrix = np.array([y.sum(), np.multiply(y, f).sum(), np.multiply(y, g).sum()])
    f_sum = f.sum()
    g_sum = g.sum()
    ff_sum = np.multiply(f, f).sum()
    fg_sum = np.multiply(f, g).sum()
    gg_sum = np.multiply(g, g).sum()

    x_matrix = np.array([[n,     f_sum,  g_sum],
                         [f_sum, ff_sum, fg_sum],
                         [g_sum, fg_sum, gg_sum]])
    try:
        opt_abc = np.dot(np.linalg.inv(x_matrix), y_matrix)
    except:
        return [0, 0, 0], sys.maxsize

    fit = np.add(opt_abc[0], np.add(np.multiply(opt_abc[1], f), np.multiply(opt_abc[2], g)))
    residual = np.subtract(series, fit)  # use raw price, not log price (10)
    mse = np.sum(np.power(residual, 2))
    return opt_abc, mse


def optimize_parameters(series, Tc_grid=179, omega_grid=30, beta_grid=100, phi_grid=30,
                        Tc_range=[1, 180], omega_range=[4.8, 7.92], beta_range=[0.15, 0.51], phi_range=[0, 6.28],
                        fig=None, ax=None):
    fit_abc = []
    fit_Tc, fit_omega, fit_beta, fit_phi = 0, 0, 0, 0
    fit_mse = sys.maxsize
    best_fit = series
    n = len(series)
    x = range(n)
    for Tc in [i * (Tc_range[1]-Tc_range[0])/Tc_grid + Tc_range[0] for i in range(Tc_grid)]:
        for beta in [(i+1) * (beta_range[1] - beta_range[0]) / beta_grid + beta_range[0] for i in range(beta_grid)]:
            for omega in [i * (omega_range[1] - omega_range[0]) / omega_grid + omega_range[0] for i in range(omega_grid)]:
                for phi in [i * (phi_range[1] - phi_range[0]) / phi_grid + phi_range[0] for i in range(phi_grid)]:
                    std_err = np.sqrt(np.divide(fit_mse, n))
                    print("optimizing >>> Tc:%s, beta:%s, omega:%s, phi:%s" % (Tc, beta, omega, phi))
                    print("                                  current best--> error:%s, Tc:%s, omega:%s, beta:%s, phi:%s"
                          % (std_err, fit_Tc, fit_omega, fit_beta, fit_phi))
                    sys.stdout.flush()
                    abc, mse = optimize_abc(series, omega, Tc, beta, phi)
                    if mse < fit_mse:
                        fit_mse = mse
                        fit_Tc = Tc
                        fit_omega = omega
                        fit_abc = abc
                        fit_beta = beta
                        fit_phi = phi
                        fit = extended_fit(series, abc, Tc, omega, beta, phi)
                        if fit is not None:
                            best_fit = fit
                            if fig is not None:
                                ax.clear()
                                ax.plot(x, series, 'b--')
                                ax.plot(range(len(best_fit)), best_fit, 'r--')
                                #ax.set_ylim([np.min(series)-100, np.max(series)+100])
                                title = "Best fit: [error:%s, Tc:%s, omega:%s, beta:%s, phi:%s]" \
                                        % (std_err, fit_Tc, fit_omega, fit_beta, fit_phi)
                                plt.xlabel('Time (Trading-days)')
                                plt.title(title)
                                plt.ylabel('Benchmark Index')
                                plt.pause(0.0001)

    return fit_mse, fit_abc, fit_Tc, fit_omega, fit_beta, fit_phi


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("too few argument")
    elif sys.argv[1] == "direct":
        series = get_series(benchmark="snp500").values
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111)
        fit_mse, fit_abc, fit_Tc, fit_omega, fit_beta, fit_phi = optimize_parameters(series=series, fig=fig1, ax=ax1)
        print("MSE:", fit_mse)
        print("A:", fit_abc[0])
        print("B:", fit_abc[1])
        print("C:", fit_abc[2])
        print("Tc:", fit_Tc)
        print("omega:", fit_omega)
        print("beta:", fit_beta)
        print("phi:", fit_phi)

        opt_fit = extended_fit(series, fit_abc, fit_Tc, fit_omega, fit_beta, fit_phi)
        ax1.clear()
        ax1.plot(range(len(series)), series, 'b--')
        ax1.plot(range(len(opt_fit)), opt_fit, 'r--')
        err = np.sqrt(np.divide(fit_mse, len(series)))
        title = "Best fit[error:%s, Tc:%s, omega:%s, beta:%s, phi:%s]" \
                % (err, fit_Tc, fit_omega, fit_beta, fit_phi)
        plt.xlabel('Time (Trading-days)')
        plt.title(title)
        plt.ylabel('Benchmark Index')
        plt.show()
    elif sys.argv[1] == "staggered":
        series = get_series(benchmark="snp500").values
        progression = segment_series(series, num_segments=100)
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111)
        crash_vote = []
        for s in progression:
            fit_mse, fit_abc, fit_Tc, fit_omega, fit_beta, fit_phi = optimize_parameters(series=s, fig=fig1, ax=ax1)
            crash_date = s[-1] + fit_Tc
            crash_vote.append(crash_date)
        plt.close()  # close fig1
        # crash likelihood plot
        kde = KernelDensity(kernel='gaussian', bandwidth=0.2)
        crash_dist = np.array(crash_vote)[:, np.newaxis]
        kde.fit(crash_dist)
        log_dens = kde.score_samples(crash_dist)
        fig2, ax1 = plt.subplots()
        ax1.plot(range(len(series)), series, 'b--')
        ax1.set_xlabel('Trading Days')
        ax1.set_ylabel('Benchmark')
        ax2 = ax1.twinx()
        ax2.set_ylabel('Crash Likelyhood')
        ax2.plot(crash_dist, np.exp(log_dens), 'r--')
        plt.show()
    else:
        print("invalid argument")






