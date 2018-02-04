#!/usr/bin/python3

"""PortfolioOptimization.py
Description:
    compute the estimated overall return and return variance of portfolios
    and optimize the assignment of capital in different assets
"""

import numpy as np
import pandas as pd
from Preprocess import Preprocess
import plotly.graph_objs as go
import plotly.offline as po


class SharpeRatio:

    """constructor
    """
    def __init__(self, asset, risk_free=0):
        self.preprocess = Preprocess()
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
        labels = []
        for i in range(iters):
            w = np.random.random(len(self.asset))
            w /= np.sum(w)
            random_portfolio = pd.Series(w, index=self.asset)
            compositions[i] = random_portfolio
            labels.append(random_portfolio.to_string())
            ret, stdev = self.evaluatePortfolio(random_portfolio)
            results[0, i] = ret
            results[1, i] = stdev
            results[2, i] = ret / stdev
            print("evaluate portfolio:", i, " ret:", ret, "stdev:", stdev)
        results_frame = pd.DataFrame(results.T, columns=['ret', 'stdev', 'sharpe'])

        max_sharpe_index = results_frame['sharpe'].idxmax()
        min_vol_index = results_frame['stdev'].idxmin()
        markers = results_frame.iloc[[max_sharpe_index, min_vol_index]]
        return markers, labels, results_frame


if __name__ == "__main__":
    stocks = ["SSL", "CAH", "STX", "PCLN", "IT"]
    sr = SharpeRatio(stocks)
    markers, labels, result = sr.searchReturnFrontier(50000)

    dist = go.Scatter(x=result["stdev"], y=result["ret"],
                      name="all samples",
                      mode='markers',
                      marker=dict(
                          size=5,
                          color='#2E86C1',
                      ),
                      text=labels)

    highlight = go.Scatter(x=markers["stdev"], y=markers["ret"],
                           name="max sharpe, min volatility",
                           mode='markers',
                           marker=dict(
                               size=10,
                               color='#E74C3C',
                           ),
                           text=labels)

    data = [dist, highlight]

    layout = go.Layout(
        title='Portfolio Composition',
        hovermode='closest',
        xaxis=dict(
            title='Risk',
        ),
        yaxis=dict(
            title='Return',
        ),
        showlegend=False
    )

    fig = go.Figure(data=data, layout=layout)

    po.plot(fig, filename="/home/meng/Projects/ResultArchive/Portfolio_Sharpe.html")

