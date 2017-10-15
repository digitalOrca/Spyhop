#!/usr/bin/python

import ast
import names
import random
from ConfigParser import ConfigParser

chromosome = []
geneTemplate = "/home/meng/Projects/NeuroTrader/Models/Evolution/GeneticTemplate.conf"

def loadTemplate():
        config = ConfigParser()
        config.read(geneTemplate)
        for section in config.sections():
            for option in config.options(section):
                value = config.get(section, option)
                try:
                    value = float(value)
                except ValueError:
                    if value == 'True' or value == 'False':
                        value = bool(value)
                    elif value == 'None':
                        value = None
                chromosome.append(value)
        
        
def shuffle(stdfrac):
    chrom = []
    for i in range(len(chromosome)):
        chromType = type(chromosome[i])
        if chromType == int:
            change = round(random.gauss(0, stdfrac * float(chromosome[i])))
            chrom.append(max(1, chrom[i]+change))
        elif chromType == float:
            change = random.gauss(0, stdfrac * float(chromosome[i]))
            chrom.append(min(max(0, chromosome[i]+change), 1))
        elif chromType == bool:
            chrom.append(abs(chromosome[i]-1))
        elif chromosome[i] is None:
            chrom.append(None)
        elif chromType == str:
            parts = chromosome[i].split('|')
            if len(parts) == 1:
                chrom.append(chromosome[i])
            else:
                options = ast.literal_eval(parts[1])
                selected = options[random.randint(0,len(options)-1)] 
                chrom.append(selected + "|" + str(options))
        else:
            pass
    return chrom
    

def save(chrom, name):
    config = ConfigParser()
    config.read(geneTemplate)
    for section in config.sections():
            for option in config.options(section):
                config.set(section, option, str(chrom.pop(0)))
    newConfig = open(name, 'w')
    config.write(newConfig)


loadTemplate()
print chromosome
for i in range(100):
    save(shuffle(0.25), "/home/meng/Projects/NeuroTrader/Models/GeneticProgression/Alive/"+names.get_full_name().replace(' ','_')+".conf")

