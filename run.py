# -*- coding: utf-8 -*-
"""
Created on Thu Sep  4 15:09:48 2025

@author: eosjo
"""
import os
os.chdir(r'C:\Kegle_Jojo\Train_Dynamics')
from classes.Agents import TrainFlowModel
import classes.plot as plot
import numpy as np

adj_matrix = [
    [0, 10, 0, 0, 0, 0, 10],
    [10, 0, 10, 0, 0, 0, 0],
    [0, 10, 0, 10, 0, 0, 0],
    [0, 0, 10, 0, 10, 0, 0],
    [0, 0, 0, 10, 0, 10, 0],
    [0, 0, 0, 0, 10, 0, 10],
    [10, 0, 0, 0, 0, 10, 0]
]
n_trains = 2


model = TrainFlowModel(n_trains,adj_matrix)
for t in range(10):
    model.step()
    plot.print_network_state(model.grid.G,t) 
    plot.plot_network_state(model.grid.G,t)

              
