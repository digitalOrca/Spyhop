#!/usr/bin/python

import numpy as np
import scipy.stats as st
from LinearRegression import LinearRegression
from PCAImpl import PCAImpl
from KMeansImpl import KMeansImpl

def getBestCluster(aggregateDf):

    for cluster in range(aggregateDf["label"].max()+1):
        cRet = aggregateDf[aggregateDf["label"]==cluster]["return"]
        avgRet = cRet.mean(skipna=True)
        stdevRet = cRet.std(skipna=True)
        z_value = avgRet/stdevRet
        probablity = st.norm.cdf(z_value)
        
        print("cluster:",cluster,\
              "average return:{: 6f}".format(avgRet),\
              "standard deviation:{: 2.6f}".format(stdevRet),\
              "z-value:{: 6f}".format(z_value), \
              "probablity:{: 6f}".format(probablity)) #TODO: fix alignment
              
        if cluster == 0:
            bestCluster = cluster
            highest_z_value = z_value
            highest_probability = probablity
        if z_value > highest_z_value:
            bestCluster = cluster
            highest_z_value = z_value
            highest_probability = probablity
              
    return bestCluster, highest_probability


def computeCorrelation(aggregateDf):
    aggregateDf["x"] = list(reversed(range(len(aggregateDf["return"]))))
    aggregateDf = aggregateDf.dropna(how="any")
    return np.corrcoef(aggregateDf["x"], aggregateDf["return"])[0][1]
    

def computeTopReturn(aggregateDf):
    leaders = aggregateDf.head(n=20)["return"]
    mean = leaders.mean(skipna=True)
    stdev = leaders.std(skipna=True)
    z_value = mean/stdev
    return st.norm.cdf(z_value)

  
def computeFitness(lr, kmi):
    lr_train, lr_validate = lr.train_validate("snp500")
    lr_predict = lr.predict()
    
    kmi_train, kmi_validate = kmi.train_validate()
    kmi_predict = kmi.predict()
    
    print("==========Train==========")
    aggregateTrainDf = lr_train.join(kmi_train['label'], how='inner')
    trainCluster, trainProbability = getBestCluster(aggregateTrainDf)
    print("trainCluster:", trainCluster)
    print("trainProbability", trainProbability)
    print("==========Validate==========")
    aggregateValidateDf = lr_validate.join(kmi_validate['label'], how='inner')
    validateCluster, validateProbability = getBestCluster(aggregateValidateDf)
    
    kmeans_accuracy = min(trainProbability, validateProbability)-abs(trainProbability-validateProbability)
    
    if trainCluster != validateCluster:
        print("Inconsistent KMeans clustering!")
        avgProbability = -1.0
        
    train_coef = computeCorrelation(aggregateTrainDf)
    validate_coef = computeCorrelation(aggregateValidateDf)
    lingres_accuracy = min(train_coef, validate_coef)-abs(train_coef-validate_coef)
    
    train_top = computeTopReturn(aggregateTrainDf)
    validate_top = computeTopReturn(aggregateValidateDf)
    combined_accuracy = min(train_top, validate_top)-abs(train_top-validate_top)
    
    #adjust fitness score weights
    fitness = kmeans_accuracy + lingres_accuracy + 2.0 * combined_accuracy
    print("=============================================")
    print("trainCluster", trainCluster)
    print("validateCluster", validateCluster)
    print("---------------------------------------------")
    print("trainProbability:", trainProbability)
    print("validateProbability", validateProbability)
    print("---------------------------------------------")
    print("train_coef", train_coef)
    print("validate_coef", validate_coef)
    print("---------------------------------------------")
    print("train_top", train_top)
    print("validate_top", validate_top)
    print("=============================================")
    
    return fitness, (kmeans_accuracy, lingres_accuracy, combined_accuracy)
