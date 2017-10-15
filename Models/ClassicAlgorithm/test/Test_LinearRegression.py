#!/usr/bin/python

import ast
import unittest
import numpy as np
import pandas as pd
from LinearRegression import LinearRegression

class Test_LinearRegression(unittest.TestCase):

    def setUp(self):
        self.lingres = LinearRegression()

    def test_preprocess_sub(self):
        df1 = self.lingres._retrieveFundamentalRatios()
        assert isinstance(df1, pd.DataFrame)
        assert not df1.empty
        df2 = self.lingres._filterColumn(df1)
        assert isinstance(df2, pd.DataFrame)
        assert not df2.empty
        df3 = self.lingres._fillMissingValue(df2)
        assert not df3.isnull().values.any()
     
    def test_preprocess(self):
        data = self.lingres.preprocess()
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert not data.isnull().values.any()
        
    def test_group_AR(self):
        data = self.lingres.preprocess()
        grouped = self.lingres.group(data)
        assert isinstance(grouped, pd.DataFrame)
        assert not grouped.empty
        assert len(grouped.index)==self.lingres.groupNum
        assert isinstance(grouped.iloc[0].iloc[0], str)
        assert isinstance(ast.literal_eval(grouped.iloc[0].iloc[0]), list)
        self.lingres.frdate = '2017-10-01' # choose a valid fund'ratio date
        ar, gar = self.lingres.computeAR(grouped, "snp500")
        assert isinstance(ar, pd.DataFrame)
        assert isinstance(gar, pd.DataFrame)
        
    def test_computeBenchmarkAR(self):
        self.lingres.frdate = '2017-10-01' # choose a valid fund'ratio date
        benchmark = self.lingres.computeBenchmarkAR("snp500")
        assert isinstance(benchmark, float)
        assert benchmark!=0
        
    def test_computeCorrCoef(self):
        ins = ['r1','r2','r3']
        cols = ['c1','c2','c3']
        df = pd.DataFrame(index=ins, columns=cols)
        df['c1']['r1'] = 1.0
        df['c1']['r2'] = 2.0
        df['c1']['r3'] = 3.0
        df['c2']['r1'] = 3.0
        df['c2']['r2'] = 2.0
        df['c2']['r3'] = 1.0
        df['c3']['r1'] = 1.0
        df['c3']['r2'] = 2.0
        df['c3']['r3'] = 1.0
        self.lingres.groupNum = 3
        corr = self.lingres.computeCorrCoef(df)
        assert len(corr.columns)==1
        assert len(corr.index)==3
        assert corr.iloc(0),iloc(0)==1.0
        assert corr.iloc(0),iloc(1)==-1.0
        assert corr.iloc(0),iloc(2)==0.0
        
    def test_computeRank(self):
        pass
        
    def test_computeSymbolScore(self):
        pass
        
if __name__=='__main__':
    unittest.main()
