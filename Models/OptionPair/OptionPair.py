#!/usr/bin/python3

from Preprocess import Preprocess
import Postprocess as post


class OptionPair:

    def __init__(self):
        self.preprocess = Preprocess(lag=70)

    def compute_correlation(self):
        daily_price = self.preprocess.retrieve_open_close()
        daily_change = post.compute_daily_change(daily_price)
        return daily_change.corr(method='pearson', min_periods=30)

    def find_movement_pairs(self, corr, threshold=0.9):
        pairs = []
        for symbol in corr:
            for (i, v) in corr[symbol].iteritems():
                if i == symbol:
                    continue
                else:
                    if abs(v) > threshold:
                        pairs.append((symbol, i, v))
        return pairs

    def narrow_growth_pairs(self, pairs, threshold=0.1):
        returns = self.preprocess.retrieve_return()

        for pair in pairs:
            try:
                r1 = returns.loc[pair[0], "return"]
                r2 = returns.loc[pair[1], "return"]
                drift = abs(r1-r2)/abs((r1+r2)/2)
            except KeyError:  # remove pair if return cannot be validated
                drift = 1
            if drift > threshold:
                pairs.remove(pair)
        return pairs


if __name__ == "__main__":
    op = OptionPair()
    covar = op.compute_correlation()
    pairs_mov = op.find_movement_pairs(covar)
    pair_final = op.narrow_growth_pairs(pairs_mov)
    for p in pair_final:
        print(p[0], p[1], p[2])
