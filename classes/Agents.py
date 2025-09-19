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
        
        self.update_target = True
        self.node_target = None
        
        self.last_node = None
        self.velocity = 5 # velocity in m/s
        self.displacement = 0 # Displacement position in the current adge. ( All trains start at 0 )
        self.advance_to_next_node = False # bool variable to see if the object already moved pass the treshold of advancing to next node
    
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
    
    
    def set_advance_to_next_node(self, value: bool):
        self.advance_to_next_node = value
        
    # ===== Outros métodos =====
    
    def calculate_target_node(self):
        
        if self.update_target == True:
            
            neighbors = list(self.network.neighbors(self.node))
            if hasattr(self, "last_node") and self.last_node in neighbors:
                neighbors.remove(self.last_node)
            if neighbors:
                self.node_target = random.choice(neighbors)
            else:
                self.node_target = self.node  # não se move se não houver vizinhos
            
    def calculate_displacement_to_target(self):
        """
        Método de cálculo de deslocamento de maneira segura
        """
        # 1. Verifica se target existe
        if self.node_target is None:
            if DEBUG:
                print(f"Train {self.trainID}: target is None")
            return
        
        # 2. Verifica se target é diferente do nó atual
        if self.node_target == self.node:
            if DEBUG:
                print(f"Train {self.trainID}: target is same as current node")
            return
        
        # 3. Verifica se a aresta existe NO GRAFO
        if not self.network.has_edge(self.node, self.node_target):
            print(f"❌ ERRO: Train {self.trainID} - Aresta ({self.node},{self.node_target}) não existe!")
            print(f"   Nó atual: {self.node}")
            print(f"   Vizinhos reais: {list(self.network.neighbors(self.node))}")
            print(f"   Target escolhido: {self.node_target}")
            self.node_target = None  # Reseta o target inválido
            return
        
        # 4. Agora sim pode acessar com segurança
        try:
            total_distance = self.network[self.node][self.node_target]['weight']
            
            # 5. Verifica se a distância é válida
            if total_distance <= 0:
                print(f"⚠️ AVISO: Distância não-positiva entre {self.node} e {self.node_target}")
                self.set_advance_to_next_node(True)
                return
            
            # Cálculo do deslocamento
            self.displacement += self.velocity
            
            if self.displacement >= total_distance:
                self.set_advance_to_next_node(True)
                self.displacement = 0
                if DEBUG:
                    print(f"Train {self.trainID}: ready to advance to {self.node_target}")
            else:
                self.set_advance_to_next_node(False)
                
        except KeyError as e:
            print(f"❌ KeyError inesperado: {e}")
            self.node_target = None
        
       
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
            if a.node_target is not None and a.node_target not in blocked_nodes and a.advance_to_next_node == True:
                a.last_node = a.node
                self.grid.move_agent(a, a.node_target) # Move o agente para a posição target.
                a.node = a.node_target          # atualiza nó atual
                a.set_advance_to_next_node(False) # atualiza o valor de advance to next node, para false

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
        
        
        print("\n=== STEP ===")
        for a in self.Train_agents:     
            print(f"Train {a.trainID}: displacement={a.displacement}, advance={a.advance_to_next_node}")
        
        # All agents calculate their target of movement
        for a in self.Train_agents: 
            a.calculate_target_node()
        
        blocked_nodes = self.get_blocked_positions(self.Train_agents)
        # Update all trains postions
        self.update_train_position(blocked_nodes)
        
        for a in self.Train_agents: 
            a.calculate_displacement_to_target()


