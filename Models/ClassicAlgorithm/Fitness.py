#!/usr/bin/python3

import numpy as np
from scipy import stats
from LinearRegression import LinearRegression
from PCAImpl import PCAImpl
from KMeansImpl import KMeansImpl
from SectorNorm import SectorNorm
from colored import fg, bg, attr

def aggregateResults(results):
    iterResults = iter(results)
    df = next(iterResults).to_frame()
    for result in iterResults:
        df = df.join(result, how="inner")
    return df
    

def eval_KMeansImpl(aggregateDf):
    aggregateDf.dropna(axis=0, how="any", inplace=True)
    aggregateDf["cluster"] = 0.0
    for cluster in range(aggregateDf["label"].max()+1):
        mask = aggregateDf["label"]==cluster
        cRet = aggregateDf[mask]["return"]
        if cRet.empty:
            raise Exception("validation set does not include all clusters")
        avgRet = cRet.mean(skipna=True)
        stdevRet = cRet.std(skipna=True)
        z_value = avgRet/stdevRet
        probablity = stats.norm.cdf(z_value)
        aggregateDf.loc[mask, "cluster"] = probablity
        if cluster == 0:
            bestCluster = cluster
            worstCluster = cluster
            highest_probability = probablity
            lowest_probability = probablity
        elif probablity > highest_probability:
            bestCluster = cluster
            highest_probability = probablity
        elif probablity < lowest_probability:
            worstCluster = cluster
            lowest_probability = probablity
    diff = highest_probability - lowest_probability
    return (bestCluster, worstCluster), diff, aggregateDf


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
    aggregateDf["overall"] = aggregateDf["score"] + aggregateDf["cluster"]
    sortedOverall = aggregateDf.sort_values("overall", ascending=False)
    leaders = sortedOverall.head(n=20)["return"]
    mean = leaders.mean(skipna=True)
    stdev = leaders.std(skipna=True)
    z_value = mean/stdev
    return stats.norm.cdf(z_value)

  
def computeFitness(lr, kmi): 
    print("Fitting KMeans Model ...")
    kmi_train, kmi_validate = kmi.train_validate()
    kmi_predict = kmi.predict()
    print("Fitting LinearRegression Model ...")
    lr_train, lr_validate = lr.train_validate("snp500")
    lr_predict = lr.predict()
    print("Fitting SectorNorm Model ...")
    sn = SectorNorm().computeSectorReturnProbability()
    
    print("Aggregating results ...")
    aggregateTrainDf = aggregateResults([lr_train["score"], lr_train["return"], \
                                         kmi_train["label"], sn["sector"]])
    aggregateValidateDf = aggregateResults([lr_validate["score"], lr_validate["return"],\
                                            kmi_validate["label"], sn["sector"]])
                                            
    # evaluate KMeans model
    (trainBestCluster, trainWorstCluster), trainDiff, aggregateTrainDf = eval_KMeansImpl(aggregateTrainDf)
    (validateBestCluster, validateWorstCluster), validateDiff, aggregateValidateDf = eval_KMeansImpl(aggregateValidateDf)
    kmeans_accuracy = min(trainDiff, validateDiff)-abs(trainDiff-validateDiff)
    if trainBestCluster != validateBestCluster:
        raise Exception("inconsistent best cluster")
    if trainWorstCluster != validateWorstCluster:
        print("%s%sWarning: inconsistent worst cluster%s"%(fg("red"),attr("bold"),attr("reset")))
        #kmeans_accuracy = -1.0
        
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
    print("train:   ", trainDiff)
    print("validate:", validateDiff)
    print("---------------------[LinearRegression]----------------------")
    print("train:   ", train_head_probability)
    print("validate:", validate_head_probability)
    print("--------------------------[Overall]--------------------------")
    print("train:   ", train_top)
    print("validate:", validate_top)
    print("-------------------------------------------------------------%s"%(attr("reset")))
    
    return fitness, (kmeans_accuracy, lingres_accuracy, combined_accuracy)
