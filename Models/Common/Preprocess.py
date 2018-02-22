#!/usr/bin/python3

import numpy as np
import pandas as pd
from sklearn import preprocessing
from DBUtils import DBConnect
from datetime import date
from datetime import timedelta


class Preprocess:

    def __init__(self, data=None, lag=30, density=0.75, limit=3, outlier=4):
        self.db = DBConnect()
        self.data = data
        self.lag = lag
        self.density = density
        self.limit = limit
        self.outlier = outlier

    def retrieve_fundamental_ratios(self, lag=True):
        if lag:
            # get time window
            start = (date.today() - timedelta(days=self.lag)).isoformat()
            end = date.today().isoformat()
            # select the earliest fundamental ratio data within one month
            query = "SELECT * FROM fundamental_ratios WHERE date = \
                    (SELECT DISTINCT date FROM fundamental_ratios WHERE date > '%s' ORDER BY date ASC LIMIT 1)" % start
            df = self.db.query(query)
        else:
            query = "SELECT * FROM fundamental_ratios WHERE date = \
                    (SELECT DISTINCT date FROM fundamental_ratios ORDER BY date DESC LIMIT 1)"
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
            query = "SELECT * FROM bar_history WHERE timestamp >= '%s 08:30:00' ORDER BY index ASC" % start_date
            df = self.db.query(query)[["timestamp", "wap", "volume"]]            
            return df

    def retrieve_open_close(self):  # daily price
        start_date = (date.today() - timedelta(days=self.lag)).isoformat()
        selection = "SELECT * FROM open_close WHERE date >= '%s' ORDER BY index ASC" % start_date
        df = self.db.query(selection, index='date')  # Type: DataFrame
        df['symbol'] = df['symbol'].astype('category')
        symbols = df["symbol"].unique()
        multi_columns = []
        for symbol in symbols:
            for col in ["open", "close", "average"]:
                multi_columns.append((symbol, col))
        columns = pd.MultiIndex.from_tuples(multi_columns, names=["symbol", "field"])
        daily_price = pd.DataFrame(columns=columns)
        for symbol in symbols:
            mask = df["symbol"] == symbol
            daily_price[(symbol, "close")] = df.loc[mask, "lastclose"].shift(-1)
            daily_price[(symbol, "open")] = df.loc[mask, "open"]
            daily_price[(symbol, "average")] = pd.concat([df.loc[mask, "lastclose"].shift(-1),
                                                          df.loc[mask, "open"]], axis=1).mean(axis=1, skipna=True)
        daily_price.sort_index(axis=0, level=0)
        return daily_price

    def retrieve_return(self, date1=None, date2=None):
        if date1 is None:
            start = (date.today() - timedelta(days=self.lag)).isoformat()
            query1 = "SELECT symbol, lastclose, open FROM open_close WHERE date = " \
                     "(SELECT DISTINCT date FROM open_close WHERE date > '%s' ORDER BY date ASC LIMIT 1)" \
                     % start
        else:
            query1 = "SELECT symbol, lastclose, open FROM open_close WHERE date='%s'" % date1

        if date2 is None:
            query2 = "SELECT symbol, lastclose, open FROM open_close WHERE date = " \
                     "(SELECT DISTINCT date FROM open_close ORDER BY date DESC LIMIT 1)"
        else:
            query2 = "SELECT symbol, lastclose, open FROM open_close WHERE date='%s'" % date2

        start_df = self.db.query(query1)
        end_df = self.db.query(query2)
        start_df['start'] = start_df.mean(axis=1, numeric_only=True)
        end_df['end'] = end_df.mean(axis=1, numeric_only=True)
        start_df.drop(["lastclose", "open"], axis=1, inplace=True)
        end_df.drop(["lastclose", "open"], axis=1, inplace=True)
        ret = pd.concat([start_df, end_df], axis=1, join="inner")  # type: pd.DataFrame
        ret["return"] = np.divide(ret["end"], ret["start"])
        ret.drop(['start', 'end'], axis=1, inplace=True)
        return ret

    def retrieve_high_low(self):
        selection = "SELECT * FROM high_low"
        df = self.db.query(selection, index="symbol")  # type: pd.DataFrame
        return df

    def retrieve_mkt_caps(self, symbols):
        start = (date.today() - timedelta(days=self.lag)).isoformat()
        end = (date.today() - timedelta(days=self.lag/2)).isoformat()
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
        mktcap.set_index(pd.Series(data=mktcap.index).astype('category'))  # change index type to category
        return mktcap

    def retrieve_symbol_sector(self):
        symbol_sector = self.db.query("SELECT symbol, sector FROM security")
        symbol_sector["sector"] = symbol_sector["sector"].astype('category')
        return symbol_sector

    def retrieve_benchmark(self, benchmark, dates=None):
        col_close = benchmark + "_prev_close"
        col_open = benchmark + "_open"
        if dates is None:
            start_date = (date.today() - timedelta(days=self.lag)).isoformat()
            selection = "SELECT date, %s, %s FROM benchmarks WHERE date >= '%s' ORDER BY date ASC"\
                        % (col_close, col_open, start_date)
        else:
            selection = "SELECT date, %s, %s FROM benchmarks WHERE date >= '%s' AND date <= '%s' ORDER BY date ASC"\
                        % (col_close, col_open, dates[0], dates[1])
        index_series = self.db.query(selection, index='date')  # type: pd.DataFrame
        index_series["open"] = index_series[col_open]
        index_series["close"] = index_series[col_close].shift(periods=-1)
        index_series.dropna(axis=0, how='any', inplace=True)
        return index_series[["open", "close"]]

    def retrieve_benchmark_change(self, benchmark, date1=None, date2=None):
        col_close = benchmark + "_prev_close"
        col_open = benchmark + "_open"
        if date1 is None:
            start = (date.today() - timedelta(days=self.lag)).isoformat()
            query1 = "SELECT date, %s FROM benchmarks WHERE date = " \
                     "(SELECT DISTINCT date FROM benchmarks WHERE date > '%s' ORDER BY date ASC LIMIT 1)" \
                     % (col_close, start)
        else:
            query1 = "SELECT date, %s FROM benchmarks WHERE date='%s'" % (col_close, date1)

        if date2 is None:
            query2 = "SELECT date, %s FROM benchmarks WHERE date= \
                     (SELECT DISTINCT date FROM benchmarks ORDER BY date DESC LIMIT 1)"\
                     % col_open
        else:
            query2 = "SELECT date, %s FROM benchmarks WHERE date='%s'" % (col_open, date2)

        start_index = float(self.db.query(query1, index=None)[col_close][0])
        end_index = float(self.db.query(query2, index=None)[col_open][0])
        return end_index/start_index

    def retrieve_dividends(self):
        selection = "SELECT * FROM dividend"
        df = self.db.query(selection, index="symbol")  # type: pd.DataFrame
        return df

    ######################################################################################
    ######################################################################################
    ######################################################################################

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
                df.loc[df[column] > outlier_upper, column] = upper
                df.loc[df[column] < outlier_lower, column] = lower
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
                return scaled_train_data, scaled_validate_data  # dataType == 'scaled'
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
                return scaled_data  # dataType == 'scaled'
