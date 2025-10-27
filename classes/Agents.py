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
import copy

DEBUG = False

class Station(mesa.Agent):
    def __init__(self,model, pos, ID, name, time_stop, enable_stop):
        # Pass the parameters to the parent class.
        super().__init__(model)
        
        self.name = name
        self.network = model.grid.G
        self.stationID = ID
        self.node = pos
        self.itineraryTable = ITINERARY_TABLE
        self.stop_time = time_stop
        self.enable_stop = enable_stop

    def get_next_mission(self, itinerary):
        
        next_mission = get_next_station_from_itinerary_table(self.itineraryTable, itinerary, self.name)
        if next_mission is None:
           return None  # não há próxima missão
        else: 
            return next_mission  # sempre retorna int
    
    def set_stop_to_train(self, train_instance: "Train") -> None:
        if(self.enable_stop == True):
            train_instance.set_stop_steps(self.stop_time)
            # set the displacement to 0, to say that the train stopped at the station 
            train_instance.set_displacement(0)
            
    def remove_step(self, train_instance: "Train") -> None:
        train_instance.removestep()
            
    def release_train_from_stop(self, train_instance: "Train") -> None:
        if(train_instance.OnStop == True):
            train_instance.release_from_stop()
    
   
    def update_grid(self):
        ''' do nothing for now, but is dedicated to update the grid, duo to topology changes in the middle of operation by random events'''
    
    def set_node_location(self, new_node):
        self.node = int(new_node)  # força a ser int
        
    
class Train(mesa.Agent):
    """
    Agente que representa um trem.
    Ele "viaja" de nó em nó pelo grafo (o meio).
    """
    def __init__(self,model,name,pos, ID, ITINERARY, size, init_velocity):
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
        self.init_velocity = init_velocity
        self.velocity = init_velocity # velocity in m/s
        
        self.displacement = 0 # Displacement position in the current adge. ( All trains start at 0 )
        self.advance_to_next_node = False # bool variable to see if the object already moved pass the treshold of advancing to next node
    
        self.crash = False
        self.size = size
        
        self.stop_steps = 0;
        self.OnStop = False
        
        self.just_arrived = False  
        
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
    
    def set_stop_steps(self, steps):
        self.stop_steps = steps
        self.velocity = 0
        self.OnStop = True
        
    def release_from_stop(self):
        self.velocity = self.init_velocity
        self.OnStop = False
        
    def removestep(self):
        if self.stop_steps > 0:
            self.stop_steps -= 1
        
        
        
    def set_displacement(self, displacement):
        self.displacement = displacement
        
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
                # Atualiza a flag apenas se encontrou um caminho válido
                self.update_target = False   # caminho válido encontrado
           
            except nx.NetworkXNoPath:
                # Se não existe caminho, mantém o nó atual como target
                self.node_target = int(self.node)
                
            # Atualiza a flag apenas se encontrou um caminho válido

                 
    
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
                self.displacement = self.displacement % total_distance
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
    
    def update_network_reference(self, G_reference):
        """
        Atualiza a referência da propriedade self.network para o grafo fornecido.
        Assim, o trem sempre enxerga o estado atual das vias e bloqueios.
    
        Parâmetros:
            G_reference : networkx.Graph
                O grafo que será usado como rede para o trem.
        """
        if G_reference is not None:
            # Atualiza a referência diretamente (sem copiar, para refletir as mudanças em tempo real)
            self.network = G_reference
        else:
            print(f"[Warning] Grafo fornecido é None para o trem {getattr(self, 'trainID', 'N/A')}.")

            
       
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
        self.G_full = G
        self.grid = NetworkGrid(G)
        self.station_table = STATION_TABLE
        self.itinerary_table = ITINERARY_TABLE
        
        nodes = list(G.nodes)
       
        
        # Retorna os valores de criação de instância para cada estação da STATION_TABLE
        station_namelist, station_ids, n_stations, time_stop_list,enable_stop_list = get_station_info(STATION_TABLE) 
        
        # Retorna os valores de criação de instância para cada estação da TRAIN_TABLE
        train_namelist, train_ids, n_trains, itinerary, size_list, init_velocity_list =  get_train_info(TRAIN_TABLE)
        
        # Instanciamento de n agentes
        train_agents = Train.create_agents(model=self, pos = None, n=n_trains, ID=train_ids, ITINERARY = itinerary, name = train_namelist, size = size_list, init_velocity = init_velocity_list)
        station_agents = Station.create_agents(model=self, pos = None, n=n_stations, ID = station_ids, name = station_namelist, time_stop = time_stop_list, enable_stop = enable_stop_list)
        
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
    
    def reverse_overlap(self,a1, a2, edge_weight):
        """
        Verifica se dois trens se sobrepõem numa mesma aresta.
        
        a1, a2: objetos trem com atributos displacement e size
        edge_weight: peso/length da aresta
        """
    
        # Calcula intervalo físico de a1
        half1 = a1.size / 2
        start1 = a1.displacement - half1
        end1 = a1.displacement + half1
    
        # Calcula intervalo físico de a2, invertendo deslocamento se necessário
        half2 = a2.size / 2
        # assume que a2 está indo na direção oposta
        start2 = edge_weight - a2.displacement - half2
        end2 = edge_weight - a2.displacement + half2
    
        # Verifica sobreposição
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
                a.update_target =True
                a.just_arrived = True


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
        Detecta colisões entre trens considerando:
        - Sobreposição na mesma aresta (mesma direção)
        - Cruzamento em direções opostas
        - Colisão em nós
        Marca self.crash = True e zera velocidade em caso de colisão.
        """
        
        for i in range(len(agents_list)):
            a1 = agents_list[i]
            for j in range(i + 1, len(agents_list)):
                a2 = agents_list[j]
    
                # Se ambos já colidiram, ignora
                if a1.crash and a2.crash:
                    continue
    
                # --- Determinar aresta atual de cada trem ---
                edge1 = (a1.node, a1.node_target)
                edge2 = (a2.node, a2.node_target)
    
                # Se algum trem não está se movendo, edge é None
                moving1 = a1.node_target is not None
                moving2 = a2.node_target is not None
    
                # --- (1) Colisão frontal ou na mesma direção na mesma aresta ---
                if moving1 and moving2:
                    same_edge = (edge1 == edge2)
                    opposite_edge = (edge1 == (edge2[1], edge2[0]))
    
                    # mesma direção
                    if same_edge:
                        if self.overlap(a1, a2):
                            a1.crash = a2.crash = True
                            a1.velocity = a2.velocity = 0
                            continue
    
                    # direção oposta
                    elif opposite_edge:
                        try:
                            weight = self.grid.G.edges[edge1]['weight']
                        except KeyError:
                            weight = self.grid.G.edges[(edge1[1], edge1[0])]['weight']
                        if self.reverse_overlap(a1, a2, weight):
                            a1.crash = a2.crash = True
                            a1.velocity = a2.velocity = 0
                            continue
    
                # --- (2) Colisão em nó ---
                # Se ambos estão no mesmo nó (ou um está chegando nesse nó)
                if a1.node == a2.node:
                    a1.crash = a2.crash = True
                    a1.velocity = a2.velocity = 0
                    continue
    
                # Se a1 chegou no nó destino de a2 (ou vice-versa)
                if moving1 and a1.node_target == a2.node:
                    # a1 atingiu a posição de a2 parado
                    a1.crash = a2.crash = True
                    a1.velocity = a2.velocity = 0
                    continue
    
                if moving2 and a2.node_target == a1.node:
                    a1.crash = a2.crash = True
                    a1.velocity = a2.velocity = 0
                    continue

  

    def update_individual_networks(self):
        """
        Cria grafos individuais para cada trem:
        - Cada trem vê todas as arestas exceto as ocupadas por outros trens,
          incluindo trens parados ou em deslocamento.
        """
        for a in self.Train_agents:
            # --- 1. Cria uma cópia do grafo base ---
            G_personal = self.G_full.copy()
    
            for b in self.Train_agents:
                if b == a:
                    continue  # ignora o próprio trem
    
                # Se o trem está em movimento (mesmo sem node_target definido), bloqueia arestas saindo do nó
                if b.node is not None:
                    neighbors = list(self.G_full.neighbors(b.node))
                    for neigh in neighbors:
                        if G_personal.has_edge(b.node, neigh):
                            G_personal.remove_edge(b.node, neigh)
    
                # Se houver target, bloqueia aresta específica
                if b.node_target is not None:
                    edge = (b.node, b.node_target)
                    rev_edge = (b.node_target, b.node)
                    if edge in G_personal.edges:
                        G_personal.remove_edge(*edge)
                    if rev_edge in G_personal.edges:
                        G_personal.remove_edge(*rev_edge)
    
            # Atualiza a visão do trem
            a.update_network_reference(G_personal)



            
            
    def update_runtime_graph(self):
        """
        Cria uma cópia do grafo original e remove as arestas atualmente ocupadas
        pelos trens em movimento (ou seja, trens que estão efetivamente entre dois nós).
        Trens parados em estação (OnStop=True) não bloqueiam as vias.
        """
        # Faz uma cópia profunda do grafo original
        self.G_runtime = copy.deepcopy(self.grid.G)
    
        removed_edges = []
    
        for train in self.Train_agents:
            # 🚫 Ignora trens parados na estação ou sem destino ativo
            if train.OnStop or train.node_target is None:
                continue
    
            edge = (train.node, train.node_target)
            rev_edge = (train.node_target, train.node)
    
            # Remove a aresta correspondente à via que o trem ocupa
            if self.G_runtime.has_edge(*edge):
                self.G_runtime.remove_edge(*edge)
                removed_edges.append(edge)
            elif self.G_runtime.has_edge(*rev_edge):
                self.G_runtime.remove_edge(*rev_edge)
                removed_edges.append(rev_edge)

    
       
    def step(self):
        
        print("\n=== STEP ===")
        
        # (1) Cada trem define sua próxima missão (ex: destino, itinerário, etc.)
        for a in self.Train_agents:     
            print(f"Train {a.trainID}: displacement={a.displacement}, advance={a.advance_to_next_node}")
            a.set_next_mission()
        
        # (2) Cada trem calcula o próximo nó de destino (node_target)
        for a in self.Train_agents: 
            a.calculate_target_node()
        
        # (3) Se o trem não estiver parado em estação, calcula o deslocamento
        # até o próximo nó (displacement → progresso dentro da aresta)
        for a in self.Train_agents: 
            if not a.OnStop:
                a.calculate_displacement_to_target()
            
        # (4) Lista de nós bloqueados (vazia neste caso, mas pode ser usada futuramente)
        blocked_nodes = []
        # blocked_nodes = self.get_blocked_positions(self.Train_agents)
    
        # (5) Detecta colisões entre trens:
        # - No mesmo nó
        # - Na mesma aresta (mesma direção)
        # - Em arestas opostas (colisão frontal)
        self.detect_collisions(self.Train_agents)
    
        # (6) Atualiza a posição dos trens no grafo,
        # movendo-os para o nó de destino se possível
        self.update_train_position(blocked_nodes)
        
        # (7) Gerencia interação entre estações e trens:
        # aplica e libera paradas conforme regras de tempo de parada
        for s in self.Station_agents:
            # Lista trens atualmente localizados na estação s
            trains_at_station = [
                a for a in self.Train_agents if a.node == s.node
            ]
            for a in trains_at_station:
                # Se o trem acabou de chegar e pode parar, aplica parada
                if not a.OnStop and a.just_arrived:
                    s.set_stop_to_train(a)
                    a.just_arrived = False  # reseta flag
                # Se o trem está parado, decrementa tempo de parada
                # e libera quando o tempo acabar
                elif a.OnStop:
                    s.remove_step(a)
                    if a.stop_steps <= 0:
                        s.release_train_from_stop(a)
                        
        # (8) Atualiza o grafo dinâmico (G_runtime),
        # removendo arestas atualmente ocupadas por trens em movimento
        self.update_individual_networks()
        self.update_runtime_graph()
    
        
        
        


