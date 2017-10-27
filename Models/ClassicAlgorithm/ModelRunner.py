#!/usr/bin/python

import sys
import json
from collections import OrderedDict
from LinearRegression import LinearRegression
from PCAImpl import PCAImpl
from KMeansImpl import KMeansImpl
from Fitness import computeFitness
import EvolutionCore as ec
from Fitness import computeCorrelation

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
    traits["Result"]["data_start_date"] = str(data_start_date)
    traits["Result"]["data_end_date"] = str(data_end_date)
    traits["Result"]["predict_start_date"] = lr.preprocess.prdate
    traits["Result"]["fitness"] = fitness
    traits["Result"]["details"]["kmeans_accuracy"] = kmeans_accuracy
    traits["Result"]["details"]["lingres_accuracy"] = lingres_accuracy
    traits["Result"]["details"]["combined_accuracy"] = combined_accuracy
    ec.save(traits, name)
    return fitness
    
#t = getTraits()
#print extractParameter(t, "PCA", ["lag", "density", "retention", "n_components"])
#computeAccuracy("Jackie_Lewis")
