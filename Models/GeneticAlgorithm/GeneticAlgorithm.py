#!/usr/bin/python3

import os
import math
import random
import traceback
from datetime import date
import EvolutionCore as ec
import ModelRunner as mr
from colored import fg, bg, attr

def pairing(survivers):
    if len(survivers) < 2:
        raise Exception("not enough survivers for pairing")
    pair = []
    population = len(survivers)
    while len(pair) < 2:
        for i in range(population):
            remain = population-i
            prob = remain/(sum(range(remain+1)))
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
    popSize = len(population)
    for index, name in enumerate(population):
        print("\n-------------------------------------------------------------")
        print("Evaluating %s in progress[%s/%s]..."%(name, index+1, popSize))
        traits = ec.getTraits(name)
        result = traits["Result"]
        if result["latest_update"] != date.today().strftime("%Y-%m-%d"):
            try:
                fitness = mr.computeAccuracy(name)
            except Exception as e:
                print("%s%sError:"%(fg("red"),attr("bold")),str(e),"%s"%(attr("reset")))
                #traceback.print_exc()
                malformed.append(name)
                continue
        else:
            print("models fitness score recorded...")
            fitness = result["fitness"]
            
        if math.isnan(fitness):
            malformed.append(name)
        else:
            fitnessTracker[name] = fitness
    print("==========[GRADEBOOK]==========")
    rankedPairs =sorted(fitnessTracker.items(), key=lambda x:x[1], reverse=True)
    for key, value in rankedPairs:
        print("%s: %s"%(key, value))
    print("============[WEAK]=============")
    eliminated = [pair[0] for pair in rankedPairs[-10:]]
    ec.eliminate(eliminated)
    for name in eliminated:
        fitnessTracker.pop(name)
    print("==========[MALFORMED]==========")
    ec.eliminate(malformed)
    print("=======[NEW GENERATION]========")
    bodyCount = len(eliminated) + len(malformed)
    survivers = list(fitnessTracker.keys())
    replenish(survivers, bodyCount)
    return malformed + eliminated
    

if __name__=="__main__":
    for i in range(50):
        print("\n\n%s%s======================== GENERATION"%(fg("green"),attr("bold")), i+1, "=======================%s"%(attr("reset")))
        population = fitnessTest()
