#!/usr/bin/python3

from Preprocess import Preprocess

class RecentHigh:

    def __init__(self):
        self.preprocess1 = Preprocess(data='open_close')
        self.preprocess2 = Preprocess(data='high_low')
    
    def prepData(self):
        daily_price = self.preprocess1.get_data()
        recent = daily_price.tail(3)
        high_low = self.preprocess2.get_data()
        print(daily_price)
        print(high_low)
        return recent
    

if __name__ == "__main__":
    rh = RecentHigh()
    rh.prepData()        
