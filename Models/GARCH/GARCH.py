#!/usr/bin/python3

import numpy as np
import pandas as pd
from scipy.optimize import fmin
from Preprocess import Preprocess
    
class GARCH:
    
    def __init__(self):
        #self.omega = omega
        #self.alpha = alpha
        #self.beta = beta
        self.preprocess = Preprocess(data='bars')
        self.resi = None
        self.vari = None
        
    def prepareData(self):
        rawData = self.preprocess.get_data(dset="all")
        rawData["date"] = rawData["timestamp"].apply(lambda x: x.date())
        rawData["time"] = rawData["timestamp"].apply(lambda x: x.time())
        symbols = (rawData.index).unique().values
        dates = sorted((rawData["date"]).unique())
        formatedData = {}
        count = 0
        for symbol in symbols:
            count += 1
            print(count, ", process for symbol:", symbol)
            symbolData = rawData[rawData.index == symbol].copy()
            symbolDf = pd.DataFrame(index=dates, columns=["vari", "resi"])
            #compute change
            change = (symbolData["wap"].pct_change()).add(1)
            logChange = change.apply(lambda x: np.log(x))
            mu = logChange.mean()
            logChange = logChange.subtract(mu)
            logChange.iloc[0] = 0
            symbolData["change"] = logChange
            vari, resi = 0, 0
            for date in dates:
                series= symbolData[symbolData["date"]==date]["change"]
                v = series.var()
                r = series.mean()
                if not np.isnan(v):
                    vari = v
                if not np.isnan(r):
                    resi = r
                symbolDf.loc[date, "vari"] = vari
                symbolDf.loc[date, "resi"] = resi
                print("------>",date, "vari:", vari, "resi:", resi)
            
            try:
                formatedData[symbol] = symbolDf
                #TODO: TEST BLOCK
                theta0 = [0.01, 0.1, 0.1]
                result = fmin(func=self.costFunc, x0=theta0, args=(symbolDf["resi"],))
                print(result)
                #TODO: END TEST BLOCK
            except Exception as e:
                print(str(e))
        return formatedData
    
    def costFunc(self, theta, resi):
        vari = self.GARCH(theta, resi)
        return np.sum(np.add(np.divide(np.power(resi, 2), vari), np.log(2*np.pi*vari)))

    def GARCH(self, theta, resi):
        omega = theta[0]
        alpha = theta[1]
        beta = theta[2]
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
        for i in range(size-1):
            v = omega + alpha * np.power(resi[i], 2) + beta * v
            vari[i+1] = v
            #vari[v+1] += omega
            #for i in alpha.size:
            #    # reduce order if necessary
            #    if v-i-1 >= 0:
            #        vari[v+1] += alpha[i] * np.power(resi[v-i-1], 2)
            #for j in beta.size:
            #    # reduce order if necessary
            #    if v-j-1 >= 0:
            #        vari[v+1] += beta[j] * vari[v-j-1]
        return vari
    
        
    def optimizeParameters(self):
        formatedData = self.prepareData()
        theta0 = [0.01, 0.1, 0.1]
        optimal = {}
        for symbol in formatedData.keys():
            resi = formatedData[symbol]
            result = fmin(costFunc(resi, GARCH(resi, theta)), theta0)
            optimal[symbol] = result
            print(result)
    
g = GARCH()    
print(g.prepareData())   
