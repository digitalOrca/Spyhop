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
    
    #TODO: increase lag once more data is available
    def __init__(self, lag=3):
        self.preprocess = Preprocess(data='bars', lag=lag)
    
        
    def prepareData(self):
        df = self.preprocess.getData()
        sequences = {}
        for symbol in df.symbol.unique().values:
            sequences[symbol] = df[df.symbol == symbol]
        return sequences
    
        
    def computeMoneyFlow(self, sequences):
        flow = pd.DataFrame(columns=["flow"])
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
        return flow
                
        
    def normalizeMoneyFlow(self, flow):
        mktcap = self.preprocess.retrieveMktCaps(flow.index)
        normalizedFlow = pd.DataFrame(columns=["flow"])
        for symbol in flow.index:
            if mktcap[symbol] is None:
                print("market caps data not available for %s"%symbol)
                continue
            normalizedFlow.loc[symbol] = flow.loc[symbol]["flow"] / (mktcap[symbol] * 1000000)
        return normalizedFlow
        
    
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
