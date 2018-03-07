#!/usr/bin/python3

import random
from itertools import count
from Preprocess import Preprocess
import numpy as np
import matplotlib.pyplot as plt
import torch
from torch import nn
from torch.nn import functional
from torch import autograd
from torch import cuda

# THIS IS A DUMMY PROGRAM FOR NOW


def preprocessData():
    preprocessing = Preprocess(data="fundamental_ratios")
    print("retrieving fundamental ratios...")
    fr_train, fr_validate = preprocessing.get_data(dataType="scaled", dset="train_validate")
    print("retrieving returns...")
    ar = preprocessing.retrieve_return()
    print("split returns...")
    ar_train = ar[ar.index.isin(fr_train.index)]
    ar_validate = ar[ar.index.isin(fr_validate.index)]
    print("trim fundamental ratios...")
    fr_train = fr_train[fr_train.index.isin(ar_train.index)]
    fr_validate = fr_validate[fr_validate.index.isin(ar_validate.index)]
    # remove boundary values
    print(ar_train)
    ar_train.drop(ar_train.nlargest(250, "return").index, axis=0, inplace=True)
    ar_train.drop(ar_train.nsmallest(250, "return").index, axis=0, inplace=True)
    # re-order train set for visualization
    ar_train = ar_train.sort_values("return")
    fr_train = fr_train.loc[ar_train.index]
    train = (fr_train, ar_train)
    # re-order validation set for visualization
    ar_validate =ar_validate.sort_values("return")
    fr_validate = fr_validate.loc[ar_validate.index]
    validate = (fr_validate, ar_validate)
    return train, validate


def createModel(input_size):
    model = nn.Sequential(
        nn.Linear(input_size, 5000),
        nn.Linear(5000, 5000),
        nn.ReLU(),
        nn.Linear(5000, 5000),
        nn.ReLU(),
        nn.Linear(5000, 5000),
        nn.ReLU(),
        nn.Linear(5000, 5000),
        nn.ReLU(),
        nn.Linear(5000, 5000),
        nn.ReLU(),
        nn.Linear(5000, 5000),
        nn.ReLU(),
        nn.Linear(5000, 5000),
        nn.ReLU(),
        nn.Linear(5000, 2500),
        nn.ReLU(),
        nn.Linear(2500, 1),
        nn.Sigmoid()
    )
    return model


def createBatch(data_input, target, batch_size, gpu=False):
    # generate random batch index
    batch_index = random.sample(range(len(data_input)), batch_size)
    # compute batch input/output
    data_input = data_input.iloc[batch_index].as_matrix().astype(np.float32)
    data_target = target.iloc[batch_index].as_matrix().astype(np.float32)
    if gpu:
        data_input = torch.from_numpy(data_input).cuda()
        data_target = torch.from_numpy(data_target).cuda()
    return autograd.Variable(data_input), autograd.Variable(data_target)


if __name__ == "__main__":
    gpu = True
    if cuda.is_available():
        gpu_count = cuda.device_count()
        if gpu_count < 1:
            gpu = False
        print("%s CUDA enabled GPU(s) available..." % gpu_count)

    # define training and validation data set
    train, validate = preprocessData()
    train_in, train_out = train
    validate_in, validate_out = validate
    # pre-compute training input data
    train_all = torch.from_numpy(train_in.as_matrix().astype(np.float32))
    if gpu:
        train_all = train_all.cuda()
    # define model
    net = createModel(len(train_in.columns))
    if gpu:
        net.cuda()

    epoch, residual = [], []
    for i in count(1):
        # Get batch data
        batch_input, batch_target = createBatch(train_in, train_out, 512, gpu)
        # Reset gradients
        net.zero_grad()
        # Forward pass
        output = functional.mse_loss(net.forward(batch_input), batch_target)
        loss = output.data[0]
        # Backward pass
        output.backward()
        # Apply gradients
        for param in net.parameters():
            param.data.add_(-0.01 * param.grad.data)

        # compute result for training visualization
        result = net(autograd.Variable(train_all))

        plt.clf()
        x = range(len(train_in))
        plt.plot(x, train_out["return"].values, 'b-')
        plt.plot(x, result.cpu().data.numpy(), 'r-')

        title = "Iteration:{:5d} Loss:{:0.9f}".format(i, loss)
        plt.title(title)
        plt.pause(0.01)

        # Stop criterion
        if loss < 1e-3:
            break
