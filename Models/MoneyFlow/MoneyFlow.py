#!/usr/bin/python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from Preprocess import Preprocess

class MoneyFlow:
    
    def __init__(self, lag=30):
        self.preprocess = Preprocess(data='ticks', lag=lag)
    
        
    def prepareData(self):
        df = self.preprocess.getData()
        sequences = {}
        for symbol in df.index.unique().values:
            sequences[symbol] = df[df.index == symbol]
        return sequences
    
        
    def computeMoneyFlow(self, sequences):
        #flow = {}
        flow = pd.DataFrame(columns=["flow"])
        for symbol in sequences.keys():
            prev_price = None
            balance = 0
            for index, row in sequences[symbol].iterrows():
                # https://interactivebrokers.github.io/tws-api/interfaceIBApi_1_1EWrapper.html#a1844eb442fb657c0f2cc0a63e4e74eba
                # tick size has multiplier of 100
                vote = row["last_price"] * row["last_size"] * 100
                if prev_price is None:
                    pass
                elif row["last_price"] > prev_price:
                    balance += vote
                elif row["last_price"] < prev_price:
                    balance -= vote
                else:
                    pass
                prev_price = row["last_price"]
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
