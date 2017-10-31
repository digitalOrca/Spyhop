#!/usr/bin/python3

import sys
import json
from datetime import date
from collections import OrderedDict
from LinearRegression import LinearRegression
from PCAImpl import PCAImpl
from KMeansImpl import KMeansImpl
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
    
    pca_paramList = ["density", "retention", "n_components", "copy", "whiten", "svd_solver", "tol", "iterated_power", "random_state"]
    density, retention, n_components, copy, whiten, svd_solver, tol, iterated_power, random_state = extractParameter(traits, "PCA", pca_paramList)
    pcai = PCAImpl(density, retention, n_components, copy, whiten, svd_solver, tol, iterated_power, random_state)
    
    kmi_paramList = ["lag", "density", "dimReductAlgo", "n_clusters", "init", "n_init", "max_iter", "tol", "precompute_distances", "verbose", "random_state", "copy_x", "n_jobs", "algorithm"]
    lag, density, dummy_instance, n_clusters, init, n_init, max_iter, tol, precompute_distances, verbose, random_state, copy_x, n_jobs, algorithm = extractParameter(traits, "KMeans", kmi_paramList)
    kmi = KMeansImpl(lag, density, pcai, n_clusters, init, n_init, max_iter, tol, precompute_distances, verbose, random_state, copy_x, n_jobs, algorithm)
    
    return lr, kmi
    

def computeAccuracy(name):
    traits = ec.getTraits(name)
    lr, kmi = loadParameters(name)
    fitness, (kmeans_accuracy, lingres_accuracy, combined_accuracy) = computeFitness(lr, kmi)
    data_start_date = lr.preprocess.frdate
    data_end_date = lr.preprocess.prdate
    
    result = traits["Result"]
    prev_count = result["update_count"]
    print("%s%slevel: %s"%(fg("cyan"),attr("bold"),prev_count+1),attr("reset"))
    w1 = 1.0 / (prev_count + 1.0)
    w2 = 1.0 - w1
    today = date.today().strftime("%Y-%m-%d")
    prev_fitness = result["fitness"]
    prev_kmeans_accuracy = result["details"]["kmeans_accuracy"]
    prev_lingres_accuracy = result["details"]["lingres_accuracy"]
    prev_combined_accuracy = result["details"]["combined_accuracy"]
    
    traits["Result"]["update_count"] = prev_count + 1
    traits["Result"]["latest_update"] = today
    if traits["Result"]["data_start_date"] is None:
        traits["Result"]["data_start_date"] = str(data_start_date)
    if traits["Result"]["data_end_date"] is None:
        traits["Result"]["data_end_date"] = str(data_end_date)
    if traits["Result"]["predict_start_date"] is None:
        traits["Result"]["predict_start_date"] = lr.preprocess.prdate
    
    traits["Result"]["fitness"] = w1*fitness + w2*prev_fitness
    traits["Result"]["details"]["kmeans_accuracy"] = w1*kmeans_accuracy + w2*prev_kmeans_accuracy
    traits["Result"]["details"]["lingres_accuracy"] = w1*lingres_accuracy + w2*prev_lingres_accuracy
    traits["Result"]["details"]["combined_accuracy"] = w1*combined_accuracy + w2*prev_combined_accuracy
    
    ec.save(traits, name)
    return fitness
    
#t = getTraits()
#print extractParameter(t, "PCA", ["lag", "density", "retention", "n_components"])
#computeAccuracy("Jackie_Lewis")
