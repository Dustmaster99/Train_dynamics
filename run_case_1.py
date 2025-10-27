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
from Configuration.definitions import *
from classes.functions import *

''' direct conection
adj_matrix = [
 [["S_A",'T_C'],100,0,0],
 [100,0,100,0],
 [0,100,["S_B",None],100],
 [0,0,100,["S_C","T_D"]]
 ]
'''

'''adding an intermediate node to allow manouvers 
adj_matrix = [
 [["S_A",'T_C'],100, 100 ,0 ,0 ],
 [100,0,0,100,0],
 [100,0,0,100,0],
 [0,100,100,["S_B",None],100],
 [0,0,0,100,["S_C","T_D"]]
 ]
'''
'''adding two intermediate node to allow manouvers '''
adj_matrix = [
 [["S_A",'T_C'],100, 100 ,0 ,0,0 ],
 [100,0,0,100,0,0],
 [100,0,0,100,0,0],
 [0,100,100,["S_B",None],100,100],
 [0,0,0,100,0,100],
 [0,0,0,100,100,["S_C","T_D"]]
 ]


edges_descrition = zerar_diagonal_principal(adj_matrix)
station_nodes,train_nodes = extrair_diagonal_principal(adj_matrix)



model = TrainFlowModel(edges_descrition, station_nodes, train_nodes,TRAIN_TABLE_DEFAULT, STATION_TABLE_DEFAULT,ITINERARY_TABLE_DEFAULT)

n_steps =30

for t in range(n_steps):
    model.step()
    plot.print_network_state(model.grid.G,t) 
    plot.plot_network_state(model.grid.G, model.G_runtime, t)
    #plot.plot_network_state_pyvis(model.grid.G,t)

              
