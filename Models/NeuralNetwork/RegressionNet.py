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


def preprocessData():
    preprocessing = Preprocess(data="fundamental_ratios")
    print("retrieving fundamental ratios...")
    fr_train, fr_validate = preprocessing.get_data(dataType="scaled", dset="train_validate")
    print("retrieving returns...")
    ar = preprocessing.compute_return(split=False)
    print("split returns...")
    ar_train = ar[ar.index.isin(fr_train.index)]
    ar_validate = ar[ar.index.isin(fr_validate.index)]
    print("trim fundamental ratios...")
    fr_train = fr_train[fr_train.index.isin(ar_train.index)]
    fr_validate = fr_validate[fr_validate.index.isin(ar_validate.index)]
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
        nn.Linear(5000, 2500),
        nn.ReLU(),
        nn.Linear(2500, 1),
        nn.Sigmoid()
    )
    return model


def createBatch(input, target, batch_size):
    batch_index = random.sample(range(len(input)), batch_size)
    batch_input = input.iloc[batch_index].as_matrix().astype(np.float32)
    batch_target = target.iloc[batch_index].as_matrix().astype(np.float32)
    batch_input = torch.from_numpy(batch_input)
    batch_target = torch.from_numpy(batch_target)
    return autograd.Variable(batch_input), autograd.Variable(batch_target)


if cuda.is_available():
    gpu_count = cuda.device_count()
    print("%s CUDA enabled GPU(s) available..." % gpu_count)


train, validate = preprocessData()
train_in, train_out = train
validate_in, validate_out = validate

net = createModel(len(train_in.columns))

#fig1 = plt.figure()
#ax1 = fig1.add_subplot(111)
#fig2 = plt.figure()
#ax2 = fig2.add_subplot(111)

epoch, residual = [], []

for i in count(1):
    # Get data
    batch_input, batch_target = createBatch(train_in, train_out, 256)
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

    #predict = net(autograd.Variable(torch.from_numpy(validate_in.as_matrix().astype(np.float32))))
    result = net(autograd.Variable(torch.from_numpy(train_in.as_matrix().astype(np.float32))))

    plt.clf()
    #x = range(len(validate_in))
    #plt.plot(x, validate_out["return"].values, 'b-')
    #plt.plot(x, [1 for i in x], 'y.-')
    #plt.plot(x, predict.data.numpy(), 'r-')
    x = range(len(train_in))
    plt.plot(x, train_out["return"].values, 'b-')
    plt.plot(x, result.data.numpy(), 'r-')

    title = "Iteration:{:5d} Loss:{:0.9f}".format(i, loss)
    plt.title(title)
    plt.pause(0.01)

    #epoch.append(i)
    #residual.append(loss)
    #ax1.clear()
    #ax1.plot(epoch, residual)
    #title = "Iteration:{:5d} Loss:{:0.9f}".format(i, loss)
    #ax1.set_title(title)
    #plt.pause(0.1)

    # Stop criterion
    if loss < 1e-3:
        break




