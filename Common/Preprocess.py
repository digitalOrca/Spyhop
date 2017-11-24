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
            end = date.today().isoformat()
            start = (date.today() - timedelta(days=self.lag)).isoformat()
            # select the earliest fundamental ratio data within one month
            query = "SELECT * FROM fundamental_ratios WHERE date = \
                    (SELECT DISTINCT date FROM fundamental_ratios \
                    WHERE date BETWEEN '%s' AND '%s' \
                    ORDER BY date ASC LIMIT 1)"\
                    %(start, end)
            df = self.db.query(query)
            
            self.frdate = df.date[0]
            self.prdate = end 
        else:
            query = "SELECT * FROM fundamental_ratios WHERE date = \
                    (SELECT DISTINCT date FROM fundamental_ratios \
                    ORDER BY date DESC LIMIT 1)"
            df = self.db.query(query)
        return df.fillna(value=np.nan) # replace None with np.nan
        
    
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
            """
            if dset == "train":
                raw_data = raw_data[mask]
            elif dset == "validate":
                raw_data = raw_data[~mask]
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
            """


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
