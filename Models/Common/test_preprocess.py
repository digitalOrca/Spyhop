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

    #def test_retrieve_open_close(self):  # TODO: maybe this is not needed
    #    self.preprocess = Preprocess(data="open_close", lag=7)
    #    try:
    #        df = self.preprocess.retrieve_open_close()
    #        if not isinstance(df, pd.DataFrame) and not df.empty:
    #            raise Exception
    #    except:
    #        self.fail()

    def test_retrieve_mkt_caps(self):
        self.preprocess = Preprocess(data="mktcaps", lag=7)  # TODO: add mktcaps option to Preprocess.getData
        try:
            df = self.preprocess.retrieve_mkt_caps(["GE", "MMM", "APPL"])
            if not isinstance(df, pd.DataFrame) and not df.empty:
                raise Exception
        except:
            self.fail()

    def test_compute_return(self):
        self.preprocess = Preprocess(data="", lag=7)
        try:
            df = self.preprocess.compute_return()
            if not isinstance(df, pd.DataFrame) and not df.empty:
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
        data = [('symbol',      ['A', 'B', 'C', 'D']),
                ('index',       [150, 200, 50, 10]),
                ('date',        [200, 210, 90, 20]),
                ('currency',    [140, 215, 95, 30]),
                ('latestadate', [140, 215, 95, 40]),
                ('dense',       [140, 215, np.NaN, 50]),
                ('sparse',      [np.NaN, np.NaN, np.NaN, 60])]
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

    """
    def test_cap_outlier(self):
        self.fail()

    def test_scale_data(self):
        self.fail()

    def test_get_data(self):
        self.fail()
    """
