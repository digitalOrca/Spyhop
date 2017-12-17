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
        train_data = self.preprocess.get_data(dataType ='scaled', lag = True)
        train_data_t = torch.from_numpy(train_data.as_matrix())
        print(train_data_t)
        #TODO: MUST FIND A WAY TO SELECT SAME COLUMNS IN VALIDATION AND PREDITION
        pass
        
    def validate(self):
        pass
   
rn = RegressionNet()
rn.train()
