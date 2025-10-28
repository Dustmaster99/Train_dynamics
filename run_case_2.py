# -*- coding: utf-8 -*-
"""
Created on Mon Oct 27 15:14:10 2025

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




adj_matrix , TRAIN_TABLE, ITINERARY_TABLE = Gen.criar_rede_completa(n = 3, i = 2, z = 3, p= 100)

edges_descrition = zerar_diagonal_principal(adj_matrix)
station_nodes,train_nodes = extrair_diagonal_principal(adj_matrix)



model = TrainFlowModel(edges_descrition, station_nodes, train_nodes, TRAIN_TABLE, STATION_TABLE_DEFAULT,ITINERARY_TABLE)

n_steps =30

for t in range(n_steps):
    model.step()
    plot.print_network_state(model.grid.G,t) 
    plot.plot_network_state(model.grid.G, model.G_runtime, t)
    #plot.plot_network_state_pyvis(model.grid.G,t)
model.export_CSV("Logs/run_case_2")

              
