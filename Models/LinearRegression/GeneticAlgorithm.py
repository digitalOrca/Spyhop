#!/usr/bin/python3

"""GeneticAlgorithm.py
Description:
    run genetic algorithm to optimize LinearRegression model parameters
"""

import os
import sys
import math
import random
import traceback
from datetime import date
import EvolutionCore as ec
import ModelRunner as mr
from colored import fg, bg, attr

"""pairing
Description:
    pairing two from surviving population to create new individuals
Input:
    survivers: list of survivers
Output:
    pair[0], pair[1]: selected pair for mating

"""
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

"""replenish
Description:
    replenish lost individuals through mating between survivers
Input:
    survivers: list of survivers
Output:
    bodyCount: number of dead inviduals from previous generation
"""
def replenish(survivers, bodyCount):
    for i in range(bodyCount):
        mother, father = pairing(survivers)
        newName = ec.birth(mother, father)
        print(newName)

"""fitnessTest
Description: 
    run model for entire population, eliminate lowest performer, malformed and
    return the invidual with highest fitness score
Output:
    champion: the best long-term performer
"""
def fitnessTest():
    population = [ f.split(".")[0] for f in os.listdir("./progression/population")]
    malformed = []
    fitnessTracker = {}
    popSize = len(population)
    champion = ""
    championScore = 0
    championLevel = 0
    for index, name in enumerate(population):
        print("\n-------------------------------------------------------------")
        print("Evaluating %s in progress[%s/%s]..."%(name, index+1, popSize))
        traits = ec.get_traits(name)
        result = traits["Result"]
        if result["latest_update"] != date.today().strftime("%Y-%m-%d"):
            try:
                fitness = mr.computeAccuracy(name)
                level = result["level"] + 1
            except Exception as e:
                print("%s%sError:"%(fg("red"),attr("bold")),str(e),"%s"%(attr("reset")))
                #traceback.print_exc()
                malformed.append(name)
                continue
        else:
            print("models fitness score recorded...")
            fitness = result["fitness"]
            level = result["level"]
        if math.isnan(fitness):
            malformed.append(name)
        else:
            fitnessTracker[name] = (fitness, level)
            if level > championLevel:
                champion = name
                championLevel = level
                championScore = fitness
            elif level == championLevel:
                if fitness >= championScore:
                    champion = name
                    championLevel = level
                    championScore = fitness
                    
    print("====================[GRADEBOOK]====================")
    rankedPairs =sorted(fitnessTracker.items(), key=lambda x:x[1][0], reverse=True)
    for name, (fitness, level) in rankedPairs:
        print("%s{:>24}: %sfitness:{:5.6f}   %slevel:{:>2}%s".format(name,fitness,level)\
              %(attr("bold"), fg("green"), fg("cyan"), attr("reset")))
    print("======================[WEAK]=======================")
    eliminated = [pair[0] for pair in rankedPairs[-10:]]
    ec.eliminate(eliminated)
    for name in eliminated:
        fitnessTracker.pop(name)
    print("====================[MALFORMED]====================")
    ec.eliminate(malformed)
    print("=================[NEW GENERATION]==================")
    bodyCount = len(eliminated) + len(malformed)
    survivers = list(fitnessTracker.keys())
    replenish(survivers, bodyCount)
    return champion
    
"""promoteChampion
Description:
    copy the champion to Champion directory
Input:
    champion: the name of the champion
"""    
def promoteChampion(champion):
    os.system("rm -f ./progression/champions/*")
    os.system("cp ./progression/population/%s.json ./progression/champions/"\
               %champion)
    
"""
MAIN
"""
if __name__=="__main__":
    try:
        iteration = int(sys.argv[1])
    except:
        iteration = 1
    for i in range(iteration):
        print("\n\n%s%s======================== GENERATION" % (fg("green"), attr("bold")), i+1,
              "=======================%s" % (attr("reset")))
        champion = fitnessTest()
        print("====================[CHAMPION]=====================")
        print(champion)
        promoteChampion(champion)
