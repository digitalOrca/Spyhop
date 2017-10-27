#!/usr/bin/python

import os
import random
import traceback
import math
import EvolutionCore as ec
import ModelRunner as mr


def pairing(survivers):
    pair = []
    population = len(survivers)
    while len(pair) < 2:
        for i in range(population):
            remain = float(population-i)
            prob = 2.0/(pow(remain,2)-remain)
            if random.uniform(0,1) <= prob:
                if len(pair) == 0:
                    pair.append(survivers[i])
                    p1 = i
                    break;
                elif i != p1:
                    pair.append(survivers[i])
                    break;
                else:
                    break;
    return pair[0], pair[1]


def replenish(survivers, bodyCount):
    for i in range(bodyCount):
        mother, father = pairing(survivers)
        newName = ec.birth(mother, father)
        print(newName)


def fitnessTest():
    population = [ f.split(".")[0] for f in os.listdir("/home/meng/Projects/NeuroTrader/Models/GeneticProgression/Alive")]
    malformed = []
    fitnessTracker = {}
    for name in population:
        traits = ec.getTraits(name)
        result = traits["Result"]
        if None in [result["data_start_date"], result["data_end_date"], \
                    result["predict_start_date"], result["fitness"], \
                    result["details"]["kmeans_accuracy"], result["details"]["lingres_accuracy"], \
                    result["details"]["combined_accuracy"]]:
            try:
                fitness = mr.computeAccuracy(name)
            except:
                traceback.print_exc()
                malformed.append(name)
                continue
        else:
            fitness = result["fitness"]
        if math.isnan(fitness):
            malformed.append(name)
        else:
            fitnessTracker[name] = fitness
    print("======MALFORMED======")
    ec.eliminate(malformed)
    print("======GRADEBOOK======")
    rankedPairs =sorted(fitnessTracker.items(), key=lambda x:x[1])
    for key, value in rankedPairs:
        print("%s: %s"%(key, value))
    print("======WEAK======")
    eliminated = [pair[0] for pair in rankedPairs[:10]]
    ec.eliminate(eliminated)
    for name in eliminated:
        fitnessTracker.pop(name)
    print("======NEW GENERATION======")
    bodyCount = len(eliminated) + len(malformed)
    survivers = list(fitnessTracker.keys())
    replenish(survivers, bodyCount)
    

for i in range(5):
    print("GENERATION ", i, "==========================================\n\n")
    fitnessTest()
