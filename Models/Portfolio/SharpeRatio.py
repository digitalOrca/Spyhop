#!/usr/bin/python3

"""PortfolioOptimization.py
Description:
    compute the estimated overall return and return variance of portfolios
    and optimize the assignment of capital in different assets
"""

import numpy as np
import pandas as pd
from Preprocess import Preprocess
import matplotlib.pyplot as plt


class SharpeRatio:

    """constructor
    """
    def __init__(self, asset, risk_free=0):
        self.preprocess = Preprocess(data='open_close')
        self.asset = asset
        self.risk_free = risk_free
        self.covariance = None  # type: pd.DataFrame
        self.mean = None  #pd.Series(index=asset)
        self.max_sharpe_comp = None  # maximum sharpe portfolio composition
        self.min_vol_comp = None  # minimum volatility portfolio composition

    """
        Description:
            compute the return covariance matrix for the items in the portfolio
            and the estimated(mean) return of each item
        Output:
            covariance: covariance matrix
            mean: mean daily return
    """
    def computeCovarMean(self):  # correlation matrix
        if self.covariance is None or self.mean is None:  # avoid duplicate query

            asset_data = self.preprocess.retrieve_open_close()[self.asset]
            daily_change = np.subtract(np.divide(asset_data.xs("close", level="field", axis=1),
                                                 asset_data.xs("open", level="field", axis=1)), 1)
            #print(stock_change)
            #daily_change = self.preprocess.get_data()[self.asset].pct_change()

            self.covariance = daily_change.cov()
            self.mean = daily_change.mean().subtract(self.risk_free/252)
        return self.covariance, self.mean

    """
        Description:
            evaluate a given portfolio and compute its overall return and volatility(standard deviation)
        Input:
            portfolio: portfolio to be evaluated as a DataFrame
    """
    def evaluatePortfolio(self, portfolio):
        weights = portfolio.values
        cov, mean = self.computeCovarMean()
        portfolio_return = np.multiply(weights, mean).sum()*252  # annualized return
        portfolio_stdev = np.sqrt(np.dot(weights, np.dot(cov, weights[np.newaxis].T)))*np.sqrt(252)
        return portfolio_return, portfolio_stdev

    """
        Description:
            using random search to find return and volatility of various portfolio composition
        Input:
            iters: number of iteration for the search
    """
    def searchReturnFrontier(self, iters):
        results = np.zeros((3, iters))
        compositions = {}
        for i in range(iters):
            w = np.random.random(len(self.asset))
            w /= np.sum(w)
            random_portfolio = pd.Series(w, index=self.asset)
            compositions[i] = random_portfolio
            ret, stdev = self.evaluatePortfolio(random_portfolio)
            results[0, i] = ret
            results[1, i] = stdev
            results[2, i] = ret / stdev
            print("evaluate portfolio:", i, " ret:", ret, "stdev:", stdev)
        results_frame = pd.DataFrame(results.T, columns=['ret', 'stdev', 'sharpe'])
        plt.scatter(results_frame.stdev, results_frame.ret, c=results_frame.sharpe, cmap='RdYlBu')
        plt.colorbar()

        max_sharpe_index = results_frame['sharpe'].idxmax()
        max_sharpe_port = results_frame.iloc[max_sharpe_index]
        self.max_sharpe_comp = compositions[max_sharpe_index]
        min_vol_index = results_frame['stdev'].idxmin()
        min_vol_port = results_frame.iloc[min_vol_index]
        self.min_vol_comp = compositions[min_vol_index]
        print("==========Stock Stats==========")
        print(self.mean)
        print("==========Maximum Sharpe Ratio Portfolio==========")
        print("Sharpe: ", results_frame['sharpe'].iloc[max_sharpe_index])
        print(self.max_sharpe_comp)
        print("==========Minimum Volatility Portfolio==========")
        print("Sharpe: ", results_frame['sharpe'].iloc[min_vol_index])
        print(self.min_vol_comp)
        # plot red star to highlight position of portfolio with highest Sharpe Ratio
        plt.scatter(max_sharpe_port[1], max_sharpe_port[0], marker=(5, 1, 0), color='r', s=250)
        # plot green star to highlight position of minimum variance portfolio
        plt.scatter(min_vol_port[1], min_vol_port[0], marker=(5, 1, 0), color='g', s=250)
        plt.show()


if __name__ == "__main__":
    stocks = ["NVDA", "AMZN", "GS", "ABT"]
    sr = SharpeRatio(stocks)
    sr.searchReturnFrontier(50000)
