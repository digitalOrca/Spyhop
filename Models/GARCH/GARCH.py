#!/usr/bin/python3

"""GARCH.py
Description:
    estimate daily volatility using GARCH(p,q) model. The estimated volatility is validated
    using intraday bar data
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import fmin
from Preprocess import Preprocess


class GARCH:

    """constructor
    """
    def __init__(self, p, q):
        self.p = p  # order of residual term
        self.q = q  # order of variance term
        self.omega = np.array([])
        self.alpha = np.empty(shape=(0, self.p))  # residual term parameter
        self.beta = np.empty(shape=(0, self.q))  # variance term parameter

    """
        Description:
            prepare all bar data into a DataFrame organized by symbols, residual and mean
        Output:
            formatedData: the DataFrame with processed residual data
    """
    def prepData(self):
        preprocess = Preprocess(data='open_close')
        daily_log_change = preprocess.get_data().pct_change().fillna(0).add(1).applymap(lambda x: np.log(x))
        mu = daily_log_change.mean()
        residual = daily_log_change.subtract(mu)
        return residual

    def computeTrueVolatility(self):
        preprocess = Preprocess(data='bars')
        df = preprocess.get_data(dset='all')
        df["date"] = df["timestamp"].apply(lambda x: x.date()).astype('category')
        dates = sorted((df["date"]).unique())
        formated_variance = pd.DataFrame(index=dates)
        count = 0
        for symbol in df.index.unique():
            print(count, " processing: ", symbol)
            wap = df[df.index == symbol][["date", "wap"]]
            symbol_variance = pd.Series(index=dates)
            for date in dates:
                vari = wap[wap["date"] == date].var()
                symbol_variance.loc[date] = vari
            formated_variance[symbol] = symbol_variance
        print(formated_variance)




    """
        Description:
            the cost function of GARCH parameter fit
        Input:
            theta: array holding GARCH parameters [omega, [p], [q]]
            resi: price residual
        Output:
            cost of model
    """
    def costFunc(self, theta, resi):
        vari = self.GARCH(theta, resi)
        return np.sum(np.add(np.divide(np.power(resi, 2), vari), np.log(2*np.pi*vari)))

    """
        Description:
            GARCH model for volatility estimation
        Input:
            theta: array holding GARCH parameters [omega, [p], [q]]
            resi: price residual
        Output:
            vari: computed series of variance
    """
    def GARCH(self, theta, resi):        
        omega = theta[0]
        alpha = theta[1:-self.q]
        beta = theta[self.p+1:]
        #assert omega > 0
        #assert np.amin(alpha) > 0
        #assert np.amin(beta) > 0
        #assert np.sum(alpha) + np.sum(beta) < 1
        size = resi.shape[0]
        vari = np.zeros(shape=size)
        # initialize variance as the overall residual series variance
        vari[0] = np.var(resi, axis=0)
        v = vari[0]
        for r in range(size-1):
            pterm = 0
            for i in range(len(alpha)):
                if r-i >= 0:  # reduce order at start
                    pterm += alpha[i] * np.power(resi[r-i], 2)
            qterm = 0
            for j in range(len(beta)):
                if r-j >= 0: # reduce order if necessary, starting order 1
                    qterm += beta[j] * vari[r-j]
            vari[r+1] = omega + pterm + qterm      
        return vari

    """
        Description:
            optimize GARCH parameter
        Input:
            formatedData: the DataFrame with processed(compute vaiance and mean) and organized bar data
    """
    def optimizeParameters(self, formatedData):
        paramSize = self.p+self.q+1
        for symbol in formatedData.keys():
            try:
                theta0 = [0.05 for x in range(paramSize)]
                xopt = fmin(func=self.costFunc, x0=theta0, args=(formatedData[symbol].values,))
                print(xopt)
                if len(xopt) == paramSize:
                    self.omega = np.append(self.omega, xopt[0])
                    self.alpha = np.append(self.alpha, [xopt[1:-self.q]], axis=0)
                    self.beta = np.append(self.beta, [xopt[self.p+1:]], axis=0)
            except Exception as e:
                print(str(e))


if __name__ == "__main__":
    garch = GARCH(3, 3)
    # data = garch.prepData()
    garch.computeTrueVolatility()
    """
    garch.optimizeParameters(data)
    print(garch.omega)
    print(garch.alpha)
    print(garch.beta)
    plt.plot(garch.alpha[:, 0], garch.beta[:, 0], 'b.', label="1st order")
    plt.plot(garch.alpha[:, 1], garch.beta[:, 1], 'r.', label="2nd order")
    plt.plot(garch.alpha[:, 2], garch.beta[:, 2], 'y.', label="3rd order")
    plt.show()
    """
