#!/usr/bin/python3

import datetime
import numpy as np
import pandas as pd
from Preprocess import Preprocess
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity


class RecentHigh:

    def __init__(self):
        self.preprocess = Preprocess()

    def prepData(self, tolerance=3):
        daily_price = self.preprocess.get_data()
        recent_average = daily_price.iloc[-1].xs("average", level="field", axis=0).transpose().to_frame(name="recent")
        high_low = self.preprocess.retrieve_high_low()
        return recent_average, high_low

    def computeRatio(self, recent_average, high_low):
        symbols = pd.concat([recent_average, high_low], axis=1, join='inner')  # type: pd.DataFrame
        ratios = pd.DataFrame(index=symbols.index)  # type: pd.DataFrame
        for reference in [13, 26, 52]:
            high, low, column = "", "", ""
            if reference == 13:
                low, high, column = "low13", "high13", "ratio13"
            elif reference == 26:
                low, high, column = "low26", "high26", "ratio26"
            elif reference == 52:
                low, high, column = "low52", "high52", "ratio52"
            columns = [low, high]
            processed = pd.concat([high_low[columns], recent_average], axis=1, join='inner')  # type: pd.DataFrame
            ratios[column] = np.clip(np.divide(np.subtract(processed["recent"], processed[low]),
                                               np.subtract(processed[high], processed[low])),
                                     0, 1)
            ratios[column] = ratios[column].fillna(ratios[column].mean())  # fill missing values
        ratios["sum"] = ratios.mean(axis=1, skipna=True)
        return ratios

    def visualizeDistribution(self, ratios):
        colors = ['red', 'green', 'blue', 'black']
        for col in ratios:
            if col != 'sum':
                sorted_ratios = np.sort(ratios[col].values)
                plt.plot([i for i in range(len(ratios))], sorted_ratios, label=col)
        plt.axis([0, len(ratios), 0, 1])
        plt.legend(prop={'size': 10}, loc=4)
        today = datetime.date.today().isoformat()
        plt.title(today)
        filename = "/home/meng/Projects/ResultArchive/RecentHigh_" + today
        plt.savefig(filename)
        plt.show()

    def visualizeKDE(self, ratios):
        colors = ['red', 'green', 'blue']
        for col in ratios:
            if col != 'sum':
                x = ratios[col].sort_values()[:, np.newaxis]
                kde = KernelDensity(kernel='gaussian', bandwidth=0.1)
                kde.fit(x)
                log_dens = kde.score_samples(x)
                plt.plot(x, np.exp(log_dens), label=col)
        plt.legend(prop={'size': 10}, loc=4)
        today = datetime.date.today().isoformat()
        plt.title(today)
        filename = "/home/meng/Projects/ResultArchive/RecentHigh_" + today
        plt.savefig(filename)
        plt.show()


if __name__ == "__main__":
    rh = RecentHigh()
    r, hl = rh.prepData()
    print(r)
    print(hl)
    ratios = rh.computeRatio(r, hl)
    #rh.visualizeDistribution(ratios)
    rh.visualizeKDE(ratios)
