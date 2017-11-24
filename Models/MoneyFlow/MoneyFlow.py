#!/usr/bin/python3

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
        flow = {}
        for symbol in sequences.keys():
            prev_price = None
            balance = 0
            for index, row in sequences[symbol].iterrows():
                vote = row["last_price"] * row["last_size"]
                if prev_price is None:
                    pass
                elif row["last_price"] > prev_price:
                    balance += vote
                elif row["last_price"] < prev_price:
                    balance -= vote
                else:
                    pass
                prev_price = row["last_price"]
            flow[symbol] = balance
        return flow
                
        
    def normalizeMoneyFlow(self):
        pass
        
    def predict(self):
        pass
        
mf = MoneyFlow()
seq = mf.prepareData()
f = mf.computeMoneyFlow(seq)

for k in f.keys():
    print(k,":",f[k])
#TODO: USE PROPER INPUT PERIOD, NOT JUST ONE DAY
# IMPLEMENT MARKET_CAP NORMALIZATION
# IMPLEMENT EVALUATION OF MODEL
