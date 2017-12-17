#!/usr/bin/python3

"""Seed.py
Description:
    Generate initial population for genetic algorithm
"""

import sys
import names
import random
import json
from collections import OrderedDict
import EvolutionCore as ec

"""save
Description:
    save the traits as json profile with a randomly generated name
"""             
def save(traits):
    name = names.get_full_name().replace(' ','_')
    path = "./progression/population/"
    f = open(path+name+".json", "w")
    json.dump(traits, f, indent=4)
    f.close()

"""
MAIN
"""
if __name__ == "__main__":
    try:
        size = int(sys.argv[1])
    except:
        print("Invalide argument. Usage: ./Seed [population_size]")
        sys.exit()
    traits = ec.get_traits()
    for i in range(int(sys.argv[1])):
        newTraits = ec.mutate(traits, 1.0)
        save(newTraits)
