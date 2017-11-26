#!/usr/bin/python3.6

import torch
from Preprocess import Preprocess

class RegressionNet:
    
    def __init__(self, lag=30, density=0.8, hyperparameters=None):
        self.preprocess = Preprocess(data='fundamental_ratios', lag=lag, \
                                                             density=density)
        self.hyperparameters = hyperparameters
        
    def createNet(self):
        pass
        
    def train(self):
        train_data = self.preprocess.getData(dataType = 'scaled', lag = True)
        #TODO: MUST FIND A WAY TO SELECT SAME COLUMNS IN VALIDATION AND PREDITION
        pass
        
    def validate(self):
        pass
   
