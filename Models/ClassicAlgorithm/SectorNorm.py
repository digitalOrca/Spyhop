#!/usr/bin/python3

from DBUtils import DBConnect
import numpy as np
import pandas as pd
from scipy import stats
from datetime import date
from datetime import timedelta
from Preprocess import Preprocess

class SectorNorm():
    
    def __init__(self, lag=30, retMax=0.25, retMin=-0.25):
        self.db = DBConnect()
        self.retMax = retMax
        self.retMin = retMin
        self.preprocess = Preprocess(data="fundamental_ratios", lag=lag)
        
        
    def computeSectorReturnProbability(self):
        symbolSector = self.db.query("SELECT symbol, sector FROM security")
        self.preprocess._retrieveFundamentalRatios(lag=True)
        start_date = self.preprocess.frdate
        ArDf = self.preprocess.retrieveAR()
        ArDf = ArDf.dropna(axis=0, how='any') # prevent arithmetic error TODO: CONSIDER USING BENCHMARK
        ArDf["return"] = (ArDf["end"]/ArDf["start"])-1.0
        # remove legacy columns
        ArDf.drop(['start', 'end'], axis=1, inplace=True)
        # remove outlier returns
        bull = ArDf[ArDf['return'] > self.retMax]
        ArDf.drop(bull.index, inplace=True)
        bear = ArDf[ArDf['return'] < self.retMin]
        ArDf.drop(bear.index, inplace=True)
        sectorReturn = pd.concat([symbolSector, ArDf], axis=1, join="inner")
        
        sector_probability = pd.Series(index=sectorReturn.index)
        for sector in sectorReturn["sector"].unique():
            mask = sectorReturn["sector"]==sector
            returnSeries = sectorReturn[sectorReturn["sector"]==sector]["return"].values
            mean = np.mean(returnSeries)
            stdev = np.std(returnSeries)
            z_value = mean / stdev
            probablity = stats.norm.cdf(z_value)
            sector_probability[mask] = probablity
        sector_probability = sector_probability.to_frame("sector")
        return sector_probability

"""
s = SectorNorm()
print(s.computeSectorReturnProbability())
"""
