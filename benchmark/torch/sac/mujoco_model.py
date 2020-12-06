#!/usr/bin/env python
# coding=utf8
# File: mujoco_model.py
import parl
import torch
import torch.nn as nn
import torch.nn.functional as F

LOG_SIG_MAX = 2
LOG_SIG_MIN = -20

# Initialize Policy weights
def weights_init_(m):
    if isinstance(m, nn.Linear):
        torch.nn.init.xavier_uniform_(m.weight, gain=1)
        torch.nn.init.constant_(m.bias, 0)

class ActorModel(parl.Model):
  def __init__(self, obs_dim, act_dim):
    super(ActorModel, self).__init__()
    self.l1 = nn.Linear(obs_dim, 256)
    self.l2 = nn.Linear(256, 256)
    self.mean_linear = nn.Linear(256, act_dim)
    self.log_std_linear = nn.Linear(256, act_dim)
    #self.log_std_linear.weight.data.uniform_(-1e-3, 1e-3)
    #self.log_std_linear.bias.data.uniform_(-1e-3, 1e-3)
    self.apply(weights_init_)

  def forward(self, obs):
    x = F.relu(self.l1(obs))
    x = F.relu(self.l2(x))
    means = self.mean_linear(x)
    log_std = self.log_std_linear(x)
    log_std = torch.clamp(log_std, min=LOG_SIG_MIN, max=LOG_SIG_MAX)
    return means, log_std

class CriticModel(parl.Model):
  def __init__(self, obs_dim, act_dim):
    super(CriticModel, self).__init__()
    self.l1 = nn.Linear(obs_dim + act_dim, 256)
    self.l2 = nn.Linear(256, 256)
    self.l3 = nn.Linear(256, 1)

    self.l4 = nn.Linear(obs_dim + act_dim, 256)
    self.l5 = nn.Linear(256, 256)
    self.l6 = nn.Linear(256, 1)
    self.apply(weights_init_)

  def forward(self, obs, act):
    concat = torch.cat([obs, act], 1)

    Q1 = F.relu(self.l1(concat))
    Q1 = F.relu(self.l2(Q1))
    Q1 = self.l3(Q1)

    Q2 = F.relu(self.l4(concat))
    Q2 = F.relu(self.l5(Q2))
    Q2 = self.l6(Q2)

    return Q1, Q2
