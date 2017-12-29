#!/usr/bin/python3

"""GARCH.py
Description:
    estimate daily volatility using GARCH(p,q) model. The estimated volatility is validated
    using intraday bar data
"""

import time
import numpy as np
import pandas as pd
import traceback
import matplotlib.pyplot as plt
from scipy import optimize
from scipy import stats
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

    """
    Incomplete
    """
    def computeVolatility(self):
        preprocess = Preprocess(data='bars')
        df = preprocess.get_data(dset='all')
        df["date"] = df["timestamp"].apply(lambda x: x.date()).astype('category')
        dates = sorted((df["date"]).unique())
        volatility = pd.DataFrame(index=dates)
        count = 0
        for symbol in df.index.unique():
            count += 1
            print(count, " processing: ", symbol)
            wap = df[df.index == symbol][["date", "wap"]]
            mean = wap["wap"].mean()
            wap["wap"] = wap["wap"].divide(mean).apply(lambda x: np.log(x))
            symbol_variance = pd.Series(index=dates)
            for date in dates:
                vari = wap[wap["date"] == date]["wap"].var()
                symbol_variance.loc[date] = vari
            volatility[symbol] = symbol_variance.fillna(mean)
        print(volatility)
        return volatility

    """
    Incomplete
    """
    def inaccuracy(self, theta, resi, symbol_volatility):
        vari = self.garch(theta, resi)
        sl = min(len(resi), len(symbol_volatility))  # shared length, force two series to the same length
        print(vari[0:sl])
        plt.close()
        plt.plot(range(sl), symbol_volatility[0:sl], 'r.', label="real")
        plt.plot(range(sl), vari[0:sl], 'b.', label="garch")
        plt.show(block=False)
        time.sleep(1)

    """
        Description:
            the cost function of GARCH parameter fit
        Input:
            theta: array holding GARCH parameters [omega, [p], [q]]
            resi: price residual
        Output:
            cost of model
    """
    def maximumLikelihood(self, theta, resi):
        vari = self.garch(theta, resi)
        negative_likelihood = np.log(2*np.pi*vari)+np.divide(np.power(resi, 2), vari)
        return np.sum(negative_likelihood)

    """
        Description:
            GARCH model for volatility estimation
        Input:
            theta: array holding GARCH parameters [omega, [p], [q]]
            resi: price residual
        Output:
            vari: computed series of variance
    """
    def garch(self, theta, resi):
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
        for r in range(size-1):
            pterm = 0
            for i in range(len(alpha)):
                if r-i >= 0:  # reduce order at start
                    pterm += alpha[i] * np.power(resi[r-i], 2)
            qterm = 0
            for j in range(len(beta)):
                if r-j >= 0:  # reduce order if necessary, starting order 1
                    qterm += beta[j] * vari[r-j]
            vari[r+1] = omega + pterm + qterm      
        return vari

    """
        Description:
            optimize GARCH parameter
        Input:
            formatedData: the DataFrame with processed(compute variance and mean) and organized bar data
    """
    def optimizeParameters(self, residuals):
        paramSize = self.p+self.q+1
        theta0 = [0.05 for x in range(paramSize)]
        for symbol in residuals.keys():
            try:
                xopt = optimize.fmin(func=self.maximumLikelihood, x0=theta0, args=(residuals[symbol].values,),
                                     xtol=0.0001, disp=False)
                VaR = np.multiply(np.sqrt(self.garch(xopt, residuals[symbol].values)), stats.norm.ppf(0.95))
                plt.close()
                plt.plot(range(len(VaR)), VaR, 'r-')
                plt.plot(range(len(VaR)), -VaR, 'r-')
                plt.plot(range(len(residuals[symbol].values)), residuals[symbol].values, 'b-')
                plt.show(block=False)
                time.sleep(5)
                if len(xopt) == paramSize:
                    self.omega = np.append(self.omega, xopt[0])
                    self.alpha = np.append(self.alpha, [xopt[1:-self.q]], axis=0)
                    self.beta = np.append(self.beta, [xopt[self.p+1:]], axis=0)
            except Exception as e:
                traceback.print_exc()
                print(str(e))


if __name__ == "__main__":
    garch = GARCH(3, 3)
    data = garch.prepData()
    garch.optimizeParameters(data)
    print(garch.omega)
    print(garch.alpha)
    print(garch.beta)
    plt.plot(garch.alpha[:, 0], garch.beta[:, 0], 'b.', label="1st order")
    plt.plot(garch.alpha[:, 1], garch.beta[:, 1], 'r.', label="2nd order")
    plt.plot(garch.alpha[:, 2], garch.beta[:, 2], 'y.', label="3rd order")
    plt.show()

