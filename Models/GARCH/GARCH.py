#!/usr/bin/python3

import numpy as np
import pandas as pd
from scipy.optimize import fmin
from Preprocess import Preprocess
    
class GARCH:
    
    def __init__(self, omega, alpha, beta):
        self.omega = omega
        self.alpha = alpha
        self.beta = beta
        self.preprocess = Preprocess(data='bars')
        self.resi = None
        self.vari = None
        
    def prepareData(self):
        rawData = self.preprocess.getData(dset="all")
        rawData["date"] = rawData["timestamp"].apply(lambda x: x.date())
        rawData["time"] = rawData["timestamp"].apply(lambda x: x.time())
        symbols = (rawData.index).unique().values
        dates = sorted((rawData["date"]).unique())
        formatedData = {}
        count = 0
        for symbol in symbols:
            count += 1
            print(count, ", process for symbol:",symbol)
            symbolData = rawData[rawData.index == symbol]
            symbolDf = pd.DataFrame(index=dates, columns=["vari", "resi"])
            #compute change
            change = symbolData["wap"].pct_change() + 1
            logChange = change.apply(lambda x: np.log(x))
            symbolData["change"] = logChange
            #correct for first bar of each day
            earliestBar = symbolData.iloc[0]["time"]
            symbolData[symbolData["time"]==earliestBar]["change"] = 0
            #compute symbol mean
            mu = symbolData["change"].mean()
            symbolData["change"] = symbolData["change"].subtract(mu)
            vari, resi = 0, 0
            for date in dates:
                series= symbolData[symbolData["date"]==date]["change"]
                v = series.var()
                if not np.isnan(v):
                    vari = v
                r = series.mean()
                if not np.isnan(r):
                    resi = r
                symbolDf.loc[date, "vari"] = vari
                symbolDf.loc[date, "resi"] = resi
                print("------>",date, "vari:", vari, "resi:", resi)
                
            formatedData[symbol] = symbolDf
        return formatedData
    
    def costFunc(self, resi, vari):
         return np.sum(np.add(np.divide(np.power(resi, 2), vari), np.log(2*np.pi*vari)))

    def GARCH(resi, theta):
        omega, alpha, beta = theta
        #assert omega > 0
        #assert np.amin(alpha) > 0
        #assert np.amin(beta) > 0
        #assert np.sum(alpha) + np.sum(beta) < 1
        size = resi.size
        lag = beta.size
        vari = np.zeros(shape=size)
        # initialize variance as the overall residual series variance
        vari[0] = np.var(resi, axis=0)
        for v in range(size-1):
            vari[v+1] += omega
            for i in alpha.size:
                # reduce order if necessary
                if v-i-1 >= 0:
                    vari[v] += alpha[i] * np.power(resi[v-i-1], 2)
            for j in beta.size:
                # reduce order if necessary
                if v-j-1 >= 0:
                    vari[v] += beta[j] * vari[v-j-1]
        return vari
    
        
    def optimizeParameters(self, resi):
        theta0 = (0.01, np.array([0.1]), np.array([0.1]))
        
        res = fmin(costFunc(resi, GARCH(resi, theta)), theta0)
        optTheta = res[0]
        
    
g = GARCH(1, 2, 3)    
print(g.prepareData())    
