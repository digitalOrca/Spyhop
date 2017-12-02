#!/usr/bin/python3

"""ModelRunner.py
Description:
    build LinearRegression model from a json profile and run it
"""

import sys
import json
from datetime import date
from collections import OrderedDict
from LinearRegression import LinearRegression
from Fitness import computeFitness
import EvolutionCore as ec
from colored import fg, bg, attr

"""extractParameter
Description:
    extract parameters from json profile and return as a tuple
Input:
    traits: json parameter profile
    model: json section name, the model name
    paramList: list of parameters to be retrieved
Output:
    parameterTuple: parameter tuple
"""
def extractParameter(traits, model, paramList) :
    parameterPairs = {}
    parameterTuple = ()
    
    for parameter in traits["Constant"]:
        parameterPairs[parameter["parameter"]] = parameter["value"]
        
    for parameter in traits[model]:
        parameterPairs[parameter["parameter"]] = parameter["value"]
     
    for parameter in paramList:
        value = parameterPairs[parameter]
        parameterTuple += (value,)
    
    return parameterTuple

"""loadParameters
Description:
    load parameters into a LinearRegression instance
Input:
    name: the name of the json profile
Output:
    lr: an instance of LinearRegression model
""" 
def loadParameters(name):
    traits = ec.getTraits(name)
    lr_paramList = ["lag", "density", "groupNum", "scoreOrder", "retMin", "retMax", "p_value"]
    lag, density, groupNum, scoreOrder, retMin, retMax, p_value = extractParameter(traits, "LinearRegression", lr_paramList)
    lr = LinearRegression(lag, density, groupNum, scoreOrder, retMin, retMax, p_value)
    return lr
    
"""computeAccuracy
Description:
    pass through the fitness score and update the json profile
Input:
    name: the name of the json profile
Output:
    fitness: fitness score
"""
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
