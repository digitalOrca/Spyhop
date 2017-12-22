#!/usr/bin/python3

import numpy as np
import pandas as pd
from DBUtils import DBConnect
import matplotlib.pyplot as plt

db = DBConnect()

covariance, mean = None, None


def buildPortfolio(position):
    portfolio = pd.Series(position, index=position.keys())
    portfolio = portfolio/portfolio.sum()
    return portfolio


def computeCovarMean(portfolio):  # actually correlation matrix TODO:CONSIDER WHETHER INCLUDE RISK FREE RETURN HERE
    global covariance, mean
    if covariance is None and mean is not None:
        return covariance, mean
    date_query = "SELECT DISTINCT date FROM open_close ORDER BY date ASC"
    dates = db.query(date_query, index=None)["date"].astype('category')
    symbols = portfolio.index.values
    all_series = pd.DataFrame(index=dates, columns=symbols)
    mean = pd.Series(index=portfolio.index)  # initialize mean series
    for symbol in symbols:
        query = "SELECT date, symbol, lastclose, open FROM open_close WHERE symbol='%s' ORDER BY date ASC" % symbol
        series = db.query(query, index='date')
        # daily price change
        all_series[symbol] = (series[['lastclose', 'open']].mean(axis=1, numeric_only=True)).pct_change()
        mean.loc[symbol] = all_series[symbol].mean()
    covariance = all_series.cov()
    return covariance, mean


def evaluatePortfolio(portfolio):  # TODO:CONSIDER WHETHER INCLUDE RISK FREE RETURN HERE
    weights = portfolio.values
    cov, mean = computeCovarMean(portfolio)
    portfolio_return = np.multiply(weights, mean).sum()*252  # annualized return
    portfolio_stdev = np.sqrt(np.dot(weights, np.dot(cov, weights[np.newaxis].T)))*np.sqrt(252)
    return portfolio_return, portfolio_stdev


def randomPorfolioGenerator(position, iters):
    results = np.zeros((3, iters))
    for i in range(iters):
        w = np.random.random(len(position))
        w /= np.sum(w)
        randomPortfolio = pd.Series(w, index=position.keys())
        ret, stdev = evaluatePortfolio(randomPortfolio)
        results[0, i] = ret
        results[1, i] = stdev
        results[2, i] = ret / stdev
        print("evaluate portfolio:", i, " ret:", ret, "stdev:", stdev)
    results_frame = pd.DataFrame(results.T, columns=['ret', 'stdev', 'sharpe'])
    plt.scatter(results_frame.stdev, results_frame.ret, c=results_frame.sharpe, cmap='RdYlBu')
    plt.colorbar()
    plt.show()
    # plot red star to highlight position of portfolio with highest Sharpe Ratio
    #plt.scatter(max_sharpe_port[1], max_sharpe_port[0], marker=(5, 1, 0), color='r', s=1000)
    # plot green star to highlight position of minimum variance portfolio
    #plt.scatter(min_vol_port[1], min_vol_port[0], marker=(5, 1, 0), color='g', s=1000)




ps = {"MMM":  1000,
       "T":    100,
       "GS":   800
       }

#pf = buildPortfolio(ps)
#evaluatePortfolio(pf)

randomPorfolioGenerator(ps, 5000)
