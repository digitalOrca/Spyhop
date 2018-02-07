#!/usr/bin/python3

# DRAFT, DETAILS TO BE WORKED IN NOTEBOOK FIRST

import plotly.offline as po
import plotly.graph_objs as go

layout = go.Layout()

updatemenus=list([
    dict(
        buttons=list([
            dict(
                args=['type', 'surface'],
                label='3D Surface',
                method='restyle'
            ),
            dict(
                args=['type', 'heatmap'],
                label='Heatmap',
                method='restyle'
            )
        ]),
        direction = 'down',
        pad = {'r': 10, 't': 10},
        showactive = True,
        x = 0.1,
        xanchor = 'left',
        y = 1.1,
        yanchor = 'top'
    ),
])

layout['updatemenus'] = updatemenus

data = [1,2,3,4,5]

fig = dict(data=data, layout=layout)

po.plot(fig, filename='/home/meng/Projects/ResultArchive/FundamentalRatios.html')