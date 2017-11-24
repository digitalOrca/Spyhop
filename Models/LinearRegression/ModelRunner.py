#!/usr/bin/python3

import sys
import json
from datetime import date
from collections import OrderedDict
from LinearRegression import LinearRegression
from Fitness import computeFitness
import EvolutionCore as ec
from colored import fg, bg, attr

def extractParameter(traits, model, order) :
    parameterPairs = {}
    parameterTuple = ()
    
    for parameter in traits["Constant"]:
        parameterPairs[parameter["parameter"]] = parameter["value"]
        
    for parameter in traits[model]:
        parameterPairs[parameter["parameter"]] = parameter["value"]
     
    for parameter in order:
        value = parameterPairs[parameter]
        parameterTuple += (value,)
    
    return parameterTuple

 
def loadParameters(name):
    traits = ec.getTraits(name)
    lr_paramList = ["lag", "density", "groupNum", "scoreOrder", "retMin", "retMax", "p_value"]
    lag, density, groupNum, scoreOrder, retMin, retMax, p_value = extractParameter(traits, "LinearRegression", lr_paramList)
    lr = LinearRegression(lag, density, groupNum, scoreOrder, retMin, retMax, p_value)
    return lr
    

def computeAccuracy(name):
    traits = ec.getTraits(name)
    lr = loadParameters(name)
    fitness = computeFitness(lr)
    data_start_date = lr.preprocess.frdate
    data_end_date = lr.preprocess.prdate
    
    result = traits["Result"]
    prev_count = result["level"]
    print("%s%slevel: %s"%(fg("cyan"),attr("bold"),prev_count+1),attr("reset"))
    w1 = 1.0 / (prev_count + 1.0)
    w2 = 1.0 - w1
    today = date.today().strftime("%Y-%m-%d")
    prev_fitness = result["fitness"]
    
    traits["Result"]["level"] = int(prev_count + 1)
    traits["Result"]["latest_update"] = today
    if traits["Result"]["data_start_date"] is None:
        traits["Result"]["data_start_date"] = str(data_start_date)
    if traits["Result"]["data_end_date"] is None:
        traits["Result"]["data_end_date"] = str(data_end_date)
    if traits["Result"]["predict_start_date"] is None:
        traits["Result"]["predict_start_date"] = lr.preprocess.prdate
    
    traits["Result"]["fitness"] = w1*fitness + w2*prev_fitness
    
    ec.save(traits, name)
    return fitness
