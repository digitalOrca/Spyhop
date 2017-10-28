#!/usr/bin/python3

import names
import random
import json
from collections import OrderedDict
import EvolutionCore as ec
              
def save(traits):
    name = names.get_full_name().replace(' ','_')
    path = "/home/meng/Projects/NeuroTrader/Models/GeneticProgression/Alive/"
    f = open(path+name+".json", "w")
    json.dump(traits, f, indent=4)
    f.close()


if __name__ == "__main__":
    traits = ec.getTraits()
    for i in range(100):
        newTraits = ec.mutate(traits, 1.0)
        save(newTraits)
