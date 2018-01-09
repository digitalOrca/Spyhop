#!/use/bin/python3

import numpy as np
import pandas as pd
from Preprocess import Preprocess
from sklearn.neighbors import KernelDensity
import matplotlib.pyplot as plt


class Beta:

    def __init__(self):
        self.preprocess = Preprocess(data='open_close')

    # TODO: put this in a common class
    def compute_alpha(self):
        self.preprocess.retrieve_fundamental_ratios(lag=True)  # set fr dates
        start_date = self.preprocess.frdate
        ArDf = self.preprocess.compute_return(split=False)
        benchmark = self.preprocess.compute_benchmark("snp500")
        ArDf = ArDf.dropna(axis=0, how='any')  # prevent arithmetic error
        ArDf["return"] = np.log(np.divide(ArDf["return"], benchmark))
        return ArDf

    def compute_beta(self, benchmark):
        index = self.preprocess.retrieve_benchmark(benchmark)
        stock = self.preprocess.retrieve_open_close()
        index_change = index[benchmark].pct_change()
        stock_change = stock.pct_change()
        for col in stock_change:
            nan_count = stock_change[col].isnull().sum()
            if nan_count > 3:
                stock_change.drop([col], axis=1, inplace=True)
        all_change = pd.concat([index_change, stock_change], axis=1, join='inner').fillna(0)
        all_beta = pd.DataFrame(index=all_change.columns, columns=["beta"], dtype=np.float32)
        all_beta.drop([benchmark], axis=0, inplace=True)  # remove benchmark column
        for col in all_change:
            if col != benchmark:
                a = all_change[col].values
                b = all_change[benchmark].values
                beta = np.multiply(np.corrcoef(a, b), np.divide(np.std(a), np.std(b)))[0, 1]
                all_beta["beta"].loc[col] = beta
        all_beta.dropna(axis=0, how='any', inplace=True)
        return all_beta

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
    betas = sb.compute_beta("snp500")
    alphas = sb.compute_alpha()
    #sb.visualize_beta_distribution(betas)
    alpha_beta = pd.concat([alphas, betas], axis=1, join='inner')
    plt.plot(alpha_beta["return"], alpha_beta["beta"], '.')
    plt.show()
