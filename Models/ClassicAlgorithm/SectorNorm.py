#!/usr/bin/python3

from DBUtils import DBConnect
import numpy as np
import pandas as pd
from datetime import date
from datetime import timedelta

class SectorNorm():
    
    def __init__(self, lag=30, retMax=0.25, retMin=-0.25):
        self.db = DBConnect()
        self.lag = lag
        self.retMax = retMax
        self.retMin = retMin
        
    def computeSectorReturn(self):
        symbolSector = self.db.query("SELECT symbol, sector FROM security")
        print(symbolSector)
        
        
        # get time window
        end = date.today().isoformat()
        start = (date.today() - timedelta(days=self.lag)).isoformat()
        
        query = "SELECT * FROM fundamental_ratios WHERE date = \
                    (SELECT DISTINCT date FROM fundamental_ratios \
                    WHERE date BETWEEN '%s' AND '%s' \
                    ORDER BY date ASC LIMIT 1)"\
                    %(start, end)
        df = self.db.query(query)
        start_date = df.date[0]
        
        
        query1 = "SELECT symbol, lastclose, open FROM open_close WHERE date='%s'"%start_date
        startDf = self.db.query(query1)
        startDf['start'] = startDf.mean(axis=1, numeric_only=True)
        # get the nearest date
        query2 = "SELECT symbol, lastclose, open FROM open_close WHERE date=\
            (SELECT DISTINCT date FROM open_close ORDER BY date DESC LIMIT 1)"
        endDf = self.db.query(query2)
        endDf['end'] = endDf.mean(axis=1, numeric_only=True)
        # concatnate two tables and compute stock return
        startDf.drop(["lastclose", "open"], axis=1, inplace=True)
        endDf.drop(["lastclose", "open"], axis=1, inplace=True)
        ArDf = pd.concat([startDf, endDf], axis=1, join="inner")
        ArDf = ArDf.dropna(axis=0, how='any') # prevent arithmetic error
        ArDf["return"] = (ArDf["end"]/ArDf["start"])-1.0
        # remove legacy columns
        ArDf.drop(['start', 'end'], axis=1, inplace=True)
        # remove outlier returns
        bull = ArDf[ArDf['return'] > self.retMax]
        ArDf.drop(bull.index, inplace=True)
        bear = ArDf[ArDf['return'] < self.retMin]
        ArDf.drop(bear.index, inplace=True)
        print(ArDf)
        
        sectorReturn = pd.concat([symbolSector, ArDf], axis=1, join="inner")
        sectorDict = {}
        for sector in sectorReturn["sector"].unique():
            returnSeries = sectorReturn[sectorReturn["sector"]==sector]["return"].values
            sectorDict[sector] = returnSeries
        
        print(sectorDict["Health Care"])
        #print(sectorReturn)
        
        """
        # compute group return
        groupAR = pd.DataFrame(index=groupDf.index)
        for column in groupDf:
            groupAR[column] = 0.0 # initialize empty column
            for groupIndex, groupStr in groupDf[column].iteritems():
                group = eval(groupStr)
                sumAR, count, avgAR = 0, 0, 0
                for symbol in group:
                    if symbol in ArDf.index:
                        count += 1.0
                        sumAR += ArDf["return"][symbol]
                if count != 0:
                    avgAR = sumAR / count
                groupAR[column][groupIndex] = avgAR
        return ArDf, groupAR
        """
        
        
        
        
        
        
        
        
s = SectorNorm()
s.computeSectorReturn()
