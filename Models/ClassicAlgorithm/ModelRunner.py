#!/usr/bin/python

import sys
import json
from collections import OrderedDict
from LinearRegression import LinearRegression
from PCAImpl import PCAImpl
from KMeansImpl import KMeansImpl

def getTraits():
    filename = sys.argv[1] + ".json"
    path = "/home/meng/Projects/NeuroTrader/Models/GeneticProgression/Alive/"
    f = open(path+filename, "r")
    traits = json.load(f, object_pairs_hook=OrderedDict)
    f.close()
    return traits
    

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

 
def loadParameters():
    
    traits = getTraits()
    lr_paramList = ["lag", "density", "groupNum", "scoreOrder", "retMin", "retMax", "p_value"]
    lag, density, groupNum, scoreOrder, retMin, retMax, p_value = extractParameter(traits, "LinearRegression", lr_paramList)
    lr = LinearRegression(lag, density, groupNum, scoreOrder, retMin, retMax, p_value)
    #lr_train, lr_validate = lr.train_validate("snp500")
    #lr_predict = lr.predict()
    
    pca_paramList = ["density", "retention", "n_components", "copy", "whiten", "svd_solver", "tol", "iterated_power", "random_state"]
    density, retention, n_components, copy, whiten, svd_solver, tol, iterated_power, random_state = extractParameter(traits, "PCA", pca_paramList)
    pcai = PCAImpl(density, retention, n_components, copy, whiten, svd_solver, tol, iterated_power, random_state)
    
    kmi_paramList = ["lag", "density", "dimReductAlgo", "n_clusters", "init", "n_init", "max_iter", "tol", "precompute_distances", "verbose", "random_state", "copy_x", "n_jobs", "algorithm"]
    lag, density, dummy_instance, n_clusters, init, n_init, max_iter, tol, precompute_distances, verbose, random_state, copy_x, n_jobs, algorithm = extractParameter(traits, "KMeans", kmi_paramList)
    kmi = KMeansImpl(lag, density, pcai, n_clusters, init, n_init, max_iter, tol, precompute_distances, verbose, random_state, copy_x, n_jobs, algorithm)
    #kmi_train, kmi_validate = kmi.train_validate()
    #kmi_predict = kmi.predict()
    
#t = getTraits()
#print extractParameter(t, "PCA", ["lag", "density", "retention", "n_components"])
loadParameters()
