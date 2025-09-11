# -*- coding: utf-8 -*-
"""
Created on Thu Sep  4 14:19:51 2025

@author: eosjo
"""

import os
os.chdir(r'C:\Kegle_Jojo\Train_Dynamics')


# mesa_info_flow.py
# Modelo: nós = meio, agentes = informação em movimento
import mesa
import numpy as np
from mesa.space import NetworkGrid
import networkx as nx
import random

DEBUG = False

class Train(mesa.Agent):
    """
    Agente que representa um trem.
    Ele "viaja" de nó em nó pelo grafo (o meio).
    """
    def __init__(self,model,pos, ID):
        # Pass the parameters to the parent class.
        super().__init__(model)
        # Create the agent's attribute and set the initial values.
        self.network = model.grid.G
        self.trainID = ID
        self.node = pos
        self.node_target = None
        self.last_node = None
    
    # ===== Getters =====
    def get_location(self):
        """
        Retorna o nó do grafo onde o agente está atualmente.
        """
        node = self.node
        
        if DEBUG == True:
            print( 'The location for train with ID ' + str(self.trainID ) + ' is the node ' + str(self.node))
        return node
    
    def get_node_neighbors(self):
        node_neighbors = list(self.network.neighbors(self.node))
        edges_neighbors = list(self.network.edges(self.node))
        return node_neighbors,edges_neighbors
    
    # ===== Setters =====
    def set_node_location(self, new_node):
        
        if self.node != None:
            self.last_node = self.node
        self.node = new_node
        
    # ===== Outros métodos =====
    
    def calculate_target_node(self):
        
        neighbors = list(self.network.neighbors(self.node))
        
        if hasattr(self, "last_node") and self.last_node in neighbors:
            neighbors.remove(self.last_node)
            
        if neighbors:
            self.node_target = random.choice(neighbors)
        else:
            self.node_target = self.node  # não se move se não houver vizinhos
        
    
  
      
    


class TrainFlowModel(mesa.Model):
    """
    Modelo com:
      - Grafo como meio de transmissão.
      - Agentes como Trens viajando.
    """
    def __init__(self, n_trens, adj_matrix, seed = None):
        super().__init__(seed=seed)
        # cria grafo determinado pela matrix de adjacências adj_matrix
        G = nx.from_numpy_array(np.array(adj_matrix))
        # cria o espaço
        self.grid = NetworkGrid(G)
        nodes = list(G.nodes)
        # Cria os ids de forma sequencial, para que tenhamos ids de 1 a n_trens
        train_ids = list(range(1, n_trens + 1))
        # Instanciamento de n agentes
        agents = Train.create_agents(model=self, pos = None, n=n_trens, ID=train_ids)
        
        
        nodes = list(self.grid.G.nodes)
        # aleatoriza a posição em que iniciam os agentes, sendo essas nós diferentes
        start_nodes = self.random.sample(nodes, len(agents))
        # efetivamente posiciona cada agente em um nó da rede
        for agent, node in zip(agents, start_nodes):
                self.grid.place_agent(agent, node)
                agent.set_node_location(node)
                
        self.Train_agents = agents 
                
                
    def update_train_position(self,blocked_nodes):
        for a in self.Train_agents:
            if a.node_target is not None and a.node_target not in blocked_nodes:
                a.last_node = a.node
                self.grid.move_agent(a, a.node_target)
                a.node = a.node_target          # atualiza nó atual

    def get_blocked_positions(self,agents_list):
        all_targets = []
        blocked_targets = []
        for a in agents_list:
            target = a.node_target
            if target in all_targets:
                blocked_targets.append(target)
            else:
                all_targets.append(target)
        return blocked_targets
    

    def step(self):
        # All agents calculate their target of movement
        for a in self.Train_agents: a.calculate_target_node()
        blocked_nodes = self.get_blocked_positions(self.Train_agents)
        # Update all trains postions
        self.update_train_position(blocked_nodes)


