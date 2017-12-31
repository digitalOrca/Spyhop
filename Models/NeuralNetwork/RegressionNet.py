#!/usr/bin/python3.6

from __future__ import print_function
from itertools import count

import random
from Preprocess import Preprocess
import torch
from torch import nn

import torch.autograd
import torch.nn.functional as F
from torch.autograd import Variable

POLY_DEGREE = 4
W_target = torch.randn(POLY_DEGREE, 1) * 5
b_target = torch.randn(1) * 5


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
    train = (fr_train, ar_train)
    validate = (fr_validate, ar_validate)
    return train, validate


def createModel(input_size):
    model = nn.Linear(input_size, 1)
    return model


def createBatch(input, target, batch_size):
    batch_index = random.sample(range(len(input)), batch_size)
    batch_input = input.iloc[batch_index].as_matrix().astype('float')
    batch_target = target.iloc[batch_index].as_matrix().astype('float')
    batch_input = torch.from_numpy(batch_input)
    batch_target = torch.from_numpy(batch_target)
    return batch_input, batch_target


def create_features(x):
    """Builds features i.e. a matrix with columns [x, x^2, x^3, x^4]."""
    x = x.unsqueeze(1)
    return torch.cat([x ** i for i in range(1, POLY_DEGREE+1)], 1)


def f(x):
    """Approximated function."""
    return x.mm(W_target) + b_target[0]


def poly_desc(W, b):
    """Creates a string description of a polynomial."""
    result = 'y = '
    for i, w in enumerate(W):
        result += '{:+.2f} x^{} '.format(w, len(W) - i)
    result += '{:+.2f}'.format(b[0])
    return result


def get_batch(batch_size=32):
    """Builds a batch i.e. (x, f(x)) pair."""
    random = torch.randn(batch_size)
    x = create_features(random)
    y = f(x)
    return Variable(x), Variable(y)


train, validate = preprocessData()
train_in, train_out = train
createBatch(train_in, train_out, 32)
fc = createModel(len(train_in.columns))

for batch_idx in count(1):
    # Get data
    batch_input, batch_target = createBatch(train_in, train_out, 32)
    # Reset gradients
    fc.zero_grad()
    # Forward pass
    print(type(batch_input))
    print(type(batch_target))
    print(fc(batch_input))  # TODO: PROBLEM WITH DATA TYPE?
    import sys
    sys.exit()
    output = F.smooth_l1_loss(fc.forward(batch_input), batch_target)
    loss = output.data[0]

    # Backward pass
    output.backward()

    # Apply gradients
    for param in fc.parameters():
        param.data.add_(-0.1 * param.grad.data)

    # Stop criterion
    if loss < 1e-3:
        break

print('Loss: {:.6f} after {} batches'.format(loss, batch_idx))
print('==> Learned function:\t' + poly_desc(fc.weight.data.view(-1), fc.bias.data))
print('==> Actual function:\t' + poly_desc(W_target.view(-1), b_target))




