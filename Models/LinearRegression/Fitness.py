#!/usr/bin/python3

import numpy as np
from scipy import stats
from LinearRegression import LinearRegression
from colored import fg, bg, attr


def eval_LinearRegression(aggregateDf):
    aggregateDf = aggregateDf.dropna(how="any")
    slope, intercept, r_value, p_value, std_err = stats.linregress(aggregateDf["score"], aggregateDf["return"])
    variance = aggregateDf["score"].apply(lambda x: np.square(x-(x*slope+intercept)))
    std_err_est = np.sqrt(variance.sum()/len(aggregateDf))
    head = aggregateDf["score"].max() * slope + intercept
    z_value = head / std_err_est
    tail_probability = stats.norm.cdf(z_value)    
    return tail_probability
    

def eval_Combination(aggregateDf):
    aggregateDf["overall"] = aggregateDf["score"] + aggregateDf["cluster"]
    sortedOverall = aggregateDf.sort_values("overall", ascending=False)
    leaders = sortedOverall.head(n=20)["return"]
    mean = leaders.mean(skipna=True)
    stdev = leaders.std(skipna=True)
    z_value = mean/stdev
    return stats.norm.cdf(z_value)

  
def computeFitness(lr):
    print("Fitting LinearRegression Model ...")
    lr_train, lr_validate = lr.train_validate("snp500")
    lr_predict = lr.predict()
    
    # evaluate LinearRegression model    
    train_head_probability = eval_LinearRegression(lr_train)
    validate_head_probability = eval_LinearRegression(lr_validate)
    #print(train_head_probability,",",validate_head_probability,",",train_head_probability,",",validate_head_probability)
    lingres_accuracy = min(train_head_probability, validate_head_probability)-abs(train_head_probability-validate_head_probability)
    
    # compute fitness score
    fitness = lingres_accuracy
    
    print("%s---------------------[LinearRegression]----------------------"%(fg("yellow")))
    print("train:   ", train_head_probability)
    print("validate:", validate_head_probability)
    print("-------------------------------------------------------------%s"%(attr("reset")))
    
    return fitness
