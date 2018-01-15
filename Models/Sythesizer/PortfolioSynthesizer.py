#!/usr/bin/python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from SharpeRatio import SharpeRatio
from InformationRation import InformationRatio

if __name__ == "__main__":
    asset = ["NVDA", "AMZN", "GS", "ABT"]
    samples = 50000
    result = pd.DataFrame(index=range(samples), columns=["return", "stdev", "IR"])
    sharpe = SharpeRatio(asset)
    information = InformationRatio()
    for i in range(samples):
        w = np.random.random(len(asset))
        w /= np.sum(w)
        random_portfolio = pd.Series(w, index=asset)
        ret, stdev = sharpe.evaluatePortfolio(random_portfolio)
        IR = information.computeInformationRatio(dict(zip(asset, w)))
        result["return"].iloc[i] = ret
        result["stdev"].iloc[i] = stdev[0]
        result["IR"].iloc[i] = IR
        print("sample:", i, " return:", ret, " stdev:", stdev[0], " IR:", IR)
    plt.figure()
    plt.scatter(result["stdev"], result["return"], c=result["IR"], cmap='RdYlBu')
    plt.colorbar()
    plt.show()
