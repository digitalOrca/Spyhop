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
            flow[symbol] = balance
        return flow
                
        
    def normalizeMoneyFlow(self, flow):
        mktcap = self.preprocess.retrieveMktCaps(flow.keys())
        normalizedFlow = {}
        for symbol in flow.keys():
            if mktcap[symbol] is None:
                print("market caps data not available for %s"%symbol)
                continue
            normalizedFlow[symbol] = flow[symbol] / (mktcap[symbol] * 1000000)
        return normalizedFlow
        
        
    def predict(self):
        pass


mf = MoneyFlow()
seq = mf.prepareData()
f = mf.computeMoneyFlow(seq)
nf = mf.normalizeMoneyFlow(f)

for k in nf.keys():
    print(k,":",nf[k])

# IMPLEMENT EVALUATION OF MODEL
