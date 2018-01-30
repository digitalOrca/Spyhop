#!/usr/bin/python3

import numpy as np
import pandas as pd
from Preprocess import Preprocess
import Postprocess as post

import plotly.offline as po
import plotly.graph_objs as go

preprocess = Preprocess()
daily_price = preprocess.retrieve_open_close()
dates = daily_price.index.values
start_date = dates[0]
end_date = dates[len(dates)-1]
index_series = preprocess.retrieve_benchmark("snp500", dates=[start_date, end_date])
beta = post.compute_beta(index_series, daily_price)
risk_free_return = 0
market_return = preprocess.compute_benchmark("snp500")
beta["reqRet"] = post.compute_required_return(risk_free_return, market_return, beta)
print("retrieve dividends...")
dividend_df = preprocess.retrieve_dividends()
growth = post.compute_dividend_growth(dividend_df)
dividend = post.compute_average_dividend(dividend_df)
print("retrieve prices...")
trade_price = daily_price.iloc[len(dates)-1].xs("average", level="field", axis=0).transpose().to_frame(name="trade_price")
print("retrieve sectors...")
symbolSector = preprocess.retrieve_symbol_sector()
sectors = symbolSector["sector"].unique()
print("retrieve market caps...")
mktcap = preprocess.retrieve_mkt_caps(symbolSector.index).dropna(axis=0, how='any')
mktcap["size"] = pd.Series(data="small", index=mktcap.index)
mktcap.loc[mktcap["mktcap"] > 2000, "size"] = "medium"
mktcap.loc[mktcap["mktcap"] > 10000, "size"] = "large"

print("computing summary...")
summary = pd.concat([beta["reqRet"], growth, dividend, trade_price, symbolSector, mktcap], axis=1, join='inner')
summary["ddm"] = np.divide(summary["dividend"], np.subtract(summary["reqRet"], summary["growth"]))  # dividend discount
print(summary)

# define sector color
colors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231', '#911eb4',
          '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080', '#e6beff']
sector_colors = dict(zip(sectors, colors))

# marker size
cap_sizes = {"large": 8, "medium": 5, "small": 3}

data = []
for sector in sectors:
    sector_set = summary[summary["sector"] == sector]
    color = sector_colors[sector]
    for cap in ["large", "medium", "small"]:
        subset = sector_set[sector_set["size"] == cap]
        group = go.Scatter(x=subset["ddm"].values, y=subset["trade_price"].values,
                           name=sector,
                           text=summary.index.values,
                           mode='markers',
                           marker=dict(size=cap_sizes[cap], color=color)
                           )
        data.append(group)


layout = go.Layout(
    xaxis=dict(
        type='log',
        autorange=True
    ),
    yaxis=dict(
        type='log',
        autorange=True
    )
)

fig = go.Figure(data=data, layout=layout)
po.plot(fig, filename="/home/meng/Projects/ResultArchive/Equity_Evaluation.html")
