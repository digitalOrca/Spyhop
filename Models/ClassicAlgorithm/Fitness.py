#!/usr/bin/python3

import numpy as np
from scipy import stats
from LinearRegression import LinearRegression
from PCAImpl import PCAImpl
from KMeansImpl import KMeansImpl
from SectorNorm import SectorNorm
from colored import fg, bg, attr

def eval_KMeansImpl(aggregateDf):
    for cluster in range(aggregateDf["label"].max()+1):
        cRet = aggregateDf[aggregateDf["label"]==cluster]["return"]
        avgRet = cRet.mean(skipna=True)
        stdevRet = cRet.std(skipna=True)
        z_value = avgRet/stdevRet
        probablity = stats.norm.cdf(z_value)
        
        #print("cluster:",cluster,\
        #      "average return:{: 6f}".format(avgRet),\
        #      "standard deviation:{: 2.6f}".format(stdevRet),\
        #      "z-value:{: 6f}".format(z_value), \
        #      "probablity:{: 6f}".format(probablity)) #TODO: fix alignment
              
        if cluster == 0:
            bestCluster = cluster
            highest_z_value = z_value
            highest_probability = probablity
        if z_value > highest_z_value:
            bestCluster = cluster
            highest_z_value = z_value
            highest_probability = probablity
              
    return bestCluster, highest_probability


def eval_LinearRegression(aggregateDf):
    aggregateDf = aggregateDf.dropna(how="any")
    slope, intercept, r_value, p_value, std_err = stats.linregress(aggregateDf["score"], aggregateDf["return"])
    variance = aggregateDf["score"].apply(lambda x: np.square(x-(x*slope+intercept)))
    std_err_est = np.sqrt(variance.sum()/len(aggregateDf))
    head = aggregateDf["score"].max() * slope + intercept
    z_value = head / std_err_est
    tail_probability = stats.norm.cdf(z_value)    
    return tail_probability
    
    
def eval_SectorNorm():
    # This statistical model does not require validation
    pass
    

def eval_Combination(aggregateDf):
    leaders = aggregateDf.head(n=20)["return"]
    mean = leaders.mean(skipna=True)
    stdev = leaders.std(skipna=True)
    z_value = mean/stdev
    return stats.norm.cdf(z_value)

  
def computeFitness(lr, kmi):
    print("Fitting LinearRegression Model ...")
    lr_train, lr_validate = lr.train_validate("snp500")
    lr_predict = lr.predict()
    print("Fitting KMeans Model ...")
    kmi_train, kmi_validate = kmi.train_validate()
    kmi_predict = kmi.predict()
    #print("Fitting SectorNorm Model ...")
    #sn = SectorNorm().computeSectorReturnProbability()
    
    # evaluate KMeans model
    aggregateTrainDf = lr_train.join(kmi_train['label'], how='inner')
    trainCluster, trainProbability = eval_KMeansImpl(aggregateTrainDf)
    aggregateValidateDf = lr_validate.join(kmi_validate['label'], how='inner')
    validateCluster, validateProbability = eval_KMeansImpl(aggregateValidateDf)
    kmeans_accuracy = min(trainProbability, validateProbability)-abs(trainProbability-validateProbability)
    if trainCluster != validateCluster:
        print("%s%sInconsistent KMeans clustering!%s"%(fg("red"), attr("bold"), attr("reset")))
        kmeans_accuracy = -1.0
    # evaluate LinearRegression model    
    train_head_probability = eval_LinearRegression(aggregateTrainDf)
    validate_head_probability = eval_LinearRegression(aggregateValidateDf)
    lingres_accuracy = min(train_head_probability, validate_head_probability)-abs(train_head_probability-validate_head_probability)
    # evaluate overall
    train_top = eval_Combination(aggregateTrainDf)
    validate_top = eval_Combination(aggregateValidateDf)
    combined_accuracy = min(train_top, validate_top)-abs(train_top-validate_top)
    
    # compute fitness score
    fitness = kmeans_accuracy + lingres_accuracy + 2.0 * combined_accuracy
    
    print("%s------------------------[KMeansImpl]-------------------------"%(fg("yellow")))
    print("train:   ", trainProbability)
    print("validate:", validateProbability)
    print("---------------------[LinearRegression]----------------------")
    print("train:   ", train_head_probability)
    print("validate:", validate_head_probability)
    print("--------------------------[Overall]--------------------------")
    print("train:   ", train_top)
    print("validate:", validate_top)
    print("-------------------------------------------------------------%s"%(attr("reset")))
    
    return fitness, (kmeans_accuracy, lingres_accuracy, combined_accuracy)
