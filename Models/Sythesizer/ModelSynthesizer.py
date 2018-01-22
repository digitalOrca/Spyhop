#!/use/bin/python3

import pandas as pd
from Preprocess import Preprocess
import Postprocess as post
import plotly.offline as po
import plotly.graph_objs as go


preprocess = Preprocess(data="open_close")
benchmark = "snp500"

index_change = preprocess.compute_benchmark(benchmark)
returns = preprocess.compute_return(split=False)
alphas = post.compute_alpha(index_change, returns)

index_series = preprocess.retrieve_benchmark(benchmark)
daily_price = preprocess.retrieve_open_close()
betas = post.compute_beta(index_series, daily_price)

alpha_beta = pd.concat([alphas, betas], axis=1, join='inner')

symbolSector = preprocess.retrieve_symbol_sector()
alpha_beta_sector = pd.concat([alpha_beta, symbolSector], axis=1, join='inner')  # type: pd.DataFrame
mktcap = preprocess.retrieve_mkt_caps(alpha_beta_sector.index).dropna(axis=0, how='any')
mktcap["size"] = pd.Series(data="small", index=mktcap.index)
mktcap.loc[mktcap["mktcap"] > 2000, "size"] = "medium"
mktcap.loc[mktcap["mktcap"] > 10000, "size"] = "large"
summary = pd.concat([alpha_beta_sector, mktcap["size"]], axis=1, join='inner')  # type: pd.DataFrame

# define sector color
colors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231', '#911eb4',
          '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080', '#e6beff']
sector_colors = dict(zip(summary["sector"].unique(), colors))
cap_sizes = {"large": 8, "medium": 5, "small": 3}
data = []
size_tiers = summary["size"].unique()
for sector in summary["sector"].unique():
    color = sector_colors[sector]
    sector_set = summary[summary["sector"] == sector]
    for cap in ["large", "medium", "small"]:
        subset = sector_set[sector_set["size"] == cap]
        group = go.Scatter(x=subset["alpha"], y=subset["beta"],
                           name=sector+"("+cap+")",
                           text=subset.index,
                           mode='markers',
                           marker=dict(size=cap_sizes[cap], color=color,
                                       line=dict(width=1, color='rgb(0, 0, 0)')
                                       )
                           )
        data.append(group)
po.plot(data, filename='/home/meng/Projects/ResultArchive/share.html')
