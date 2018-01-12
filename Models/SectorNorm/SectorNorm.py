#!/usr/bin/python3

from DBUtils import DBConnect
import numpy as np
import pandas as pd
from scipy import stats
import datetime
from Preprocess import Preprocess
import Postprocess as post
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity
from scipy import integrate


class SectorNorm:
    
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
            returnSeries = sectorReturn[sectorReturn["sector"] == sector]["return"].values
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
        sector_shown = [#"Consumer Services",
                        #"Public Utilities",
                        "Basic Industries",
                        #"Capital Goods",
                        #"Finance",
                        "Consumer Non-Durables",
                        "Technology",
                        #"Health Care",
                        "Energy",
                        #"Consumer Durables",
                        #"Miscellaneous",
                        "Transportation"]
        for sector in sectorReturn["sector"].unique():
            symbols = sectorReturn[sectorReturn["sector"] == sector].index
            sector_ret = ArDf.loc[symbols.values]["alpha"].sort_values()
            sector_stats = sector_ret[:, np.newaxis]
            kde = KernelDensity(kernel='gaussian', bandwidth=0.025)
            kde.fit(sector_stats)
            log_dens = kde.score_samples(sector_stats)
            print("{:25s}:".format(sector), integrate.trapz(np.exp(log_dens[sector_ret > 0]), sector_ret[sector_ret > 0]))
            if sector in sector_shown:
                plt.plot(sector_stats, np.exp(log_dens), label=sector)
        plt.axis([-0.5, 0.5, 0, 10])
        plt.legend(prop={'size': 10}, loc=4)
        today = datetime.date.today().isoformat()
        plt.title(today)
        filename = "/home/meng/Projects/ResultArchive/SectorNorm_" + today
        plt.savefig(filename)
        plt.show()


if __name__ == "__main__":
    s = SectorNorm()
    ar = post.compute_alpha("snp500")
    #s.computeSectorReturnProbability(ar)
    s.visualizeSectorKDE(ar)
