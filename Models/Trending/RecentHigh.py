#!/usr/bin/python3

import numpy as np
import pandas as pd
from Preprocess import Preprocess
import matplotlib.pyplot as plt

class RecentHigh:

    def __init__(self):
        self.preprocess1 = Preprocess(data='open_close')
        self.preprocess2 = Preprocess(data='high_low')
    
    def prepData(self, tolerance=3, reference=13):
        daily_price = self.preprocess1.get_data()
        recent_average = daily_price.tail(tolerance).mean(axis=0, skipna=True).to_frame(name="recent")
        high, low = "", ""
        if reference == 13:
            low, high = "low13", "high13"
        elif reference == 26:
            low, high = "low26", "high26"
        elif reference == 52:
            low, high = "low52", "high52"
        columns = [low, high]
        high_low = self.preprocess2.get_data()[columns]
        processed = pd.concat([high_low, recent_average], axis=1, join='inner')
        processed["ratio"] = np.clip(np.divide(np.subtract(processed["recent"], processed[low]),
                                               np.subtract(processed[high], processed[low])),
                                     0, 1)
        print(processed)

        # the histogram of the data
        n, bins, patches = plt.hist(processed["ratio"].values, bins=50, normed=1, facecolor='green', alpha=0.75)
        plt.axis([0, 1, 0, 2])
        plt.show()



if __name__ == "__main__":
    rh = RecentHigh()
    rh.prepData()        
