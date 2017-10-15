#!/usr/bin/python

import os
import random
import subprocess
from ConfigParser import ConfigParser

class Individual:


    def __init__(self, generation):
        self.model = ""
        self.chromosome = [] # list of hyper parameters
        self.sore = 0;
        self.generation = generation
        self.longevity = 0


    def loadConfig(self, conf):
        config = ConfigParser()
        config.read(conf)
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
                self.chromosome.append(value)
        print self.chromosome
        

    def run(self):
        root = "DIR"
        #args = self.chromosome
        #command = args.insert(0, root+self.model)
        #ps = subprocess.Popen(command, stdout=subprocess.PIPE, \
        #                               stderr=subprocess.PIPE)
        #output, error = ps.communicate()
        #TODO: update score based on the output
        self.score = random.uniform(0,1)
        
        
class Population:


    def __init__(self, popSize=100, mutRate=0.02, mutDist=0.1):
        self.popSize = popSize
        self.mutRate = mutRate
        self.mutDist = mutDist
        self.currGen = 0
        self.members = []
        for i in range(self.popSize):
            #TODO: TESTING
            c = []
            for x in range(4):
                c.append(random.uniform(1,10))
            self.members.append(Individual(c, 0))


    def evalAll(self):
        for s in self.members:
            s.run()
        self.members.sort(key=lambda x: x.score, reverse=True)
        
        
    def crossover(self, chrom1, chrom2): #uniform crossover
        if len(chrom1) != len(chrom2):
            raise Exception("Unmatched chromosome size")
        newChrom = []
        for i in range(len(chrom1)):
            if random.uniform(0,1) < 0.5:
                newChrom.append(chrom1[i])
            else:
                newChrom.append(chrom2[i])
        return newChrom


    def mutation(self, chrom, stdfrac): #TODO: IMCOMPLETE
        for i in range(len(chrom)):
            if random.uniform(0,1) < self.mutRate:
                chromType = type(chrom[i])
                if chromType == int:
                    change = round(random.gauss(0, stdfrac * float(chrom[i])))
                    chrom[i] = max(1, chrom[i]+change)
                elif chromType == float:
                    change = random.gauss(0, stdfrac * float(chrom[i]))
                    chrom[i] = min(max(0, chrom[i]+change), 1)
                elif chromType == bool:
                    chrom[i] = abs(chrom[i]-1)
                elif chromType == str:
                    pass
                else:
                    pass
        return chrom


    def reproduce(self):
        self.evalAll()
        nextGen = []
        self.currGen += 1
        while len(nextGen) < len(self.members):
            pair = []
            p1 = -1
            while len(pair) < 2:
                for i in range(self.popSize):
                    remain = float(self.popSize-i)
                    prob = 2.0/(pow(remain,2)-remain)
                    if random.uniform(0,1) < prob:
                        if len(pair) == 0:
                            pair.append(self.members[i])
                            p1 = i
                            break;
                        elif i != p1:
                            pair.append(self.members[i])
                            break;
                        else:
                            break;
            crossedChrom = self.crossover(pair[0].chromosome, pair[1].chromosome)
            newChromosome = self.mutation(crossedChrom, self.mutDist)
            nextGen.append(Individual(newChromosome, self.currGen))
        self.members = nextGen
        
"""        
if __name__ == "__main__":
    population = Population(popSize=4, metachrom=["f","f","f","f"])
    print population.members[0].chromosome," ",population.members[1].chromosome," ",population.members[2].chromosome," ",population.members[3].chromosome
    for i in range(50):
        population.reproduce()
        print population.members[0].chromosome," ",population.members[1].chromosome," ",population.members[2].chromosome," ",population.members[3].chromosome
    """
    
i = Individual(0)
i.loadConfig("/home/meng/Projects/NeuroTrader/Models/Evolution/geneTemplate.conf")
