from unittest import TestCase
from Preprocess import Preprocess
import numpy as np
import pandas as pd


class TestPreprocess(TestCase):

    def test_retrieve_fundamental_ratios(self):
        self.preprocess = Preprocess(data="fundamental_ratios")
        try:
            df = self.preprocess.retrieve_fundamental_ratios()
            if not isinstance(df, pd.DataFrame) and not df.empty:
                raise Exception
        except:
            self.fail()

    def test_retrieve_ticks(self):
        self.preprocess = Preprocess(data="ticks", lag=7)
        try:
            df = self.preprocess.retrieve_ticks(lag=True)
            if not isinstance(df, pd.DataFrame) and not df.empty:
                raise Exception
        except:
            self.fail()

    def test_retrieve_bars(self):
        self.preprocess = Preprocess(data="bars", lag=7)
        try:
            df = self.preprocess.retrieve_bars()
            if not isinstance(df, pd.DataFrame) and not df.empty:
                raise Exception
        except:
            self.fail()

    def test_retrieve_open_close(self):
        self.preprocess = Preprocess(data="open_close", lag=7)
        try:
            df = self.preprocess.retrieve_open_close()
            if not isinstance(df, pd.DataFrame) and not df.empty:
                raise Exception
        except:
            self.fail()

    def test_retrieve_mkt_caps(self):
        self.preprocess = Preprocess(data="mktcaps", lag=7)
        try:
            df = self.preprocess.retrieve_mkt_caps(["GE", "MMM", "APPL"])
            if not isinstance(df, pd.DataFrame) and not df.empty:
                raise Exception
        except:
            self.fail()

    def test_retrieve_dividends(self):
        self.preprocess = Preprocess(data="open_close", lag=7)
        try:
            df = self.preprocess.retrieve_dividends()
            if not isinstance(df, pd.DataFrame) and not df.empty:
                raise Exception
        except:
            self.fail()

    def test_retrieve_benchmark(self):
        self.preprocess = Preprocess(data="open_close", lag=30)
        try:
            df = self.preprocess.retrieve_benchmark("snp500")
            if not isinstance(df, pd.DataFrame) and not df.empty:
                raise Exception
        except:
            self.fail()

    def test_compute_return(self):
        self.preprocess = Preprocess(data="", lag=7)
        try:
            df1 = self.preprocess.compute_return(split=False)  # non-split is a super set of split returns
            df2 = self.preprocess.compute_return(split=True, dset='train')
            df3 = self.preprocess.compute_return(split=True, dset='predict')
            if not isinstance(df1, pd.DataFrame) and not df1.empty and \
                    not isinstance(df2, pd.DataFrame) and not df2.empty and \
                    not isinstance(df3, pd.DataFrame) and not df3.empty:
                raise Exception
        except:
            self.fail()

    def test_compute_benchmark(self):
        self.preprocess = Preprocess(data="", lag=7)
        try:
            change = self.preprocess.compute_benchmark("snp500")
            if not isinstance(change, float):
                raise Exception
        except:
            self.fail()

    def test_filter_column(self):
        self.preprocess = Preprocess(data="", density=0.5, lag=7)
        data = [('symbol', ['A', 'B', 'C', 'D']),
                ('index', [150, 200, 50, 10]),
                ('date', [200, 210, 90, 20]),
                ('currency', [140, 215, 95, 30]),
                ('latestadate', [140, 215, 95, 40]),
                ('dense', [140, 215, np.NaN, 50]),
                ('sparse', [np.NaN, np.NaN, np.NaN, 60])]
        df = pd.DataFrame.from_items(data)
        filtered = self.preprocess.filter_column(df)
        self.assertEqual(len(filtered.columns), 2)  # only symbol and dense will survive

    def test_fill_missing_value(self):
        self.preprocess = Preprocess(data="", lag=7)
        data = [('x', [40, 30, np.NaN, np.NaN]),
                ('y', [np.NaN, 60, 50, 60])]
        df = pd.DataFrame.from_items(data)
        filled = self.preprocess.fill_missing_value(df)
        self.assertFalse(filled.isnull().values.any())

    def test_cap_outlier(self):
        self.preprocess = Preprocess(data="", lag=7, limit=3, outlier=4)
        data = [('x', [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 8]),
                ('y', [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 50]),
                ('z', [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 10000])]
        df = pd.DataFrame.from_items(data)
        dfc = df.copy()  # method will operate on the same memory location without making copy
        capped = self.preprocess.cap_outlier(df)
        self.assertEqual(capped['x'].max(), dfc['x'].max())
        self.assertTrue(capped['z'].max() < dfc['z'].max())

    def test_scale_data(self):
        self.preprocess = Preprocess(data="", lag=7)
        data = [('x', [1, 2, 3, 4]),
                ('y', [51, -6, 43, -8])]
        df = pd.DataFrame.from_items(data)
        scaled = self.preprocess.scale_data(df)
        self.assertTrue(scaled['x'].max() <= 1)
        self.assertTrue(scaled['y'].max() <= 1)
        self.assertTrue(scaled['x'].min() >= 0)
        self.assertTrue(scaled['y'].min() >= 0)

    def test_get_data(self):
        pass  # this method is composed of other tested methods
