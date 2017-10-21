#!/usr/bin/python

import scipy.stats as st
from LinearRegression import LinearRegression
from KMeansImpl import KMeansImpl

def getBestCluster(aggregateTrainDf):

    for cluster in range(aggregateTrainDf["label"].max()+1):
        cRet = aggregateTrainDf[aggregateTrainDf["label"]==cluster]["return"]
        avgRet = cRet.mean(skipna=True)
        stdevRet = cRet.std(skipna=True)
        z_value = avgRet/stdevRet
        probablity = st.norm.cdf(z_value)
        
        print "cluster:",cluster,\
              "average return:{: 6f}".format(avgRet),\
              "standard deviation:{: 2.6f}".format(stdevRet),\
              "z-value:{: 6f}".format(z_value), \
              "probablity:{: 6f}".format(probablity) #TODO: fix alignment
              
        if cluster == 0:
            highest_z_value = z_value
        if z_value > highest_z_value:
            bestCluster = cluster
              
    return bestCluster, probablity


def computeFitness():
    lr = LinearRegression()
    lr_train, lr_validate = lr.train_validate("snp500")
    lr_predict = lr.predict()
    
    kmi = KMeansImpl(dimReductAlgo='PCA')
    kmi_train, kmi_validate = kmi.train_validate()
    kmi_predict = kmi.predict()
    
    aggregateTrainDf = lr_train.join(kmi_train['label'], how='inner')
    trainCluster, trainProbability = getBestCluster(aggregateTrainDf)

    aggregateValidateDf = lr_validate.join(kmi_validate['label'], how='inner')
    validateCluster, validateProbability = getBestCluster(aggregateValidateDf)
    
    if trainCluster != validateCluster:
        print "Inconsistent KMeans clustering!"
        return -1.0
    else:
        return validateProbability


vp = computeFitness()
print "Fitness score:",vp
