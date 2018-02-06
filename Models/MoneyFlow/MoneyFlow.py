#!/usr/bin/python3

"""MoneyFlow.py
Description:
    computing the accumulative imbalance of two driving forces to the prices. 
    If the current trade tick is higher than the previous one, then its monetary
    amount is counted as the positive force, and vice-versa. The accumulative
    imbalance between positive and negative force is then correlated to the 
    price movement over a period of time.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Preprocess import Preprocess


class MoneyFlow:
    
    """
    Constructor
    """
    def __init__(self, lag=30):
        self.preprocess = Preprocess(lag=lag)

    """prepareData
    Description:
        prepare data as a dict of price sequences
    Input:
        lag: if the data is lagged
    Output:
        sequences: dict of price sequence for each symbol
    """
    def prepareData(self, lag=True):
        print("retrieving bar data...")
        df = self.preprocess.retrieve_bars(split=True, lag=lag)
        sequences = {}
        count = 0
        for symbol in (df.index).unique().values:
            print("count:", count, " symbol: ", symbol)
            count += 1
            sequences[symbol] = df[df.index == symbol]
        return sequences

    """computeMoneyFlow
    Description:
        compute money flow imbalance for each symbol
    Input:
        sequences: dict of price sequence for each symbol
    Output:
        flow: dict of trade imbalance correspond to each symbol
    """    
    def computeMoneyFlow(self, sequences):
        count = 0
        flow = pd.DataFrame(columns=["flow"])
        for symbol in sequences.keys():
            symbol_seq = sequences[symbol]
            sign = np.sign(np.subtract(symbol_seq["wap"], symbol_seq["wap"].shift(periods=1)))
            balance = np.multiply(sign[1:], np.multiply(symbol_seq["wap"][1:], symbol_seq["volume"][1:])).sum()
            print("count", count, ", symbol", symbol, ":", balance)
            count += 1
            # https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#a1844eb442fb657c0f2cc0a63e4e74eba
            # tick size has multiplier of 100
            flow.loc[symbol] = balance * 100
        flow.set_index(pd.Series(data=flow.index).astype('category'))
        return flow

    """normalizeMoneyFlow
    Description:
        normalize computed money flow imbalance by the market cap of the symbol
    Input:
        flow: dict of trade imbalance correspond to each symbol
    Output:
        normalizeMoneyFlow: dict of normalized trade imbalance correspond 
        to each symbol
    """
    def normalizeMoneyFlow(self, flow):
        print("retrieving market capitalization...")
        mktcap = self.preprocess.retrieve_mkt_caps(flow.index)
        print("received market capitalization")
        flow_cap = pd.concat([flow, mktcap], axis=1, join="inner").dropna(axis=0, how="any")
        flow_cap["normal_flow"] = np.divide(np.divide(flow_cap["flow"], flow_cap["mktcap"]), 1000000)
        normalized_flow = flow_cap["normal_flow"].to_frame()
        return normalized_flow

    """visualizeFlowReturn
    Description:
        visualize normalized money flow imbalance and the return
    """
    def visualizeFlowReturn(self, normalizedFlow):
        ar = self.preprocess.compute_return(split=True, dset='train')  # stock return during next period
        ar.set_index(pd.Series(data=ar.index).astype('category'))
        print(ar)
        flow_return = pd.concat([normalizedFlow, ar], axis=1, join='inner')
        print(flow_return)
        # print(flow_return)
        x = flow_return["normal_flow"]
        y = flow_return["return"]
        plt.plot(x, y, 'r.')
        plt.show()

    def train(self):
        pass

    def predict(self):
        pass


if __name__ == "__main__":
    mf = MoneyFlow()
    seq = mf.prepareData()
    f = mf.computeMoneyFlow(seq)
    nf = mf.normalizeMoneyFlow(f)
    mf.visualizeFlowReturn(nf)
