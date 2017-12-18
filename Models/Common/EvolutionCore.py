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


def get_traits(name=None):
    """getTraits
    Description:
        load json profile into data structure
    Input:
        name: name of the json profile, default is the template
    Output:
        traits: json object
    """
    if name is None:
        template = open("./progression/DNA.json", 'r')
        traits = json.load(template, object_pairs_hook=OrderedDict)
        template.close()
    else:
        f = open(population_root+name+".json", "r")
        traits = json.load(f, object_pairs_hook=OrderedDict)
        f.close()
    return traits


def mut_bool():
    """mutBool
    Description:
        boolean value mutation
    """
    rand = random.uniform(0, 1)
    return rand > 0.5
    

def mut_int(min_val, max_val):
    """mutInt
    Description:
        integer value mutation
    """
    new_int = random.randint(min_val, max_val)
    return new_int
    

def mut_float(min_val, max_val):
    """mutFloat
    Description:
        float value mutation
    """
    new_float = random.uniform(min_val, max_val)
    return new_float
    

def mut_str(option):
    """mutStr
    Description:
        string value mutation
    """
    length = len(option)
    index = random.randint(0, length-1)
    return option[index]
    

def mutate(traits, mutation_rate):
    """mutate
    Description:
        mutate a given set of traits at a given mutation rate
    Input:
        traits: json object representing traits
        mutationRate: mutation rate
    Output:
        traits: mutated traits
    """
    for model in traits:
        if model == "Constant" or model == "Result":
            continue
        else:
            for parameter in traits[model]:
                mutable = parameter["mutable"]
                if mutable:
                    if random.uniform(0, 1) < mutation_rate:
                        dt = parameter["type"]
                        if dt == "int":
                            parameter["value"] = mut_int(parameter["min"], parameter["max"])
                        elif dt == "float":
                            parameter["value"] = mut_float(parameter["min"], parameter["max"])
                        elif dt == "bool":
                            parameter["value"] = mut_bool()
                        elif dt == "str":
                            parameter["value"] = mut_str(parameter["option"])
                        else:
                            pass
    return traits
    

def mate(traits1, traits2):
    """mate
    Description:
        mate two traits and create a new traits
    Input:
        traits1, traits2: parent traits
    Output:
        new_traits: child trait
    """
    new_traits = get_traits()
    for model in traits1:
        if model == "Constant" or model == "Result":
            continue
        else:
            for parameter, parameter1, parameter2 in zip(new_traits[model], traits1[model], traits2[model]):
                mutable = parameter["mutable"]
                if mutable:
                    if random.uniform(0, 1) < 0.5:
                        parameter["value"] = parameter1["value"]
                    else:
                        parameter["value"] = parameter2["value"]
    return new_traits


def save(traits, name=None):
    """save
    Description:
        save a given trait as a json file under a given name
    """
    if name is None:
        name = names.get_full_name().replace(' ', '_')
    f = open(population_root+name+".json", "w")
    f.seek(0)
    json.dump(traits, f, indent=4)
    f.truncate()
    f.close()


def birth(parent1, parent2):
    """birth
    Description:
        generate new traits under new name from two parents
    Input:
        parent1, parent2: parents names
    Output:
        new_name: child name
    """
    traits1 = get_traits(parent1)
    traits2 = get_traits(parent2)
    new_traits = mate(traits1, traits2)
    new_traits = mutate(new_traits, 0.05)  # TODO:DEFINE MUTATION RATE IN CONFIG
    new_name = names.get_full_name().replace(' ', '_')
    save(new_traits, new_name)
    return new_name
    

def eliminate(losers):
    """eliminate
    Description:
        eliminate a given list of weak models from population
    Input:
        losers: list of models to be eliminated
    """
    for name in losers:
        print("Eliminate:", name)
        os.system("rm -f %s%s.json" % (population_root, name))
    
#t1 = getTraits("Denis_Garza")
#t2 = getTraits("David_Stull")
#mate(t1, t2)
#birth("Aaron_Wallace", "Katherine_Denson")
