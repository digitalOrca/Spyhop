#!/usr/bin/python

import ast
import names
import random
import json
from collections import OrderedDict

def loadTemplate():
    template = open("/home/meng/Projects/NeuroTrader/Models/GeneticProgression/GeneticTemplate.json", 'r')
    ancestor = json.load(template, object_pairs_hook=OrderedDict)
    template.close()
    return ancestor

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
    
def mutate(ancestor, mutationRate):
    for model in ancestor:
        if model == "Constant" or model == "Result":
            continue
        else:
            for parameter in ancestor[model]:
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
    return ancestor                

def save(traits):
    name = names.get_full_name().replace(' ','_')
    path = "/home/meng/Projects/NeuroTrader/Models/GeneticProgression/Alive/"
    f = open(path+name+".json", "w")
    json.dump(traits, f, indent=4)
    f.close()


if __name__ == "__main__":
    ancestor = loadTemplate()
    for i in range(100):
        newTraits = mutate(ancestor, 1.0)
        save(newTraits)
