#!/usr/bin/python3

"""EvolutionCore.py
Description:
    core functions for genetic algorithm
"""

import os
import json
import names
import random
from collections import OrderedDict

# relative path of population directory to the genetic algorithm
population_root = "./progression/population/"

"""getTraits
Description:
    load json profile into datastructure
Input:
    name: name of the json profile, default is the template
Output:
    traits: json object
"""
def getTraits(name = None):
    if name == None:
        #TODO: FIX THIS BUG/ THIS IS USED IN BOTH SEEDING AND TRAINING!!!
        template = open("./progression/DNA.json", 'r')
        traits = json.load(template, object_pairs_hook=OrderedDict)
        template.close()
    else:
        f = open(population_root+name+".json", "r")
        traits = json.load(f, object_pairs_hook=OrderedDict)
        f.close()
    return traits

"""mutBool
Description:
    boolean value mutation
"""
def mutBool():
    rand = random.uniform(0, 1)
    return (rand>0.5)
    
"""mutInt
Description:
    integer value mutation
"""  
def mutInt(minVal, maxVal):
    newInt = random.randint(minVal, maxVal)
    return newInt
    
"""mutFloat
Description:
    float value mutation
"""    
def mutFloat(minVal, maxVal):
    newFloat = random.uniform(minVal, maxVal)
    return newFloat
    
"""mutStr
Description:
    string value mutation
"""    
def mutStr(option):
    l = len(option)
    index = random.randint(0,l-1)
    return option[index]
    
"""mutate
Description:
    mutate a given set of traits at a given mutation rate
Input:
    traits: json object representing traits
    mutationRate: mutation rate
Output:
    traits: mutated traits
"""    
def mutate(traits, mutationRate):
    for model in traits:
        if model == "Constant" or model == "Result":
            continue
        else:
            for parameter in traits[model]:
                mutable = parameter["mutable"]
                if mutable == True:
                    if random.uniform(0,1) < mutationRate:
                        datatype = parameter["type"]
                        if datatype == "int":
                            parameter["value"] = mutInt(parameter["min"], parameter["max"])
                        elif datatype == "float":
                            parameter["value"] = mutFloat(parameter["min"], parameter["max"])
                        elif datatype == "bool":
                            parameter["value"] = mutBool()
                        elif datatype == "str":
                            parameter["value"] = mutStr(parameter["option"])
                        else:
                            pass
    return traits
    
"""mate
Description:
    mate two traits and create a new traits
Input:
    traits1, traits2: parent traits
Output:
    newTraits: child trait
"""    
def mate(traits1, traits2):
    newTraits = getTraits()
    for model in traits1:
        if model == "Constant" or model == "Result":
            continue
        else:
            for parameter, parameter1, parameter2 in zip(newTraits[model], traits1[model], traits2[model]):
                mutable = parameter["mutable"]
                if mutable == True:
                    if random.uniform(0,1) < 0.5:
                        parameter["value"] = parameter1["value"]
                    else:
                        parameter["value"] = parameter2["value"]
    return newTraits

"""save
Description:
    save a given trait as a json file under a given name
"""
def save(traits, name=None):
    if name is None:
        name = names.get_full_name().replace(' ','_')
    f = open(population_root+name+".json", "w")
    f.seek(0)
    json.dump(traits, f, indent=4)
    f.truncate()
    f.close()

"""birth
Description:
    generate new traits under new name from two parents
Input:
    parent1, parent2: parents names
Output:
    newName: child name
"""
def birth(parent1, parent2):
    traits1 = getTraits(parent1)
    traits2 = getTraits(parent2)
    newTraits = mate(traits1, traits2)
    newTraits = mutate(newTraits, 0.05) #TODO:DEFINE MUTATION RATE IN CONFIG
    #newName = parent1.split("_")[0]+"_"+parent2.split("_")[1]
    newName = names.get_full_name().replace(' ','_')
    save(newTraits, newName)
    return newName
    
"""eliminate
Description:
    eliminate a given list of weak models from population
Input:
    losers: list of models to be eliminated
"""
def eliminate(losers):
    for name in losers:
        print("Eliminate:", name)
        os.system("rm -f %s%s.json"%(population_root,name))
    
#t1 = getTraits("Denis_Garza")
#t2 = getTraits("David_Stull")
#mate(t1, t2)
#birth("Aaron_Wallace", "Katherine_Denson")
