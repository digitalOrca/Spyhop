#!/usr/bin/python3

"""ReportGenerator.py
Description:
    run the champion model and view the results
"""

import os
import ModelRunner as mr
from LinearRegression import LinearRegression

"""getChampion
Description: 
    get the name of champion model
"""
def getChampion():
    return os.listdir("./progression/champions")[0].split(".")[0]

"""
MAIN
"""
if __name__=="__main__":
    champion = getChampion()
    lr_model = mr.loadParameters(champion)
    lr_model.train(benchmark="snp500")
    print(lr_model.predict())


