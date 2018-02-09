#!/usr/bin/python3

import numpy as np
from Preprocess import Preprocess
import Postprocess as post


class InformationRatio:

    def __init__(self, benchmark="snp500"):
        self.benchmark = benchmark
        self.preprocess = Preprocess()
        self.alpha = None
        self.index = None

    def computeInformationRatio(self, portfolio):
        returns = self.preprocess.retrieve_return()
        index = self.preprocess.retrieve_benchmark_change("snp500")
        if self.alpha is None:
            alpha = post.compute_alpha(index, returns).loc[portfolio.keys()]["alpha"].values
            self.alpha = alpha
        else:
            alpha = self.alpha
        #print("alpha:", alpha)
        weight = np.array(list(portfolio.values()))
        #print("weight", weight)
        portfolio_return = np.sum(np.multiply(alpha, weight))
        #print("portfolio return", portfolio_return)
        volatility = np.std(alpha)
        #print("volatility", volatility)
        if self.index is None:
            index = self.preprocess.retrieve_benchmark_change(self.benchmark) - 1
            self.index = index
        else:
            index = self.index
        #print("benchmark", index)
        information_ratio = (portfolio_return - index) / volatility
        return information_ratio


if __name__ == "__main__":
    ir = InformationRatio()
    portfolio = {
                 "HES": 0.1,
                 "FTI": 0.2,
                 "FCX": 0.3,
                 "WB": 0.4
                 }
    result = ir.computeInformationRatio(portfolio)
    print("Information Ratio:", result)
