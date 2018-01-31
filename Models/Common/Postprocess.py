#!/usr/bin/python3

import numpy as np
import pandas as pd


def compute_alpha(index, returns):
    returns["alpha"] = np.subtract(returns["return"], index)
    return returns["alpha"].to_frame()


def compute_beta(index, daily_price):
    index_change = np.subtract(np.divide(index["close"], index["open"]), 1).to_frame(name="benchmark")
    stock_change = np.subtract(np.divide(daily_price.xs('close', level='field', axis=1),
                                         daily_price.xs('open', level='field', axis=1)), 1)
    for col in stock_change:
        nan_count = stock_change[col].isnull().sum()
        if nan_count > 3:  # remove columns with insufficient data
            stock_change.drop([col], axis=1, inplace=True)
    all_change = pd.concat([index_change, stock_change], axis=1, join='inner').fillna(0)
    volatility = pd.DataFrame(index=all_change.columns, columns=["beta"], dtype=np.float32)
    volatility.drop(["benchmark"], axis=0, inplace=True)  # remove benchmark column

    for col in all_change:
        b = all_change["benchmark"].values
        with np.errstate(invalid='ignore'):  # ignore runtime warning in np.corrcoef due to numeric instability
            if col != "benchmark":
                a = all_change[col].values
                np.corrcoef(a, b)
                beta = np.multiply(np.corrcoef(a, b), np.divide(np.std(a), np.std(b)))[0, 1]
                volatility["beta"].loc[col] = beta
    volatility.dropna(axis=0, how='any', inplace=True)
    return volatility


def compute_beta_new(index, daily_price):
    benchmark = index.columns.values[0]
    index_change = index.pct_change()
    stock_change = daily_price.pct_change()
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


def compute_required_return(ret_rf, ret_mkt, beta):
    req_ret = np.add(np.multiply(beta, (ret_mkt - ret_rf)), ret_rf)
    return req_ret


def compute_dividend_growth(dividends_df):
    prev_dividends = dividends_df["past_yr"]
    next_dividends = dividends_df["next_yr"]
    dividends_df["growth"] = np.multiply(np.subtract(next_dividends, prev_dividends), prev_dividends)
    return dividends_df["growth"].to_frame()


def compute_average_dividend(dividends_df):
    dividends_df["dividend"] = dividends_df[["past_yr", "next_yr"]].mean(axis=1)  # type:pd.DataFrame
    return dividends_df["dividend"].to_frame()
