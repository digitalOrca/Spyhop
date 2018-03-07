#!/usr/bin/python3

from Preprocess import Preprocess
import Postprocess as post

class OptionPair:

    def __init__(self):
        self.preprocess = Preprocess(lag=70)

    def computeCorrelation(self):
        daily_price = self.preprocess.retrieve_open_close()
        daily_change = post.compute_daily_change(daily_price)
        return daily_change.corr(method='pearson', min_periods=30)

    def findPairs(self, corr, threshold=0.85):
        pairs = []
        for symbol in corr:
            for (i, v) in corr[symbol].iteritems():
                if i == symbol:
                    continue
                else:
                    if abs(v) > threshold:
                        pairs.append((symbol, i, v))
        for p in pairs:
            print(p[0], p[1], p[2])
        return pairs


if __name__ == "__main__":
    op = OptionPair()
    covar = op.computeCorrelation()
    pairs = op.findPairs(covar)
