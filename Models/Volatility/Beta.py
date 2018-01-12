#!/use/bin/python3

import numpy as np
import pandas as pd
from Preprocess import Preprocess
import Postprocess as post
from sklearn.neighbors import KernelDensity
import matplotlib.pyplot as plt
import mpld3
from mpld3 import plugins

class Beta:

    def __init__(self):
        self.preprocess = Preprocess(data='open_close')


    # make this per sector
    def visualize_beta_distribution(self, betas):
        sorted_beta = betas["beta"].sort_values()
        beta_stats = sorted_beta[:, np.newaxis]
        kde = KernelDensity(kernel='gaussian', bandwidth=0.025)
        kde.fit(beta_stats)
        log_dens = kde.score_samples(beta_stats)
        plt.plot(beta_stats, np.exp(log_dens))
        plt.show()


if __name__ == "__main__":
    sb = Beta()
    betas = post.compute_beta("snp500")
    alphas = post.compute_alpha("snp500")
    alpha_beta = pd.concat([alphas, betas], axis=1, join='inner')  # type: pd.DataFrame
    preprocess = Preprocess(data="open_close")
    symbolSector = preprocess.retrieve_symbol_sector()
    # define sector color
    colors = ['#e6194b', '#3cb44b', '#ffe119', '#0082c8', '#f58231', '#911eb4',
              '#46f0f0', '#f032e6', '#d2f53c', '#fabebe', '#008080', '#e6beff']
    sector_colors = dict(zip(symbolSector["sector"].unique(), colors))
    symbolSector["color"] = symbolSector["sector"].astype(str).apply(lambda x: sector_colors[x])
    # select sectors to show
    print(symbolSector["sector"].unique())
    show_section = [
                    #"Consumer Services",
                    #"Public Utilities",
                    "Basic Industries",
                    #"Capital Goods",
                    #"Finance",
                    "Consumer Non-Durables",
                    "Technology",
                    #"Health Care",
                    "Energy",
                    #"Consumer Durables",
                    #"Miscellaneous",
                    "Transportation"
                    ]
    symbolSector = symbolSector[symbolSector["sector"].isin(show_section)]


    alpha_beta_sector = pd.concat([alpha_beta, symbolSector], axis=1, join='inner')  # type: pd.DataFrame

    mktcap = preprocess.retrieve_mkt_caps(alpha_beta_sector.index)
    print(mktcap)

    # TODO: CONTINUE HERE

    fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'))
    scatter = ax.scatter(alpha_beta["alpha"], alpha_beta["beta"], c=symbolSector["color"])
    ax.grid(color='white', linestyle='solid')
    ax.set_title("Alpha vs Beta", size=20)
    labels = [str(label) for label in alpha_beta.index]
    tooltip = mpld3.plugins.PointLabelTooltip(scatter, labels=labels)
    mpld3.plugins.connect(fig, tooltip)
    mpld3.show()
