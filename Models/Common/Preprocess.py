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

    def retrieve_fundamental_ratios(self, lag=True):
        if lag:
            # get time window
            start = (date.today() - timedelta(days=self.lag)).isoformat()
            end = date.today().isoformat()
            # select the earliest fundamental ratio data within one month
            query = "SELECT * FROM fundamental_ratios WHERE date = \
                    (SELECT DISTINCT date FROM fundamental_ratios \
                    WHERE date > '%s'\
                    ORDER BY date ASC LIMIT 1)"\
                    % start
            df = self.db.query(query)
            
            self.frdate = df.date[0]
            self.prdate = end 
        else:
            query = "SELECT * FROM fundamental_ratios WHERE date = \
                    (SELECT DISTINCT date FROM fundamental_ratios \
                    ORDER BY date DESC LIMIT 1)"
            df = self.db.query(query)
        return df.fillna(value=np.nan)

    def retrieve_ticks(self, lag=True):
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
                     % (start, start, self.lag/2)
            df = self.db.query(query)
            return df[df["event"] == "last"][["timestamp", "last_price", "last_size"]]
        else:
            query = "SELECT * FROM tick_history WHERE timestamp > \
                     (SELECT timestamp FROM tick_history \
                     ORDER BY timestamp DESC LIMIT 1) \
                     - INTERVAL '%s days' \
                     ORDER BY timestamp ASC" \
                     % (self.lag/2)
            df = self.db.query(query)
            return df[df["event"] == "last"][["timestamp", "last_price", "last_size"]]

    def retrieve_bars(self, split=True, lag=True):
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
                         % (start, start, self.lag / 2)
                df = self.db.query(query)[["timestamp", "wap", "volume"]]
            else:
                query = "SELECT * FROM bar_history WHERE timestamp > \
                         (SELECT timestamp FROM bar_history \
                         ORDER BY timestamp DESC LIMIT 1) \
                         - INTERVAL '%s days' \
                         ORDER BY timestamp ASC" \
                         % (self.lag/2)
                df = self.db.query(query)[["timestamp", "wap", "volume"]]
            return df
        else:
            start_date = (date.today() - timedelta(days=self.lag)).isoformat()
            query = "SELECT * FROM bar_history WHERE timestamp >= '%s' \
                     ORDER BY index ASC" % start_date
            df = self.db.query(query)[["timestamp", "wap", "volume"]]            
            return df

    def retrieve_open_close(self):
        start_date = (date.today() - timedelta(days=self.lag)).isoformat()
        selection = "SELECT * FROM open_close WHERE date >= '%s' \
                     ORDER BY index ASC" % start_date
        df = self.db.query(selection)
        df["average"] = df[["lastclose", "open"]].mean(axis=1, skipna=True, numeric_only=True)
        daily_price = {}
        for symbol in (df.index).unique().values:
            daily_price[symbol] = df[df.index == symbol][["date", "average"]]
        return daily_price

    def retrieve_mkt_caps(self, symbols):
        start = (date.today() - timedelta(days=self.lag)).isoformat()
        end = (date.today() - timedelta(days=self.lag/2)).isoformat()
        #mktcap = {}
        mktcap = pd.DataFrame(columns=["mktcap"])
        for symbol in symbols:
            query = "SELECT AVG(mktcap) FROM fundamental_ratios WHERE symbol='%s' \
                     AND date BETWEEN '%s' AND '%s'" \
                     % (symbol, start, end)
            avg_mkt_caps = self.db.query(query, index=None)["avg"].values[0]
            # proximate mktcap using any data available
            if avg_mkt_caps is None:
                query2 = "SELECT AVG(mktcap) FROM fundamental_ratios WHERE symbol='%s'" \
                          % symbol
                avg_mkt_caps = self.db.query(query2, index=None)["avg"].values[0]
            mktcap.loc[symbol] = avg_mkt_caps
            #mktcap[symbol] = avg_mkt_caps
        mktcap.set_index(pd.Series(data=mktcap.index).astype('category'))  # change index type to category
        return mktcap

    def compute_return(self):
        if self.frdate == "" or self.prdate == "":
            self.retrieve_fundamental_ratios(lag=True)
        query1 = "SELECT symbol, lastclose, open FROM open_close WHERE date='%s'" % self.frdate
        start_df = self.db.query(query1)
        start_df['start'] = start_df.mean(axis=1, numeric_only=True)
        
        query2 = "SELECT symbol, lastclose, open FROM open_close WHERE date=\
            (SELECT DISTINCT date FROM open_close ORDER BY date DESC LIMIT 1)"
        end_df = self.db.query(query2)
        end_df['end'] = end_df.mean(axis=1, numeric_only=True)
        start_df.drop(["lastclose", "open"], axis=1, inplace=True)
        end_df.drop(["lastclose", "open"], axis=1, inplace=True)
        ret = pd.concat([start_df, end_df], axis=1, join="inner")  # type: pd.DataFrame
        ret["return"] = (ret["end"]/ret["start"])
        ret.drop(['start', 'end'], axis=1, inplace=True)
        return ret

    def compute_benchmark(self, benchmark):
        # get the date of fundamental ratio data
        query1 = "SELECT date, %s FROM benchmark WHERE date='%s'"\
                                                % (benchmark, self.frdate)
        start_index = float(self.db.query(query1, index='date')[benchmark][0])
        query2 = "SELECT date, %s FROM benchmark WHERE date=\
            (SELECT DISTINCT date FROM benchmark ORDER BY date DESC LIMIT 1)"\
            % benchmark
        end_index = float(self.db.query(query2, index='date')[benchmark][0])
        return end_index/start_index

    def filter_column(self, df):
        df = df.drop(['index', 'date', 'currency', 'latestadate'], axis=1)
        rows_count = len(df)
        weak_columns = []
        for column in df:
            missing = df[column].isnull().sum()
            density = 1.0-(float(missing)/float(rows_count))
            if density < self.density:
                weak_columns.append(column)
                # print "remove sparse column:", "%16s"%column," (density: %f)"%density
        df.drop(weak_columns, axis=1, inplace=True)
        if df.empty:
            raise Exception("model density requirement too high!")
        return df

    def fill_missing_value(self, df):
        for column in df:
            median = df[column].median()
            df[column].fillna(value=median, inplace=True)
        return df

    def cap_outlier(self, df):
        outlier_counter = -1
        iter_count = 0
        while outlier_counter != 0 and iter_count < 50:
            iter_count += 1
            for column in df:
                mean = df[column].mean()
                stdev = df[column].std()
                upper = mean + self.limit * stdev
                lower = mean - self.limit * stdev
                outlier_upper = mean + self.outlier * stdev
                outlier_lower = mean - self.outlier * stdev
                outlier_counter = ((df[column] > outlier_upper) | (df[column] < outlier_lower)).sum()
                df[column][df[column] > outlier_upper] = upper
                df[column][df[column] < outlier_lower] = lower
        return df

    def scale_data(self, data):
        scaler = preprocessing.MinMaxScaler()
        scaled_data = scaler.fit_transform(data)
        return pd.DataFrame(data=scaled_data, index=data.index, columns=data.columns)

    def get_data(self, dataType="raw", lag=True, dset="all"):
        np.random.seed(int(date.today().strftime("%Y%m%d")))
        if self.data == "fundamental_ratios":
            raw_data = self.retrieve_fundamental_ratios(lag=lag)
            mask = np.random.rand(len(raw_data)) < 0.8
            if dset == "train_validate":
                if dataType == 'raw':
                    return raw_data[mask], raw_data[~mask]
                filtered_data = self.filter_column(raw_data)
                if dataType == 'filtered':
                    return filtered_data[mask], filtered_data[~mask]
                filtered_train_data = filtered_data[mask].copy()
                filtered_validate_data = filtered_data[~mask].copy()
                filled_train_data = self.fill_missing_value(filtered_train_data)
                filled_validate_data = self.fill_missing_value(filtered_validate_data)
                if dataType == 'filled':
                    return filled_train_data, filled_validate_data
                capped_train_data = self.cap_outlier(filled_train_data)
                capped_validate_data = self.cap_outlier(filled_validate_data)
                scaled_train_data = self.scale_data(capped_train_data)
                scaled_validate_data = self.scale_data(capped_validate_data)
                return scaled_train_data, scaled_validate_data
            else:
                if dataType == 'raw':
                    return raw_data
                filtered_data = self.filter_column(raw_data)
                if dataType == 'filtered':
                    return filtered_data
                filled_data = self.fill_missing_value(filtered_data)
                if dataType == 'filled':
                    return filled_data
                capped_data = self.cap_outlier(filled_data)
                scaled_data = self.scale_data(capped_data)
                return scaled_data
        elif self.data == "ticks":
            raw_data = self.retrieve_ticks(lag)
            return raw_data
        elif self.data == "bars":
            if dset == "train_validate":
                split_data = self.retrieve_bars(split=True, lag=lag)
                return split_data
            else:
                whole_data = self.retrieve_bars(split=False, lag=lag)
                return whole_data
        elif self.data == 'open_close':
            raw_data = self.retrieve_open_close(lag)
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
