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
    tail = aggregateDf["score"].min() * slope + intercept
    z_value_head = head / std_err_est
    z_value_tail = tail / std_err_est
    #probability of head larger than 0
    head_probability = stats.norm.cdf(z_value_head)
    #probability of tail smaller than 0
    tail_probability = 1.0 - stats.norm.cdf(z_value_tail)
    return head_probability, tail_probability
    

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
    train_prob_h, train_prob_t = eval_LinearRegression(lr_train)
    validate_prob_h, validate_prob_t = eval_LinearRegression(lr_validate)
    train_probability = (train_prob_h + train_prob_t)/2
    validate_probability = (validate_prob_h + validate_prob_t)/2
    #print(train_probability,",",validate_probability,",",train_probability,",",validate_probability)
    lingres_accuracy = min(train_probability, validate_probability)-abs(train_probability-validate_probability)
    
    # compute fitness score
    fitness = lingres_accuracy
    
    print("%s---------------------[LinearRegression]----------------------"%(fg("yellow")))
    print("train_low:{:0.5f},  train_high:{:0.5f}".format(train_prob_t, train_prob_h))
    print("valid_low:{:0.5f},  valid_high:{:0.5f}".format(validate_prob_t, validate_prob_h))
    print("-------------------------------------------------------------%s"%(attr("reset")))
    
    return fitness
