#!/usr/bin/python3

import pandas as pd
from Preprocess import Preprocess
import Postprocess as post

import plotly.offline as po
import plotly.graph_objs as go


preprocess = Preprocess(data="open_close", lag=45)
benchmark = "snp500"

# pre-load all data
print("retrieving open_close data...")
daily_price = preprocess.retrieve_open_close()
dates = daily_price.index.values
duration = len(daily_price)
# sectors
print("retrieving symbol sectors data...")
symbolSector = preprocess.retrieve_symbol_sector()
sectors = symbolSector["sector"].unique()
# load market caps
print("retrieving market caps data...")
mktcap = preprocess.retrieve_mkt_caps(daily_price.columns.get_level_values("symbol").values).dropna(axis=0, how='any')
mktcap["size"] = pd.Series(data="small", index=mktcap.index)
mktcap.loc[mktcap["mktcap"] > 2000, "size"] = "medium"
mktcap.loc[mktcap["mktcap"] > 10000, "size"] = "large"
# marker size
cap_sizes = {"large": 8, "medium": 5, "small": 3}
size_tiers = cap_sizes.keys()
# define sector color
colors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231', '#911eb4',
          '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080', '#e6beff']
sector_colors = dict(zip(sectors, colors))

steps = 10
transition = 1000

# make figure
figure = {
    'data': [],
    'layout': {},
    'frames': []
}

# fill in most of layout
figure['layout']['xaxis'] = {'title': 'Alpha', 'range': [-0.5, 0.5]}
figure['layout']['yaxis'] = {'title': 'Beta', 'range': [-5, 5]}
figure['layout']['hovermode'] = 'closest'
figure['layout']['sliders'] = {
    'args': [
        'transition', {
            'duration': 400,
            'easing': 'cubic-in-out'
        }
    ],
    'initialValue': 0,
    'plotlycommand': 'animate',
    'values': range(steps),
    'visible': True
}

figure['layout']['updatemenus'] = [
    {
        'buttons': [
            {
                'args': [None, {'frame': {'duration': 500, 'redraw': False},
                                'fromcurrent': True, 'transition': {'duration': 300, 'easing': 'quadratic-in-out'}}],
                'label': 'Play',
                'method': 'animate'
            },
            {
                'args': [[None], {'frame': {'duration': 0, 'redraw': False}, 'mode': 'immediate',
                                  'transition': {'duration': 0}}],
                'label': 'Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 10, 't': 87},
        'showactive': False,
        'type': 'buttons',
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
    }
]

sliders_dict = {
    'active': 0,
    'yanchor': 'top',
    'xanchor': 'left',
    'currentvalue': {
        'font': {'size': 20},
        'prefix': 'End Date:',
        'visible': True,
        'xanchor': 'right'
    },
    'transition': {'duration': transition, 'easing': 'cubic-in-out'},
    'pad': {'b': 10, 't': 50},
    'len': 0.9,
    'x': 0.1,
    'y': 0,
    'steps': []
}

summaries = []
for i in range(steps):
    print("summarizing step:", i)
    start = i
    end = -steps + 1 + i if (steps - i > 1) else duration
    price_frame = daily_price.iloc[start: end]
    start_date = dates[start]
    end_index = duration - steps + i if end < 0 else duration - 1
    end_date = dates[end_index]
    return_frame = preprocess.compute_return(split=False, dates=[start_date, end_date])

    index_change = preprocess.compute_benchmark(benchmark, dates=[start_date, end_date])
    alpha = post.compute_alpha(index_change, return_frame)

    index_series = preprocess.retrieve_benchmark(benchmark, dates=[start_date, end_date])
    beta = post.compute_beta(index_series, price_frame)

    alpha_beta = pd.concat([alpha, beta], axis=1, join='inner')
    alpha_beta_sector = pd.concat([alpha_beta, symbolSector], axis=1, join='inner')  # type: pd.DataFrame
    summary = pd.concat([alpha_beta_sector, mktcap["size"]], axis=1, join='inner')
    summaries.append(summary)

# process summaries for index alignment
valid_index = summaries[0].index.values
i = 1  # keep track of summaries index
for summary in summaries[1:]:
    print("post-processing summaries:", i)
    drop_list = list(set(summary.index.values) - set(valid_index))
    append_list = list(set(valid_index) - set(summary.index.values))
    summary.drop(labels=drop_list, axis=0, inplace=True)
    summary = summary.append(summaries[i - 1].reindex(append_list))  # loc deprecated by reindex
    summary = summary.reindex(valid_index)  # guarantee index order
    summaries[i] = summary
    i += 1

i = 0
for summary in summaries:
    print("Framing summary:", i)
    frame = {'data': [], 'name': str(i)}
    for sector in sectors:
        color = sector_colors[sector]
        sector_set = summary[summary["sector"] == sector]
        for cap in ["large", "medium", "small"]:
            subset = sector_set[sector_set["size"] == cap]
            group = go.Scatter(x=subset["alpha"], y=subset["beta"],
                               name=sector + "(" + cap + ")",
                               text=subset.index,
                               mode='markers',
                               marker=dict(size=cap_sizes[cap], color=color,
                                           opacity=0.75
                                           #line=dict(width=1, color='#EEEEEE')
                                           )
                               )
            frame['data'].append(group)
            if i == 0:  # make data
                figure['data'].append(group)
    figure['frames'].append(frame)
    slider_step = {'args': [[str(i)],
                            {'frame': {'duration': transition, 'redraw': False},
                             # 'mode': 'immediate',
                             'transition': {'duration': transition}}
                            ],
                   'label': str(i),
                   'method': 'animate'}
    sliders_dict['steps'].append(slider_step)
    i += 1
figure['layout']['sliders'] = [sliders_dict]
po.plot(figure, filename="/home/meng/Projects/ResultArchive/Alpha_Beta_Movement.html")
