#!/usr/bin/python3

"""GARCH.py
Description:
    estimate daily volatility using GARCH(p,q) model. The estimated volatility is validated
    using intraday bar data
"""

import numpy as np
import pandas as pd
from scipy.optimize import fmin
from Preprocess import Preprocess


class GARCH:

    """constructor
    """
    def __init__(self, p, q):
        self.p = p  # order of residual term
        self.q = q  # order of variance term
        self.preprocess = Preprocess(data='bars')

    """
        Description:
            prepare all bar data into a DataFrame organized by symbols, residual and mean
        Output:
            formatedData: the DataFrame with processed(compute vaiance and mean) and organized bar data
    """
    def prepareData(self):
        print("start retrieving data...")
        rawData = self.preprocess.get_data(dset="all")
        rawData["date"] = rawData["timestamp"].apply(lambda x: x.date())
        rawData["time"] = rawData["timestamp"].apply(lambda x: x.time())
        symbols = (rawData.index).unique().values
        dates = sorted((rawData["date"]).unique())
        formatedData = {}
        count = 0
        print("start formatting data...")
        for symbol in symbols:
            count += 1
            print(count, ", process for symbol:", symbol)
            symbolData = rawData[rawData.index == symbol].copy()
            symbolDf = pd.DataFrame(index=dates, columns=["vari", "resi"])
            # compute log change
            change = (symbolData["wap"].pct_change()).add(1)
            logChange = change.apply(lambda x: np.log(x))
            mu = logChange.mean()
            logChange = logChange.subtract(mu)
            logChange.iloc[0] = 0
            symbolData["change"] = logChange
            vari, resi = 0, 0
            for date in dates:
                series= symbolData[symbolData["date"] == date]["change"]
                v = series.var()
                r = series.mean()
                if not np.isnan(v):
                    vari = v
                if not np.isnan(r):
                    resi = r
                symbolDf.loc[date, "vari"] = vari
                symbolDf.loc[date, "resi"] = resi
                print("------>",date, "vari:", vari, "resi:", resi)
            formatedData[symbol] = symbolDf
        return formatedData

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
        size = resi.size
        lag = beta.size
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
        for symbol in formatedData.keys():
            try:
                theta0 = [0.05 for x in range(self.p+self.q+1)]
                result = fmin(func=self.costFunc, x0=theta0, args=((formatedData[symbol])["resi"],))
                print(result)
            except Exception as e:
                print(str(e))


if __name__ == "__main__":  # TODO: IMPROVE MEMORY EFFICIENCY, OTHERWISE UPGRADE MEMORY
    garch = GARCH(1, 1)
    data = garch.prepareData()
    garch.optimizeParameters(data)
