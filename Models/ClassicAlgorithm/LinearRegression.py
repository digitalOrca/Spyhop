#!/usr/bin/python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from DBUtils import DBConnect
from datetime import date
from datetime import timedelta
from Preprocess import Preprocess


class LinearRegression:


    def __init__(self, lag=30, density=0.8, groupNum=21, scoreOrder=4, \
                                    retMin=-0.25, retMax=0.25, p_value = 0.05):
        self.db = DBConnect()
        self.preprocess = Preprocess(data='fundamental_ratios', lag=lag, \
                                                             density=density)
        self.groupNum = groupNum
        self.scoreOrder = scoreOrder
        self.retMin = retMin
        self.retMax = retMax
        self.p_value = p_value
        self.coefficient = pd.DataFrame()

        
    def group(self, df):
        dfGroup = []
        rowsCount = len(df)
        groupSize = np.ceil(float(rowsCount)/float(self.groupNum))
        for column in df:
            sortedColumn = df[column].sort_values(ascending=True) # sort based on ratio values
            currGroup, currStock = 0, 0
            fGroup_temp = [[] for i in range(self.groupNum)]
            symbols = list(sortedColumn.index)
            for i, val in enumerate(fGroup_temp):
                increment = (len(symbols) - currStock) / (self.groupNum - currGroup)
                fGroup_temp[i] = symbols[int(currStock):int(currStock+increment)]
                currStock += increment
                currGroup += 1     
            fGroup = [str(i) for i in fGroup_temp]    
            dfGroup.append(fGroup)
        npGroup = np.transpose(np.asarray(dfGroup))
        groupIndex = [i for i in range(self.groupNum)]
        columns = df.columns.values
        groupDf = pd.DataFrame(data=npGroup, index=groupIndex, columns=columns)
        return groupDf

    
    def computeRank(self, df, groupDf):
        rankDf = pd.DataFrame(index=df.index)
        for column in groupDf:
            col = pd.Series(index=df.index)
            for index, group in groupDf[column].iteritems():
                symbols = eval(group)
                for symbol in symbols:
                    col[symbol] = index
            rankDf[column] = col
        return rankDf


    def computeBenchmarkAR(self, benchmark):
        # get the date of fundamental ratio data
        query1 = "SELECT date, %s FROM benchmark WHERE date='%s'"\
                                                %(benchmark, self.preprocess.frdate)
        startIndex = float(self.db.query(query1, index='date')[benchmark][0])
        query2 = "SELECT date, %s FROM benchmark WHERE date=\
            (SELECT DISTINCT date FROM benchmark ORDER BY date DESC LIMIT 1)"\
                                                %benchmark
        endIndex = float(self.db.query(query2, index='date')[benchmark][0])
        return endIndex/startIndex
               

    def computeAR(self, groupDf, benchmark):
        # get the date of fundamental ratio data
        query1 = "SELECT symbol, lastclose, open FROM open_close WHERE date='%s'"%self.preprocess.frdate     
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
        benchmarkAR = self.computeBenchmarkAR(benchmark)
        ArDf["return"] = (ArDf["end"]/ArDf["start"])/benchmarkAR -1.0
        # remove legacy columns
        ArDf.drop(['start', 'end'], axis=1, inplace=True)
        # remove outlier returns
        bull = ArDf[ArDf['return'] > self.retMax]
        #print("Number of stocks exceeding max gain:",len(bull))
        ArDf.drop(bull.index, inplace=True)
        bear = ArDf[ArDf['return'] < self.retMin]
        #print("Number of stocks exceeding max loss:",len(bear))
        ArDf.drop(bear.index, inplace=True)
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
        
        
    def visualizeGroupAR(self, groupAR):
        x = np.arange(self.groupNum)
        plotSize = float(len(groupAR.columns))
        dim = np.ceil(np.sqrt(plotSize))
        pltIndex = 1
        for factor in groupAR.columns:
            plt.subplot(dim, dim, pltIndex)
            pltIndex += 1
            plt.scatter(x, groupAR[factor])
            plt.xlabel("groups")
            plt.ylabel(factor)
            axes = plt.gca()
            axes.set_ylim([-0.05,0.05]) 
        plt.show()
        
        
    def computeCorrCoef(self, groupAR):
        coefDf = pd.DataFrame(index=groupAR.columns)
        coefDf["corrcoef"] = 0.0
        for column in groupAR:
            x = [i for i in range(self.groupNum)]
            y = groupAR[column].astype(float)
            slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
            if p_value < self.p_value:
                coefDf["corrcoef"][column] = r_value
            else:
                coefDf.drop([column], axis=0, inplace=True)
                #print("remove insignificant column:", "%16s"%column," (p value: %f)"%p_value)
        self.coefficient = coefDf
        return coefDf
        
        
    def computeSymbolScore(self, coefDf, rankDf, Ar=None):
        newRankDf = pd.DataFrame(0.0, index=rankDf.index, columns=rankDf.columns)
        dropList1 = [col for col in rankDf.columns if col not in coefDf.index]
        dropList2 = [ind for ind in coefDf.index if ind not in rankDf.columns]
        rankDf.drop(dropList1, axis=1, inplace=True)
        coefDf.drop(dropList2, inplace=True)
        coefDf = np.sign(coefDf) * coefDf.pow(self.scoreOrder).abs()
        offset = (float(self.groupNum) - 1.0)/2.0
        rankDf = rankDf - offset
        newRankDf["score"] = rankDf.dot(coefDf)
        if Ar is not None:
            scoreDf = newRankDf['score'].to_frame().join(100*Ar['return'], how='left')
            return scoreDf.sort_values('score', ascending=False)
        return newRankDf['score'].sort_values(ascending=False)
        
    
    def train(self, benchmark, trainset=None):
        if trainset is not None:
            data = trainset
        else:
            data = self.preprocess.getData(dataType = 'filled', lag = True)
        groups = self.group(data)
        ar, gar = self.computeAR(groups, benchmark)
        #self.visualizeGroupAR(gar)
        coefDf = self.computeCorrCoef(gar)
        rankDf = self.computeRank(data, groups)
        return self.computeSymbolScore(coefDf, rankDf, ar)


    def validate(self, benchmark, validateset):
        testGroups = self.group(validateset)
        ar, gar = self.computeAR(testGroups, benchmark)
        testRankDf = self.computeRank(validateset, testGroups)
        return self.computeSymbolScore(self.coefficient, testRankDf, ar)
        

    def train_validate(self, benchmark):
        trainSet = self.preprocess.getData(dataType = 'filled', lag = True, dset="train")
        validateSet = self.preprocess.getData(dataType = 'filled', lag = True, dset="validate")
        t = self.train(benchmark, trainset=trainSet)
        v = self.validate(benchmark, validateset = validateSet)
        return t,v
        

    def predict(self):
        newdata = self.preprocess.getData(dataType = 'filled', lag = False)
        if self.coefficient.empty:
            print("model coefficient not fitted!")
            return
        newGroupDf = self.group(newdata)
        newRankDf = self.computeRank(newdata, newGroupDf)
        return self.computeSymbolScore(self.coefficient, newRankDf)
        
       
#lr = LinearRegression()
#print(lr.train("snp500")))
#import timeit
#start_time = timeit.default_timer()
#data = lr.preprocess.getData(dataType = 'filled', lag = True)
#groups = lr.group(data)
#ar, gar = lr.computeAR(groups, "snp500")
#coefDf = lr.computeCorrCoef(gar)
#rankDf = lr.computeRank(data, groups)
#lr.computeSymbolScore(coefDf, rankDf, ar)
#elapsed = timeit.default_timer() - start_time
#self.visualizeGroupAR(gar)
#print(elapsed)
