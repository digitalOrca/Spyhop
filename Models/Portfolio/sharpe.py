#!/usr/bin/python3

import numpy as np
import pandas as pd
from DBUtils import DBConnect

db = DBConnect()


def buildPortfolio(position):
    portfolio = pd.Series(position, index=position.keys())
    portfolio = portfolio/portfolio.sum()
    return portfolio


def computeCovarMean(portfolio):  # actually correlation matrix TODO:CONSIDER WHETHER INCLUDE RISK FREE RETURN HERE
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
    for i in range(iters):
        w = np.random.random(len(position))
        w /= np.sum(w)
        randomPortfolio = pd.Series(w, index=position.keys())
        ret, stdev = evaluatePortfolio(randomPortfolio)
        # TODO: DO SOME PLOTTING TO FIND RETURN FRONTIER


ps = {"MMM":  1000,
       "T":    100,
       "GS":   800
       }

pf = buildPortfolio(ps)
evaluatePortfolio(pf)


weights = np.random.random(4)
print(weights.sum())