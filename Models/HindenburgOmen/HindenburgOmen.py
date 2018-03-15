#!/usr/bin/python3

"""HindenburgOmen.py
Description:
    Utility for finding Hindenburg Omen
"""

import numpy as np
import pandas as pd
from Preprocess import Preprocess


class HindenburgOmen:

    """constructor
    """
    def __init__(self):
        self.preprocess = Preprocess(lag=80)
        self.daily_price = None

    """benchmarkCriteria
        Description:
            test the condition that current benchmark is higher than 50 trade-days ago
    """
    def benchmark_criteria(self):
        benchmark = self.preprocess.retrieve_benchmark("snp500")
        latest = benchmark.iloc[-1]["open"]
        prev50 = benchmark.iloc[-50]["open"]
        return latest > prev50

    """benchmarkCriteria
        Description:
            get recent and high/low price for all stocks
    """
    def compute_price_high_low(self):
        if self.daily_price is None:
            self.daily_price = self.preprocess.retrieve_open_close()
        recent_average = self.daily_price.iloc[-1].xs("average", level="field", axis=0).transpose().to_frame(name="recent")
        high_low = self.preprocess.retrieve_high_low()
        return recent_average, high_low

    """computeRatio
        Description:
            convert current price level to ratio with respect to high/low data
    """
    @staticmethod
    def compute_ratio(recent_average, high_low):
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
        return ratios

    """highLowCriteria
        Description:
            test the condition that new high and new low is above threshold, new high is not too dominant
    """
    def high_low_criteria(self, highlow52ratio=0.028):
        # highlow52ratio: The daily number of new 52-week highs and new 52-week lows are both greater than a threshold
        r, hl = self.compute_price_high_low()
        ratios = rh.compute_ratio(r, hl)
        total = len(ratios.index)
        high52count = len(ratios[ratios["ratio52"] > 0.999].index)
        low52count = len(ratios[ratios["ratio52"] < 0.001].index)
        high52ratio = high52count / total
        low52ratio = low52count / total
        print(">>>52-week-high:", high52ratio, "52-week-low:", low52ratio)
        return high52ratio > highlow52ratio and low52ratio > highlow52ratio and high52ratio/low52ratio < 2

    """mclCriteria
        Description:
            test the condition that 19-day McClellan Oscillator is below the 39-day McClellan Oscillator
    """
    def mcl_criteria(self):  # McClellan Oscillator
        if self.daily_price is None:
            self.daily_price = self.preprocess.retrieve_open_close()
        dif_series = []
        for i in range(-2, -41, -1):  # last day's closing price is not collected, so, forward shift 1 day
            open = self.daily_price.iloc[i].xs("open", level="field", axis=0)
            close = self.daily_price.iloc[i].xs("close", level="field", axis=0)
            change = (close-open).values
            upw = sum(i > 0 for i in change)
            dpw = sum(i < 0 for i in change)
            dif_series.append(upw - dpw)
        ad = sum(dif_series[:19])/19
        bd = sum(dif_series[:39])/39
        print(">>>AD(19):", ad)
        print(">>>BD(39)", bd)
        mcl = ad - bd
        return mcl < 0


"""Main"""
if __name__ == "__main__":
    rh = HindenburgOmen()
    c1 = rh.high_low_criteria(highlow52ratio=0.028)
    c2 = rh.benchmark_criteria()
    c3 = rh.mcl_criteria()
    print("*New High, New Low Criteria (>2.8%, new_high<2*new_low)", c1)
    print("*Benchmark 50-day Criteria (rising)", c2)
    print("*McClellan Oscillator (<0)", c3)



