#!/usr/bin/python3

import numpy as np
import pandas as pd
from Preprocess import Preprocess
import Postprocess as post

import plotly.offline as po
import plotly.graph_objs as go

preprocess = Preprocess(data="dividend")
daily_price = preprocess.retrieve_open_close()
dates = daily_price.index.values
start_date = dates[0]
end_date = dates[len(dates)-1]
index_series = preprocess.retrieve_benchmark("snp500", dates=[start_date, end_date])
beta = post.compute_beta(index_series, daily_price)
risk_free_return = 0
market_return = preprocess.compute_benchmark("snp500")
beta["reqRet"] = post.compute_required_return(risk_free_return, market_return, beta)
dividend_df = preprocess.retrieve_dividends()
growth = post.compute_dividend_growth(dividend_df)
dividend = post.compute_average_dividend(dividend_df)
trade_price = daily_price.iloc[len(dates)-1].transpose().to_frame(name="trade_price")
summary = pd.concat([beta["reqRet"], growth, dividend, trade_price], axis=1, join='inner')
summary["ddm"] = np.divide(summary["dividend"], np.subtract(summary["reqRet"], summary["growth"]))  # dividend discount
print(summary)


group = go.Scatter(x=summary["ddm"].values, y=summary["trade_price"].values,
                   name="test",
                   text=summary.index.values,
                   mode='markers',
                   marker=dict(size=10, color='blue',
                               line=dict(width=1, color='#EEEEEE')
                               )
                   )
data = [group]

po.plot(data, filename="/home/meng/Projects/ResultArchive/Equity_Evaluation.html")
