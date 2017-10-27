#!/usr/bin/python

import os
import json
import names
import random
from collections import OrderedDict

def getTraits(name = None):
    if name == None:
        template = open("/home/meng/Projects/NeuroTrader/Models/GeneticProgression/GeneticTemplate.json", 'r')
        traits = json.load(template, object_pairs_hook=OrderedDict)
        template.close()
    else:
        f = open("/home/meng/Projects/NeuroTrader/Models/GeneticProgression/Alive/"+name+".json", "r")
        traits = json.load(f, object_pairs_hook=OrderedDict)
        f.close()
    return traits


def mutBool():
    rand = random.uniform(0, 1)
    return (rand>0.5)
    
    
def mutInt(minVal, maxVal):
    newInt = random.randint(minVal, maxVal)
    return newInt
    
    
def mutFloat(minVal, maxVal):
    newFloat = random.uniform(minVal, maxVal)
    return newFloat
    
    
def mutStr(option):
    l = len(option)
    index = random.randint(0,l-1)
    return option[index]
    
    
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


def save(traits, name=None):
    if name is None:
        name = names.get_full_name().replace(' ','_')
    path = "/home/meng/Projects/NeuroTrader/Models/GeneticProgression/Alive/"
    f = open(path+name+".json", "w")
    f.seek(0)
    json.dump(traits, f, indent=4)
    f.truncate()
    f.close()


def birth(parent1, parent2):
    traits1 = getTraits(parent1)
    traits2 = getTraits(parent2)
    newTraits = mate(traits1, traits2)
    newTraits = mutate(newTraits, 0.05) #TODO:DEFINE MUTATION RATE IN CONFIG
    #newName = parent1.split("_")[0]+"_"+parent2.split("_")[1]
    newName = names.get_full_name().replace(' ','_')
    save(newTraits, newName)
    return newName
    

def eliminate(losers):
    for name in losers:
        print("Eliminate:", name)
        os.system("rm -f /home/meng/Projects/NeuroTrader/Models/GeneticProgression/Alive/%s.json"%name)
    
#t1 = getTraits("Denis_Garza")
#t2 = getTraits("David_Stull")
#mate(t1, t2)
#birth("Aaron_Wallace", "Katherine_Denson")
