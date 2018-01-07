#!/usr/bin/python3

from DBUtils import DBConnect
import numpy as np
import pandas as pd
from scipy import stats
import datetime
from Preprocess import Preprocess
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity

class SectorNorm():
    
    def __init__(self, lag=30):
        self.db = DBConnect()
        self.preprocess = Preprocess(data="fundamental_ratios", lag=lag)
        
        
    def computeAlpha(self):
        self.preprocess.retrieve_fundamental_ratios(lag=True)  # set fr dates
        start_date = self.preprocess.frdate

        ArDf = self.preprocess.compute_return(split=False)
        benchmark = self.preprocess.compute_benchmark("snp500")
        ArDf = ArDf.dropna(axis=0, how='any')  # prevent arithmetic error
        ArDf["return"] = np.log(np.divide(ArDf["return"], benchmark))
        return ArDf


    def computeSectorReturnProbability(self, ArDf):
        symbolSector = self.preprocess.retrieve_symbol_sector()
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
            print(sector, probablity)
        sector_probability = sector_probability.to_frame("sector")
        return sector_probability

    def visualizeSectorKDE(self, ArDf):
        symbolSector = self.preprocess.retrieve_symbol_sector()
        sectorReturn = pd.concat([symbolSector, ArDf], axis=1, join="inner")
        for sector in sectorReturn["sector"].unique():
            symbols = sectorReturn[sectorReturn["sector"] == sector].index
            sector_stats = ArDf.loc[symbols.values]["return"].sort_values()[:, np.newaxis]
            kde = KernelDensity(kernel='gaussian', bandwidth=0.01)
            kde.fit(sector_stats)
            log_dens = kde.score_samples(sector_stats)
            plt.plot(sector_stats, np.exp(log_dens), label=sector)
        plt.axis([-0.5, 0.5, 0, 15])
        plt.legend(prop={'size': 10}, loc=4)
        today = datetime.date.today().isoformat()
        plt.title(today)
        filename = "/home/meng/Projects/ResultArchive/SectorNorm_" + today
        plt.savefig(filename)
        plt.show()


if __name__ == "__main__":
    s = SectorNorm()
    ar = s.computeAlpha()
    #s.computeSectorReturnProbability(ar)
    s.visualizeSectorKDE(ar)
