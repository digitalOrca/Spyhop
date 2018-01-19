#!/usr/bin/python3

import numpy as np
import pandas as pd
from Preprocess import Preprocess


def compute_alpha(benchmark):
    preprocess = Preprocess(data="fundamental_ratios")
    preprocess.retrieve_fundamental_ratios(lag=True)  # set fr dates
    returns = preprocess.compute_return(split=False)
    index = preprocess.compute_benchmark(benchmark)
    returns["alpha"] = np.subtract(returns["return"], index)
    return returns["alpha"].to_frame()


def compute_beta( benchmark):
    preprocess = Preprocess(data="fundamental_ratios")
    index = preprocess.retrieve_benchmark(benchmark)
    stock = preprocess.retrieve_open_close()
    index_change = index[benchmark].pct_change()
    stock_change = stock.pct_change()
    for col in stock_change:
        nan_count = stock_change[col].isnull().sum()
        if nan_count > 3:  # remove columns with insufficient data
            stock_change.drop([col], axis=1, inplace=True)
    all_change = pd.concat([index_change, stock_change], axis=1, join='inner').fillna(0)
    volatility = pd.DataFrame(index=all_change.columns, columns=["beta"], dtype=np.float32)
    volatility.drop([benchmark], axis=0, inplace=True)  # remove benchmark column

    for col in all_change:
        b = all_change[benchmark].values
        with np.errstate(invalid='ignore'):  # ignore runtime warning in np.corrcoef due to numeric instability
            if col != benchmark:
                a = all_change[col].values
                np.corrcoef(a, b)
                beta = np.multiply(np.corrcoef(a, b), np.divide(np.std(a), np.std(b)))[0, 1]
                volatility["beta"].loc[col] = beta
    volatility.dropna(axis=0, how='any', inplace=True)
    return volatility