# From https://github.com/brentyi/multimodalfilter/blob/master/scripts/push_task/train_push.py

import sys
import os
sys.path.insert(0, os.getcwd())

import argparse
import datetime

import fannypack
import torch
import torch.nn as nn
import torch.optim as optim

from torch.utils.data import DataLoader

from datasets.gentle_push.data_loader import Dataset, PushTask
from unimodals.robotics.encoders import (
    ProprioEncoder, ForceEncoder, GentlePushImageEncoder, DepthEncoder, ActionEncoder,
)
from unimodals.common_models import MLP
from unimodals.robotics.decoders import ContactDecoder
from fusions.common_fusions import Concat
from training_structures.Simple_Late_Fusion import train, test

Task = PushTask

# Parse args
parser = argparse.ArgumentParser()
Task.add_dataset_arguments(parser)
args = parser.parse_args()
dataset_args = Task.get_dataset_args(args)

fannypack.data.set_cache_path('datasets/gentle_push/cache')

# Load trajectories into memory
train_trajectories = Task.get_train_trajectories(**dataset_args)
val_trajectories = Task.get_eval_trajectories(**dataset_args)

train_loader = DataLoader(
    Dataset(train_trajectories),
    batch_size=32,
    shuffle=True,
)
val_loader = DataLoader(
    Dataset(val_trajectories),
    batch_size=32,
    shuffle=True,
)

encoders = [
    ProprioEncoder(32, input_dim=2, alpha=1.0),
    ProprioEncoder(32, input_dim=3, alpha=1.0),
    ProprioEncoder(32, input_dim=7, alpha=1.0),
    GentlePushImageEncoder(32, alpha=1.0),
    ProprioEncoder(32, input_dim=7, alpha=1.0),
]
fusion = Concat()
head=MLP(320,128,2)
optimtype = optim.Adam
loss_state = nn.MSELoss()

train(encoders, fusion, head,
      train_loader, val_loader,
      15,
      task='regression',
      optimtype=optimtype,
      criterion=loss_state,
      lr=0.001)
