# -*- coding: utf-8 -*-
"""
Created on Thu Sep  4 15:09:48 2025

@author: eosjo
"""
import os
os.chdir(r'C:\Kegle_Jojo\Train_Dynamics')


from classes.Agents import TrainFlowModel
import classes.Generate_network as Gen
import classes.plot as plot
import numpy as np
from classes.functions import *
from Configuration.definitions import *

adj_matrix = [
    [["S_A",'T_A'], 100, 100, 0, 0, 0, 0, 0, 0, 0],  # nó 0 → nó 1 e 2
    [0, 0, 0, 100, 0, 0, 0, 0, 0, 0],   # nó 1 → nó 3
    [0, 0, 0, 100, 0, 0, 0, 0, 0, 0],   # nó 2 → nó 3
    [0, 0, 0, ["S_B",None], 100, 0, 0, 0, 0, 0],   # nó 3 → nó 4
    [0, 0, 0, 0, 0, 100, 100, 100, 0, 0],   # nó 4 → nó 5, 6 e 7
    [0, 0, 0, 0, 0, 0, 0, 0, 100, 0],   # nó 5 → nó 8
    [0, 0, 0, 0, 0, 0, 0, 0, 100, 100], # nó 6 → nós 8 e 9
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 80],   # nó 7 → nó 9
    [0, 0, 0, 0, 0, 0, 0, 0,["S_C",None], 0],   # nó 8 → (sem conexões de saída)
    [0, 0, 0, 0, 0, 0, 0, 0, 0, ["S_D","T_B"]]      # nó 9 (sem conexões de saída)
]



edges_descrition = zerar_diagonal_principal(adj_matrix)
station_nodes,train_nodes = extrair_diagonal_principal(adj_matrix)

model = TrainFlowModel(edges_descrition, station_nodes, train_nodes, TRAIN_TABLE_DEFAULT, STATION_TABLE_DEFAULT,ITINERARY_TABLE_DEFAULT)

n_steps =30

for t in range(n_steps):
    model.step()
    plot.print_network_state(model.grid.G,t) 
    plot.plot_network_state(model.grid.G, model.G_runtime, t)
    #plot.plot_network_state_pyvis(model.grid.G,t)
model.export_CSV("Logs/run")


              
