#!/usr/bin/python3

"""LinearRegression
Description:
    multi-variable linear regression. Variables are all the fundamental ratios. 
    All symbols are divided into group, averaging their fundamental_ratios and 
    the average ratios are regressed with the return over a period of time to 
    determine the effectiveness of each variable. Then each symbol is rated by
    the sum of the variable scores.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from DBUtils import DBConnect
from sklearn import preprocessing
from Preprocess import Preprocess


class LinearRegression:

    """constructor
    lag: length of the period for calculating return
    density: data density requirement for each fundamental ratios columns
    groupNum: the number of groups
    scoreOrder: the amount of bias for variable with different confidence
    retMin: minimum return example to be included in the model
    retMax: maximum return example to be included in the model
    p_value: p-value requirement for each variable columns
    """
    def __init__(self, lag=30, density=0.8, groupNum=21, scoreOrder=4, retMin=-0.25, retMax=0.25, p_value=0.05):
        self.db = DBConnect()
        self.preprocess = Preprocess(data='fundamental_ratios', lag=lag, density=density)
        self.groupNum = groupNum
        self.scoreOrder = scoreOrder
        self.retMin = retMin
        self.retMax = retMax
        self.p_value = p_value
        self.coefficient = pd.DataFrame()

    """group
    Description:
        create symbol groups for each variables
    Input:
        df: processed dataframe with fundamental ratios
    Output:
        groupDf: symbol groups for each ratio
    """    
    def group(self, df):
        dfGroup = []
        rowsCount = len(df)
        groupSize = np.ceil(float(rowsCount)/float(self.groupNum))
        for column in df:
            sortedColumn = df[column].sort_values(ascending=True)  # sort based on ratio values
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

    """computeRank
    Description: 
        compute the ranking score of each symbol on each ratio
    Input:
        df: processed dataframe with fundamental ratios
        groupDf: symbol groups for each ratio
    Output:
        rankDf: dataframe of ranking scores for each symbol on each ratio
    """
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

    """computeAR
    Description:
        compute the individuals returns and group average returns
    Input:
        groupDf: symbol groups for each ratio
        benchmark: benchmark for evaluating return
    Output:
        ArDf: individuals returns
        groupAR: group average returns
    """
    def computeAR(self, groupDf, benchmark):
        ArDf = self.preprocess.retrieve_return()
        benchmarkAR = self.preprocess.retrieve_benchmark_change(benchmark)
        ArDf["return"] = ArDf["return"]/benchmarkAR - 1.0
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
        
    """visualizeGroupAR
    Description:
        plot the correlation between group average return and ratios
    Input:
        groupAR:
            group average return for each ratio
    """    
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
            axes.set_ylim([-0.05, 0.05])
        plt.show()
        
    """visualizeTrainValidate
    Description: 
        visualize the effectiveness of the model
    """    
    def visualizeTrainValidate(self, train, validate):
        plt.close()
        x_1 = train["score"]
        y_1 = train["return"]
        x_2 = validate["score"]
        y_2 = validate["return"]
        plt.plot(x_1, y_1, 'b.', label="train")
        plt.plot(x_2, y_2, 'r.', label="validate")
        plt.draw()
        plt.show(block=False)
        
    """computeCorrCoef
    Description:
        compute correlation coefficient for each ratios and drop the ratios 
        with p_value higher than the model requirement
    Input:
        groupAR: group average return for each ratio
        coefDf: remaining ratios slope z-score
    """    
    def computeCorrCoef(self, groupAR):
        coefDf = pd.DataFrame(index=groupAR.columns)
        coefDf["corrcoef"] = 0.0
        for column in groupAR:
            x = [i for i in range(self.groupNum)]
            y = groupAR[column].astype(float)
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            if p_value < self.p_value:
                # looking for definitive strong slope
                coefDf["corrcoef"][column] = slope/std_err
            else:
                coefDf.drop([column], axis=0, inplace=True)
                #print("remove insignificant column:", "%16s"%column," (p value: %f)"%p_value)
        self.coefficient = coefDf
        return coefDf
        
    """computeSymbolScore
    Description: compute overall score from all ratio regression and rank symbol
    Input:
        coefDf: dataframe of slope strength
        rankDf: dataframe of ranking scores for each symbol on each ratio
        Ar: return of each symbol
    """    
    def computeSymbolScore(self, coefDf, rankDf, Ar=None):
        newRankDf = pd.DataFrame(0.0, index=rankDf.index, columns=rankDf.columns)
        dropList1 = [col for col in rankDf.columns if col not in coefDf.index]
        dropList2 = [ind for ind in coefDf.index if ind not in rankDf.columns]
        rankDf.drop(dropList1, axis=1, inplace=True)
        coefDf.drop(dropList2, inplace=True)
        coefDf = np.sign(coefDf) * coefDf.pow(self.scoreOrder).abs()
        # normalize scores
        scaler = preprocessing.MinMaxScaler()
        newRankDf["score"] = scaler.fit_transform(rankDf.dot(coefDf))
        if Ar is not None:
            scoreDf = newRankDf['score'].to_frame().join(100*Ar['return'], how='left')
            return scoreDf.sort_values('score', ascending=False)
        return newRankDf['score'].sort_values(ascending=False)
        
    """
    TRAIN
    """
    def train(self, benchmark, trainset=None):
        if trainset is not None:
            data = trainset
        else:
            data = self.preprocess.get_data(dataType='filled', lag = True)
        groups = self.group(data)
        ar, gar = self.computeAR(groups, benchmark)
        #self.visualizeGroupAR(gar)
        coefDf = self.computeCorrCoef(gar)
        rankDf = self.computeRank(data, groups)
        return self.computeSymbolScore(coefDf, rankDf, ar)

    """
    VALIDATE
    """
    def validate(self, benchmark, validateset):
        testGroups = self.group(validateset)
        ar, gar = self.computeAR(testGroups, benchmark)
        testRankDf = self.computeRank(validateset, testGroups)
        return self.computeSymbolScore(self.coefficient, testRankDf, ar)
        
    """
    TRAIN AND VALIDATE
    """
    def train_validate(self, benchmark):
        trainSet, validateSet = self.preprocess.get_data(dataType='filled', lag=True, dset="train_validate")
        t = self.train(benchmark, trainset=trainSet)
        v = self.validate(benchmark, validateset = validateSet)
        #self.visualizeTrainValidate(t, v)
        return t, v
        
    """
    PREDICT
    """
    def predict(self):
        newdata = self.preprocess.get_data(dataType='filled', lag=False)
        if self.coefficient.empty:
            raise Exception("model coefficient not fitted!")
        newGroupDf = self.group(newdata)
        newRankDf = self.computeRank(newdata, newGroupDf)
        return self.computeSymbolScore(self.coefficient, newRankDf)
