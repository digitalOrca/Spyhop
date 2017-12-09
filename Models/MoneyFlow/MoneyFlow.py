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
    #TODO: increase lag once more data is available
    def __init__(self, lag=6):
        self.preprocess = Preprocess(data='bars', lag=lag)
    
    
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
        df = self.preprocess.getData(lag=lag)
        sequences = {}
        count = 0
        print(df)
        print((df.index).unique().values)
        for symbol in (df.index).unique().values:
            print("count:",count, " symbol: ", symbol)
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
        flow = pd.DataFrame(columns=["flow"])
        count = 0
        for symbol in sequences.keys():
            prev_price = None
            balance = 0
            for index, row in sequences[symbol].iterrows():
                # https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#a1844eb442fb657c0f2cc0a63e4e74eba
                # tick size has multiplier of 100
                vote = row["wap"] * row["volume"] * 100
                if prev_price is None:
                    pass
                elif row["wap"] > prev_price:
                    balance += vote
                elif row["wap"] < prev_price:
                    balance -= vote
                else:
                    pass
                prev_price = row["wap"]
            flow.loc[symbol] = balance
            print("count: ", count, " symbol: ", symbol, " balance: ", balance)
            count += 1
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
        mktcap = self.preprocess.retrieveMktCaps(flow.index)
        normalizedFlow = pd.DataFrame(columns=["flow"])
        count = 0
        for symbol in flow.index:
            if mktcap[symbol] is None:
                print("market caps data not available for %s"%symbol)
                count += 1
                continue
            normalizedFlow.loc[symbol] = flow.loc[symbol]["flow"] / (mktcap[symbol] * 1000000)
        print("Number of discarded symbols: ", count)
        return normalizedFlow
        
    
    """visualizeFlowReturn
    Description:
        visualize normalized money flow imbalance and the return
    """
    def visualizeFlowReturn(self, normalizedFlow):
        ar = self.preprocess.retrieveAR()
        print(ar)
        flowReturn = pd.concat([normalizedFlow, ar], axis=1, join='inner')
        #print(flowReturn)
        x = flowReturn["flow"]
        y = flowReturn["return"]
        plt.plot(x, y, 'r.')
        plt.show()
    
        
    def train(self):
        pass
        
        
    def predict(self):
        pass


mf = MoneyFlow()
seq = mf.prepareData()
f = mf.computeMoneyFlow(seq)
nf = mf.normalizeMoneyFlow(f)
mf.visualizeFlowReturn(nf)


# IMPLEMENT EVALUATION OF MODEL
