#!/usr/bin/python3

from Preprocess import Preprocess

class RecentHigh:

    def __init__(self):
        self.preprocess = Preprocess(data='open_close')
    
    def prepData(self):
        daily_price = self.preprocess.get_data()
        recent = daily_price.tail(3)
        # TODO: READ 52 WEEK HIGH
        # TODO: NEED TO COLLECT DATA FIRST
        return recent
    
            
        
        
if __name__ == "__main__":
    rh = RecentHigh()
    rh.prepData()        
