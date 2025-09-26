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

'''
# Grafo watts_strogatz com 8 nós
adj_matrix = Gen.gerar_matriz_adjacencia(
    topo_type="watts_strogatz",
    n=8,      # Número de nós
    k=2,      # Cada nó conecta a 2 vizinhos (grau 2 para circular puro)
    p=0.4       # Probabilidade zero de rewiring - mantém a estrutura circular
)
Gen.visualizar_matriz_adjacencia (adj_matrix)
print(adj_matrix)

'''


adj_matrix = [
    [0, 50, 0, 0, 0, 0, 50],
    [50, 0, 50, 0, 0, 0, 0],
    [0, 50, 0, 50, 0, 0, 0],
    [0, 0, 50, 0, 50, 0, 0],
    [0, 0, 0, 50, 0, 50, 0],
    [0, 0, 0, 0, 50, 0, 50],
    [50, 0, 0, 0, 0, 50, 0]
]

station_nodes = ["S_A", None, "S_B", None, "S_C", None, "S_D"]

'''
adj_matrix = Gen.gerar_matriz_adjacencia_2(
    num_nos=15,
    min_ligacoes=2,
    max_ligacoes=3,
    peso_min=10,
    peso_max=30,
    direcionado=False
)
'''

n_trains = 1

model = TrainFlowModel(n_trains,adj_matrix, station_nodes)
for t in range(50):
    model.step()
    plot.print_network_state(model.grid.G,t) 
    plot.plot_network_state(model.grid.G,t)

              
