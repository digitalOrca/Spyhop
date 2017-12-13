#!/usr/bin/python3

import numpy as np
import pandas as pd
from sklearn import preprocessing
from DBUtils import DBConnect
from datetime import date
from datetime import timedelta


class Preprocess:


    def __init__(self, data, lag=30, density=0.75, limit=3, outlier=4):
        self.db = DBConnect()
        self.data = data
        self.lag = lag
        self.density = density
        self.limit = limit
        self.outlier = outlier
        self.frdate = ""
        self.prdate = ""


    def _retrieveFundamentalRatios(self, lag=True):
        if lag:
            # get time window
            start = (date.today() - timedelta(days=self.lag)).isoformat()
            end = date.today().isoformat()
            # select the earliest fundamental ratio data within one month
            query = "SELECT * FROM fundamental_ratios WHERE date = \
                    (SELECT DISTINCT date FROM fundamental_ratios \
                    WHERE date > '%s'\
                    ORDER BY date ASC LIMIT 1)"\
                    %(start)
            df = self.db.query(query)
            
            self.frdate = df.date[0]
            self.prdate = end 
        else:
            query = "SELECT * FROM fundamental_ratios WHERE date = \
                    (SELECT DISTINCT date FROM fundamental_ratios \
                    ORDER BY date DESC LIMIT 1)"
            df = self.db.query(query)
        return df.fillna(value=np.nan) # replace None with np.nan
        
    
    def _retrieveTicks(self, lag=True):
        if lag:
            # get time window
            start = (date.today() - timedelta(days=self.lag)).isoformat()
            query = "SELECT * from tick_history WHERE timestamp > \
                     (SELECT timestamp FROM tick_history \
                         WHERE timestamp > '%s' \
                         ORDER BY timestamp ASC LIMIT 1) \
                     AND timestamp < \
                     (SELECT timestamp FROM tick_history \
                        WHERE timestamp > '%s' \
                        ORDER BY timestamp ASC LIMIT 1) \
                        + INTERVAL '%s days' \
                     ORDER BY timestamp ASC" \
                     %(start, start, self.lag/2)
            df = self.db.query(query)
            return df[df["event"]=="last"][["timestamp","last_price","last_size"]]
        else:
            query = "SELECT * FROM tick_history WHERE timestamp > \
                     (SELECT timestamp FROM tick_history \
                     ORDER BY timestamp DESC LIMIT 1) \
                     - INTERVAL '%s days' \
                     ORDER BY timestamp ASC" \
                     %(self.lag/2)
            df = self.db.query(query)
            return df[df["event"]=="last"][["timestamp","last_price","last_size"]]
    
    
    def _retrieveBars(self, split=True, lag=True):
        if split:
            if lag:
                # get time window
                start = (date.today() - timedelta(days=self.lag)).isoformat()
                query = "SELECT * from bar_history WHERE timestamp > \
                         (SELECT timestamp FROM bar_history \
                             WHERE timestamp > '%s' \
                             ORDER BY timestamp ASC LIMIT 1) \
                         AND timestamp < \
                         (SELECT timestamp FROM bar_history \
                            WHERE timestamp > '%s' \
                            ORDER BY timestamp ASC LIMIT 1) \
                            + INTERVAL '%s days' \
                         ORDER BY timestamp ASC" \
                         %(start, start, self.lag/2)
                df = self.db.query(query)[["timestamp", "wap", "volume"]]
            else:
                query = "SELECT * FROM bar_history WHERE timestamp > \
                         (SELECT timestamp FROM bar_history \
                         ORDER BY timestamp DESC LIMIT 1) \
                         - INTERVAL '%s days' \
                         ORDER BY timestamp ASC" \
                         %(self.lag/2)
                df = self.db.query(query)[["timestamp", "wap", "volume"]]
            return df
        else:
            start_date = (date.today() - timedelta(days=self.lag)).isoformat()
            query = "SELECT * FROM bar_history WHERE timestamp >= '%s' \
                     ORDER BY index ASC"%start_date
            df = self.db.query(query)[["timestamp", "wap", "volume"]]
            return df
    
    
    def _retrieveOpenClose(self):
        start_date = (date.today() - timedelta(days=self.lag)).isoformat()
        selection = "SELECT * FROM open_close WHERE date >= '%s' \
                     ORDER BY index ASC"%start_date
        df = self.db.query(selection)
        df["average"] = df[["lastclose", "open"]].mean(axis=1, skipna=True, numeric_only=True)
        dailyPrice = {}
        for symbol in (df.index).unique().values:
            dailyPrice[symbol] = df[df.index==symbol][["date", "average"]]
        return dailyPrice
    
    
    def retrieveMktCaps(self, symbols):
        start = (date.today() - timedelta(days=self.lag)).isoformat()
        end = (date.today() - timedelta(days=self.lag/2)).isoformat()
        mktcap = {}
        for symbol in symbols:
            query = "SELECT AVG(mktcap) FROM fundamental_ratios WHERE symbol='%s' \
                     AND date BETWEEN '%s' AND '%s'" \
                     %(symbol, start, end)
            avgMktCaps = self.db.query(query, index=None)["avg"].values[0]
            # proximate mktcap using any data available
            if avgMktCaps is None:
                query2 = "SELECT AVG(mktcap) FROM fundamental_ratios WHERE symbol='%s'" \
                          %(symbol)
                avgMktCaps = self.db.query(query2, index=None)["avg"].values[0]
            mktcap[symbol] = avgMktCaps
        return mktcap
    
    
    def retrieveAR(self):
        if self.frdate == "" or self.prdate == "":
            self._retrieveFundamentalRatios(lag=True)
        query1 = "SELECT symbol, lastclose, open FROM open_close WHERE date='%s'"%self.frdate
        startDf = self.db.query(query1)
        startDf['start'] = startDf.mean(axis=1, numeric_only=True)
        
        query2 = "SELECT symbol, lastclose, open FROM open_close WHERE date=\
            (SELECT DISTINCT date FROM open_close ORDER BY date DESC LIMIT 1)"
        endDf = self.db.query(query2)
        endDf['end'] = endDf.mean(axis=1, numeric_only=True)
        startDf.drop(["lastclose", "open"], axis=1, inplace=True)
        endDf.drop(["lastclose", "open"], axis=1, inplace=True)
        ArDf = pd.concat([startDf, endDf], axis=1, join="inner")
        ArDf["return"] = (ArDf["end"]/ArDf["start"])
        ArDf.drop(['start', 'end'], axis=1, inplace=True)
        return ArDf
        
    
    def computeBenchmarkAR(self, benchmark):
        # get the date of fundamental ratio data
        query1 = "SELECT date, %s FROM benchmark WHERE date='%s'"\
                                                %(benchmark, self.frdate)
        startIndex = float(self.db.query(query1, index='date')[benchmark][0])
        query2 = "SELECT date, %s FROM benchmark WHERE date=\
            (SELECT DISTINCT date FROM benchmark ORDER BY date DESC LIMIT 1)"\
                                                %benchmark
        endIndex = float(self.db.query(query2, index='date')[benchmark][0])
        return endIndex/startIndex
    
        
    def _filterColumn(self, df):
        df = df.drop(['index','date','currency','latestadate'], axis=1)
        rowsCount = len(df)
        weakColumns = []
        for column in df:
            missing = df[column].isnull().sum()
            density = 1.0-(float(missing)/float(rowsCount))
            if density < self.density:
                weakColumns.append(column)
                #print "remove sparse column:", "%16s"%column," (density: %f)"%density 
        df.drop(weakColumns, axis=1, inplace=True)
        if df.empty:
            raise Exception("model density requirement too high!")
        return df
        
        
    def _fillMissingValue(self, df):	
        for column in df:
            median = df[column].median()
            df[column].fillna(value=median, inplace=True)
        return df
    
    
    def _capOutlier(self, df):
        rowsCount = len(df)
        outlierCounter = -1
        iterCount = 0
        while outlierCounter != 0 and iterCount < 50:
            iterCount += 1
            for column in df:
                mean = df[column].mean()
                stdev = df[column].std()
                upper = mean + self.limit * stdev
                lower = mean - self.limit * stdev
                outlierUpper = mean + self.outlier * stdev
                outlierLower = mean - self.outlier * stdev
                outlierCounter = ((df[column] > outlierUpper) | \
                                  (df[column] < outlierLower)).sum()
                df[column][df[column] > outlierUpper] = upper
                df[column][df[column] < outlierLower] = lower
            #print "remaining number of outliers:",outlierCounter 
        return df
    
    
    def _scaleData(self, data):
        scaler = preprocessing.MinMaxScaler()
        scaled_data = scaler.fit_transform(data)
        return pd.DataFrame(data = scaled_data ,index = data.index, columns=data.columns)
        
        
    def getData(self, dataType = "raw", lag=True, dset="all"): #raw, filtered, filled, scaled
        np.random.seed(int(date.today().strftime("%Y%m%d"))) #align splits for different models
        if self.data == "fundamental_ratios":
            raw_data = self._retrieveFundamentalRatios(lag = lag)
            mask = np.random.rand(len(raw_data)) < 0.8
            if dset == "train_validate":
                if dataType == 'raw':
                    return raw_data[mask], raw_data[~mask]
                filtered_data = self._filterColumn(raw_data)
                if dataType == 'filtered':
                    return filtered_data[mask], filtered_data[~mask]
                filtered_train_data = filtered_data[mask].copy()
                filtered_validate_data = filtered_data[~mask].copy()
                filled_train_data = self._fillMissingValue(filtered_train_data)
                filled_validate_data = self._fillMissingValue(filtered_validate_data)
                if dataType == 'filled':
                    return filled_train_data, filled_validate_data
                capped_train_data = self._capOutlier(filled_train_data)
                capped_validate_data = self._capOutlier(filled_validate_data)
                scaled_train_data = self._scaleData(capped_train_data)
                scaled_validate_data = self._scaleData(capped_validate_data)
                return scaled_train_data, scaled_validate_data
            else:
                if dataType == 'raw':
                    return raw_data
                filtered_data = self._filterColumn(raw_data)
                if dataType == 'filtered':
                    return filtered_data
                filled_data = self._fillMissingValue(filtered_data)
                if dataType == 'filled':
                    return filled_data
                capped_data = self._capOutlier(filled_data)
                scaled_data = self._scaleData(capped_data)
                return scaled_data
        elif self.data == "ticks":
            raw_data = self._retrieveTicks(lag)
            return raw_data
        elif self.data == "bars":
            if dset == "train_validate":
                split_data = self._retrieveBars(split=True, lag=lag)
                return split_data
            else:
                whole_data = self._retrieveBars(split=False, lag=lag)
                return whole_data
        elif self.data == 'open_close':
            raw_data = self._retrieveOpenClose(lag)
            return raw_data
            


#TODO: MOVE THIS TO UNITTEST
"""
pfr = Preprocess('fundamental_ratios')
raw = pfr._retrieveFundamentalRatios(lag=True)
pfr.retrieveAR()
import timeit
start_time = timeit.default_timer()
data = pfr._filterColumn(raw)
fulldata = pfr._fillMissingValue(data)
capped_data = pfr._capOutlier(fulldata)
pfr._scaleData(capped_data)
elapsed = timeit.default_timer() - start_time
print elapsed
#pfr.getData('filled')
"""
#pfr = Preprocess(data="bars")
#print(pfr.getData(lag=True, dset="all"))
