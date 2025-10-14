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
from Configuration.definitions import *

DEBUG = False

class Station(mesa.Agent):
    def __init__(self,model, pos, ID, name):
        # Pass the parameters to the parent class.
        super().__init__(model)
        
        self.name = name
        self.network = model.grid.G
        self.stationID = ID
        self.node = pos
        self.itineraryTable = ITINERARY_TABLE

    def get_next_mission(self, itinerary):
        
        next_mission = get_next_station_from_itinerary_table(self.itineraryTable, itinerary, self.name)
        if next_mission is None:
           return None  # não há próxima missão
        else: 
            return next_mission  # sempre retorna int
    
    
    def update_grid(self):
        ''' do nothing for now, but is dedicated to update the grid, duo to topology changes in the middle of operation by random events'''
    
    def set_node_location(self, new_node):
        self.node = int(new_node)  # força a ser int
        
    
class Train(mesa.Agent):
    """
    Agente que representa um trem.
    Ele "viaja" de nó em nó pelo grafo (o meio).
    """
    def __init__(self,model,name,pos, ID, ITINERARY, size):
        # Pass the parameters to the parent class.
        super().__init__(model)
        # Create the agent's attribute and set the initial values.
        self.network = model.grid.G
        self.trainID = ID
        self.node = pos
        self.itinerary = ITINERARY
        self.next_mission = None
        self.name = name
        
        self.update_target = True
        self.node_target = None
       
        self.last_node = None
        self.velocity = 70 # velocity in m/s
        
        self.displacement = 0 # Displacement position in the current adge. ( All trains start at 0 )
        self.advance_to_next_node = False # bool variable to see if the object already moved pass the treshold of advancing to next node
    
        self.crash = False
        self.size = size
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
        self.node = int(new_node)  # força inteiro
    
    
    def set_advance_to_next_node(self, value: bool):
        self.advance_to_next_node = value
        
    # ===== Outros métodos =====
    
    def calculate_target_node(self):
    
        """
        Atualiza self.node_target para o próximo nó no caminho mínimo
        entre self.node (atual) e self.next_mission.
        """
        
        if self.update_target and self.next_mission is not None:
            try:
                # Calcula o caminho mínimo usando Dijkstra
                # Garantindo que self.node e self.next_mission sejam inteiros
                path = nx.dijkstra_path(
                    self.network, int(self.node), int(self.next_mission), weight="weight"
                )
    
                # Se existir um caminho com mais de um nó, pega o próximo nó
                # path[0] é o nó atual, path[1] é o próximo
                if len(path) > 1:
                    self.node_target = int(path[1])  # garante inteiro
                else:
                    # Já está no destino
                    self.node_target = int(self.node)
    
            except nx.NetworkXNoPath:
                # Se não existe caminho, mantém o nó atual como target
                self.node_target = int(self.node)
                
    
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
        
        
    def set_next_mission(self):
        # Pega agente Station no mesmo nó
        station_agent = next(
            (a for a in self.model.grid.get_cell_list_contents([self.node])
             if isinstance(a, Station)),
            None
        )
        if station_agent is None:
            return
        
        # Pega o nome da próxima estação
        next_station_name = station_agent.get_next_mission(self.itinerary)
        
        if next_station_name is None:
            return
        
        # Procura o agente Station correspondente para pegar o nó
        target_station_agent = next(
            (a for a in self.model.Station_agents if a.name == next_station_name),
            None
        )
        
        if target_station_agent is not None:
            # Atualiza next_mission com o nó da rede
            self.next_mission = target_station_agent.node
            
       
class TrainFlowModel(mesa.Model):
    """
    Modelo com:
      - Grafo como meio de transmissão.
      - Agentes como Trens viajando.
    """
    
    def __init__(self, adj_matrix, station_nodes_list, train_nodes_list ,seed = None):
        
        super().__init__(seed=seed)
        # cria grafo determinado pela matrix de adjacências adj_matrix
        G = nx.from_numpy_array(np.array(adj_matrix))
        
        # concatena os nomes das estações aos nós pertencentes das mesmas
        for i, station_name in enumerate(station_nodes_list ):
            G.nodes[i]['station_name'] = station_name
        
        # concatena os nomes das estações aos nós pertencentes das mesmas
        for i, train_name in enumerate(train_nodes_list ):
            G.nodes[i]['train_name'] = train_name
        
        
        # Importa informações de topologia :
        self.grid = NetworkGrid(G)
        self.station_table = STATION_TABLE
        self.itinerary_table = ITINERARY_TABLE
        
        nodes = list(G.nodes)
       
        
        # Retorna os valores de criação de instância para cada estação da STATION_TABLE
        station_namelist, station_ids, n_stations = get_station_info(STATION_TABLE) 
        
        # Retorna os valores de criação de instância para cada estação da TRAIN_TABLE
        train_namelist, train_ids, n_trains, itinerary, size_list =  get_train_info(TRAIN_TABLE)
        
        # Instanciamento de n agentes
        train_agents = Train.create_agents(model=self, pos = None, n=n_trains, ID=train_ids, ITINERARY = itinerary,name = train_namelist, size = size_list)
        station_agents = Station.create_agents(model=self, pos = None, n=n_stations, ID = station_ids, name = station_namelist)
        
        # retorna todos os nós da rede.
        nodes = list(self.grid.G.nodes)
       
        # lista apenas os nós que possuem estação
        station_nodes = [node for node, data in self.grid.G.nodes(data=True) if data.get('station_name') is not None]
        
        # lista apenas os nós que possuem estação
        train_nodes = [node for node, data in self.grid.G.nodes(data=True) if data.get('init_train_number') is not None]

       # nodes_with_trains:
        nodes_with_train = [
           (node, data['train_name'])
           for node, data in self.grid.G.nodes(data=True)
           if data.get('train_name') is not None
           ] 
        
        name_to_node = {name: int(node) for node, name in nodes_with_train}
         
        # posiciona cada agente de trem no nó inicial correto
        for agent in train_agents:
            node = name_to_node.get(agent.name)
            if node is not None:
                self.grid.place_agent(agent, node)
                agent.set_node_location(node)
        
        
       # nodes_with_station: lista (node, station_name)
        nodes_with_station = [
           (node, data['station_name'])
           for node, data in self.grid.G.nodes(data=True)
           if data.get('station_name') is not None
           ]
        
        # dicionário rápido: nome -> nó
        name_to_node = {name: int(node) for node, name in nodes_with_station}

        # posiciona cada agente Station no nó correto
        for agent in station_agents:
            node = name_to_node.get(agent.name)
            if node is not None:
                self.grid.place_agent(agent, node)
                agent.set_node_location(node)
       
      
        # Finish the initialization and create a self property to store the agents after init
        self.Station_agents = station_agents
        self.Train_agents = train_agents
        
        
        
    def overlap(self, a1, a2):
        """
        Retorna True se os intervalos de deslocamento (considerando o tamanho)
        se sobrepõem na mesma aresta.
        """
        half1 = a1.size / 2
        half2 = a2.size / 2

        # posição inicial e final de cada trem
        start1 = a1.displacement - half1
        end1 = a1.displacement + half1
        start2 = a2.displacement - half2
        end2 = a2.displacement + half2

        # se há interseção entre os segmentos
        return not (end1 < start2 or end2 < start1)
                
    def update_train_position(self, blocked_nodes):
        for a in self.Train_agents:
    
            # 🚫 se o trem já colidiu, não se move mais
            if a.crash == True:  
                continue
    
            # ✅ só move se tiver destino, não estiver bloqueado, e puder avançar
            if (
                a.node_target is not None
                and a.node_target not in blocked_nodes
                and a.advance_to_next_node is True
            ):
                a.last_node = a.node
                self.grid.move_agent(a, a.node_target)  # move o agente para o nó destino
                a.node = a.node_target
                a.set_advance_to_next_node(False)


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
    
    def detect_collisions(self, agents_list):
        """
        Marca self.crash = True para trens que colidem e mantém o estado para sempre.
        Considera:
        - colisão no mesmo nó;
        - sobreposição na mesma aresta (mesma direção);
        - cruzamento em direções opostas (A->B e B->A);
        - offset físico baseado em self.size (centro do trem).
        """
        
        for i in range(len(agents_list)):
            a1 = agents_list[i]
            for j in range(i + 1, len(agents_list)):
                a2 = agents_list[j]
    
                # Se ambos já colidiram, não precisa verificar de novo
                if a1.crash and a2.crash:
                    continue
    
                # --- (1) colisão no mesmo nó ---
                if a1.node == a2.node:
                    a1.crash = a2.crash = True
                    continue
    
                # --- (2) mesma aresta (mesma direção) ---
                if a1.node == a2.node and a1.node_target == a2.node_target:
                    if self.overlap(a1, a2):
                        a1.crash = a2.crash = True
                        continue
    
                # --- (3) cruzamento oposto (A->B e B->A) ---
                if a1.node == a2.node_target and a1.node_target == a2.node:
                    if self.overlap(a1, a2):
                        a1.crash = a2.crash = True
                        continue




    def step(self):
        
        print("\n=== STEP ===")
        for a in self.Train_agents:     
            print(f"Train {a.trainID}: displacement={a.displacement}, advance={a.advance_to_next_node}")
            a.set_next_mission()
        # All agents calculate their target of movement
        for a in self.Train_agents: 
            a.calculate_target_node()
        
        blocked_nodes = []
        #blocked_nodes = self.get_blocked_positions(self.Train_agents)
        
        self.detect_collisions(self.Train_agents)
        
        # Update all trains postions
        self.update_train_position(blocked_nodes)
        
        for a in self.Train_agents: 
            a.calculate_displacement_to_target()


