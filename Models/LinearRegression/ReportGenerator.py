#!/usr/bin/python3

import os
import ModelRunner as mr
from LinearRegression import LinearRegression

def getChampion():
    return os.listdir("./progression/champions")[0].split(".")[0]

champion = getChampion()
lr_model = mr.loadParameters(champion)
lr_model.train(benchmark="snp500")
print(lr_model.predict())


