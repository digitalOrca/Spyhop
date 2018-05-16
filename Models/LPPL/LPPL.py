#!/usr/bin/python3

"""LPPL.py
Description:
    implement log-periodic power law for predicting stock market crash
    reference: https://arxiv.org/pdf/1003.2920.pdf
    https://arxiv.org/pdf/1002.1010.pdf
"""

import sys
import datetime
import numpy as np
import pandas as pd
from Preprocess import Preprocess
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity

"""get_series
    Description:
        retrieve historic benchmark index data (read from downloaded data for now)
    Input:
        benchmark: name of benchmark for analysis
"""
def get_series(benchmark="snp500"):
    preprocess = Preprocess(lag=2800)
    index_series = preprocess.retrieve_benchmark(benchmark)
    return index_series["close"]


"""segment_series
    Description:
        segment the historic data set to compute for crash date progression
    Input:
        series: complete data series
        base_frac: starting fraction of the complete series
        num_segments: the number of segment to proceed to the complete series
"""
def segment_series(series, base_frac=0.5, num_segments=100):
    progression = []
    base = int(len(series)*base_frac)
    baseline = series[:base]
    extended = series[base:]
    progression.append(baseline)
    for i in range(1, num_segments+1):
        cutoff = int((i/num_segments)*len(extended))
        ext = extended[:cutoff]
        new_series = np.concatenate((baseline, ext), axis=0)
        progression.append(new_series)
    return progression


"""cache constants for faster computation"""
Tc_cache, beta_cache, omega_cache, phi_cache = 0, 0, 0, 0
dT_cache, p_cache, f_cache = 0, 0, 0

"""precompute_constant
    Description:
        compute f, g using cached parameters or terms
    Input:
        length: length of series
        Tc: model parameter
        beta: model parameter
        omega: model parameter
        phi: model parameter
"""
def precompute_constant(length, Tc, beta, omega, phi):
    global Tc_cache, beta_cache, omega_cache, phi_cache, dT_cache, p_cache, f_cache

    if Tc == Tc_cache:
        dT = dT_cache
        if beta == beta_cache:
            f = f_cache
        else:
            beta_cache = beta
            f = np.power(dT, beta)
            f_cache = f

        if omega == omega_cache:
            p = p_cache
        else:
            omega_cache = omega
            p = np.multiply(np.log(dT), omega)
            p_cache = p
        g = np.multiply(f, np.cos(np.add(p, phi)))  # always re-compute g
    else:
        dT = np.add(np.array([d for d in list(range(int(length), 0, -1))]), Tc)
        f = np.power(dT, beta)
        p = np.multiply(np.log(dT), omega)
        g = np.multiply(f, np.cos(np.add(p, phi)))
        # update all cache values
        Tc_cache = Tc
        beta_cache = beta
        omega_cache = omega
        phi_cache = phi
        dT_cache = dT
        p_cache = p
        f_cache = f
    return f, g


"""extended_fit
    Description:
        compute for fit line till day of predicted crash
    Input:
        series: historical benchmark data
        abc: model parameters
        Tc: model parameter
        omega: model parameter
        beta: model parameter
        phi: model parameter
"""
def extended_fit(series, abc, Tc, omega, beta, phi):
    f, g = precompute_constant(len(series)+Tc, Tc, beta, omega, phi)
    ext_fit = np.add(abc[0], np.add(np.multiply(abc[1], f), np.multiply(abc[2], g)))
    return ext_fit


"""optimize_abc
    Description:
        compute analytical solution for parameter A, B, C
    Input:
        series: historical benchmark data
        omega: model parameter
        Tc: model parameter
        beta: model parameter
        phi: model parameter
"""
def optimize_abc(series, omega, Tc, beta, phi):
    n = series.size  # len(series)
    f, g = precompute_constant(n, Tc, beta, omega, phi)
    y = series
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


"""optimize_parameters
    Description:
        compute optimized parameter for LPPL model
    Input:
        series: historical benchmark data
        Tc_grid: number of Tc parameter steps
        omega_grid: number of omega parameter steps
        beta_grid: number of beta parameter steps
        phi_grid: number of phi parameter steps
        Tc_range: range of Tc
        omega_range: range of omega
        beta_range: range of beta
        phi_range: range of phi
        fig: figure
        ax: figure axis
"""
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
                    #print("optimizing >>> Tc:%s, beta:%s, omega:%s, phi:%s" % (Tc, beta, omega, phi))
                    #print("                                  current best--> error:%s, Tc:%s, omega:%s, beta:%s, phi:%s"
                    #      % (std_err, fit_Tc, fit_omega, fit_beta, fit_phi))
                    #sys.stdout.flush()
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
                                crash_date_str = singularity_Date(fit_Tc)
                                title = "Best fit: [error:%s, Tc:%s(%s), omega:%s, beta:%s, phi:%s]" \
                                        % (std_err, fit_Tc, crash_date_str, fit_omega, fit_beta, fit_phi)
                                plt.xlabel('Time (Trading-days)')
                                plt.title(title)
                                plt.ylabel('Benchmark Index')
                                plt.pause(0.0001)
    return fit_mse, fit_abc, fit_Tc, fit_omega, fit_beta, fit_phi


"""singularity_Date
    Description:
        Compute the project date of crash from Tc
    Input:
        Tc: optimized number of trading days till crash
"""
def singularity_Date(Tc):
    c_day = datetime.datetime.now()
    holidays = pd.read_csv("/home/meng/Projects/NeuroTrader/Models/Config/TradingHoliday.csv")\
        .Date.apply(lambda x: str(x).strip()).tolist()
    incr = datetime.timedelta(days=1)
    while Tc > 0:
        if (c_day + incr).weekday() <= 4 and (c_day + incr).strftime("%Y-%m-%d") not in holidays:  # weekday
            Tc -= 1
        c_day += incr
    return c_day.strftime("%Y-%m-%d")


"""Main"""
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("too few argument")
    elif sys.argv[1] == "direct":
        series = get_series(benchmark="snp500").values
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111)
        fit_mse, fit_abc, fit_Tc, fit_omega, fit_beta, fit_phi = optimize_parameters(series=series, fig=fig1, ax=ax1)
        crash_date_str = singularity_Date(fit_Tc)
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
        title = "Best fit[error:%s, Tc:%s(%s), omega:%s, beta:%s, phi:%s]" \
                % (err, fit_Tc, crash_date_str, fit_omega, fit_beta, fit_phi)
        plt.xlabel('Time (Trading-days)')
        plt.title(title)
        plt.ylabel('Benchmark Index')
        plt.show()
    elif sys.argv[1] == "staggered":
        series = get_series(benchmark="snp500").values
        progression = segment_series(series, base_frac=0.8, num_segments=100)
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111)
        crash_vote = []
        for s in progression:
            fit_mse, fit_abc, fit_Tc, fit_omega, fit_beta, fit_phi = optimize_parameters(series=s, fig=fig1, ax=ax1)
            crash_date = len(s) + fit_Tc
            print("Staggered size:", len(s), "Crash vote:", crash_date)
            crash_vote.append(crash_date)
        print("Voting Results:")
        for v in crash_vote:
            print(v)
        plt.close()  # close fig1
        # crash likelihood plot
        kde = KernelDensity(kernel='gaussian', bandwidth=5)
        crash_dist = np.array(sorted(crash_vote))[:, np.newaxis]
        kde.fit(crash_dist)
        log_dens = kde.score_samples(crash_dist)
        fig2, ax1 = plt.subplots()
        ax1.plot(range(len(series)), series, 'b--')
        ax1.set_xlabel('Trading Days')
        ax1.set_ylabel('Benchmark')
        ax2 = ax1.twinx()
        ax2.set_ylabel('Crash Likelihood')
        ax2.plot(crash_dist, np.exp(log_dens), 'r--')
        plt.show()
    else:
        print("invalid argument")






