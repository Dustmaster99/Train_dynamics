# -*- coding: utf-8 -*-
"""
Created on Thu Sep  4 14:19:51 2025

@author: eosjo
"""

from dataclasses import dataclass
from pathlib import Path

# mesa_info_flow.py
# Modelo: nós = meio, agentes = informação em movimento
import mesa
import numpy as np
from mesa.space import NetworkGrid
import networkx as nx
import random
from Configuration.definitions import *
from mesa.datacollection import DataCollector

DEBUG = False


@dataclass
class FlagState:
    """Mantém os valores anterior e atual de uma flag de estado."""

    previous: bool = False
    current: bool = False

    def update(self, new_value: bool):
        """Move o valor atual para ``previous`` e registra o novo valor."""
        self.previous = self.current
        self.current = new_value


class StateFlags:
    """Agrupa flags nomeadas e preserva suas transições de estado."""

    def __init__(self, **kwargs):
        self._states = {key: FlagState(value, value) for key, value in kwargs.items()}

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key in self._states:
                self._states[key].update(value)
            else:
                self._states[key] = FlagState(value, value)

    def __getattr__(self, item):
        return self._states[item]


class Station(mesa.Agent):
    def __init__(self,model, pos, ID, name, time_stop, enable_stop, itinerary_table):
        # Pass the parameters to the parent class.
        super().__init__(model)
        
        self.name = name
        self.network = model.grid.G
        self.stationID = ID
        self.node = pos
        self.itineraryTable = itinerary_table
        self.stop_time = time_stop
        self.enable_stop = enable_stop
        self.agent_type = "Station"
        self.currentTrains = None

    def get_next_mission(self, itinerary):
        
        next_mission = get_next_station_from_itinerary_table(self.itineraryTable, itinerary, self.name)
        if next_mission is None:
           return None  # não há próxima missão
        else: 
            return next_mission  
    
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
        self.last_node = None
        
        #Itinerary Information
        self.itinerary = ITINERARY
        self.itinerary_start_time = None
        self.itinerary_end_time = None
        

        self.next_mission = None
        self.name = name
        self.agent_type = "Train"
        self.update_target = True
        self.node_target = None
        
        # Flags 
        self.is_itinerary_active = FlagState(False, False)
        self.OnStop = False
        self.just_arrived = False 
        self.advance_to_next_node = False # bool variable to see if the object already moved pass the treshold of advancing to next node
        self.crash = False
       
        # cinematic data
        self.init_velocity = init_velocity
        self.velocity = 0 # velocity in m/s
        self.displacement = 0 # Displacement position in the current adge. ( All trains start at 0 ) 
        self.size = size
        self.stop_steps = 0;
        
        
         
        
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
        Impede múltiplos trens escolherem o mesmo target no mesmo step.
        """
        previous_target = self.node_target  # salva valor anterior
        
        if self.update_target and self.next_mission is not None:
            try:
                # Caminho mínimo usando Dijkstra
                path = nx.dijkstra_path(
                    self.network, int(self.node), int(self.next_mission), weight="weight"
                )
    
                if len(path) > 1:
                    proposed_target = int(path[1])  # próximo nó
    
                    # --- VERIFICA SE O TARGET ESTÁ BLOQUEADO ---
                    if proposed_target in self.model.step_blocked_targets:
                        # Target ocupado neste step → não muda node_target
                        if DEBUG:
                            print(f"Train {self.trainID}: target {proposed_target} blocked this step")
                        self.node_target = None
                        self.update_target = True
                        return
                    else:
                        # Target livre → atualiza e bloqueia
                        self.node_target = proposed_target
                        self.model.step_blocked_targets.add(proposed_target)
                else:
                    # Já está no destino
                    self.node_target = int(self.node)
                
                # Caminho válido encontrado
                self.update_target = False
    
            except nx.NetworkXNoPath:
                # Sem caminho → mantém nó atual
                self.node_target = int(self.node)
                
        # --- Atualiza velocidade ---
        if not self.OnStop:
            if self.next_mission is None:
                # Sem próxima missão → velocidade zero obrigatória
                self.velocity = 0
            elif self.update_target and (self.node_target is None or self.node_target == previous_target):
                # Tentou atualizar o target mas falhou ou permaneceu o mesmo
                self.velocity = 0
            elif self.node_target is not None and not self.update_target:
                # Target válido e atualização concluída
                self.velocity = self.init_velocity

    
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
            print(f"ERRO: Train {self.trainID} - Aresta ({self.node},{self.node_target}) não existe!")
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
                print(f"AVISO: Distância não-positiva entre {self.node} e {self.node_target}")
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
            print(f"ERRO: KeyError inesperado: {e}")
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
            self.next_mission = None
            self.is_itinerary_active.update(False)
            return
        
        # Procura o agente Station correspondente para pegar o nó
        target_station_agent = next(
            (a for a in self.model.Station_agents if a.name == next_station_name),
            None
        )
        
        if target_station_agent is not None:
            # Atualiza next_mission com o nó da rede, e define o itinerario como ativo
            self.next_mission = target_station_agent.node
            self.is_itinerary_active.update(True)
            
            
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
    
    def check_itinerary_status(self):
        """
       Verifica se houve transição de True→False na flag `is_itinerary_active`.
       Caso sim, registra no histórico global do modelo.
       """
        # Transição de inicio de itinerário
        if(self.is_itinerary_active.previous == False) and (self.is_itinerary_active.current == True):
            self.itinerary_start_time = self.model.step_count * STEP_SCALE
        
        # Transição de fim de itinerário
        if(self.is_itinerary_active.previous == True) and (self.is_itinerary_active.current == False):
            self.itinerary_end_time = self.model.step_count * STEP_SCALE
            delta = self.itinerary_end_time - self.itinerary_start_time
            # adiciona um registro no histórico do modelo
            self.model.itinerary_historian.append({
                "name": self.itinerary,
                "delta": delta
            })
            
            
            
        
            
            
       
class TrainFlowModel(mesa.Model):
    """
    Modelo com:
      - Grafo como meio de transmissão.
      - Agentes como Trens viajando.
    """
    
    def __init__(self, adj_matrix, station_nodes_list, train_nodes_list , train_table ,station_table, itinerary_table, LogMetrics = True, seed = None):
        
        super().__init__(seed=seed)
        # cria grafo determinado pela matrix de adjacências adj_matrix
        G = nx.from_numpy_array(np.array(adj_matrix))
        self.LogMetrics = LogMetrics
        
        # concatena os nomes das estações aos nós pertencentes das mesmas
        for i, station_name in enumerate(station_nodes_list ):
            G.nodes[i]['station_name'] = station_name
        
        # concatena os nomes das estações aos nós pertencentes das mesmas
        for i, train_name in enumerate(train_nodes_list ):
            G.nodes[i]['train_name'] = train_name
        
        
        # Importa informações de topologia :
        self.G_full = G
        self.grid = NetworkGrid(G)
        self.train_table = train_table
        self.station_table = station_table
        self.itinerary_table = itinerary_table
        self.itinerary_historian = []
        self.step_blocked_targets = set()  # armazena targets já escolhidos neste step
        nodes = list(G.nodes)
        self.step_count = 0
       
        
        # Retorna os valores de criação de instância para cada estação da STATION_TABLE
        station_namelist, station_ids, n_stations, time_stop_list,enable_stop_list = get_station_info(self.station_table) 
        
        # Retorna os valores de criação de instância para cada estação da TRAIN_TABLE
        train_namelist, train_ids, n_trains, itinerary, size_list, init_velocity_list =  get_train_info(self.train_table)
        
        # Instanciamento de n agentes
        train_agents = Train.create_agents(model=self, pos = None, n=n_trains, ID=train_ids, ITINERARY = itinerary, name = train_namelist, size = size_list, init_velocity = init_velocity_list)
        station_agents = Station.create_agents(model=self, pos = None, n=n_stations, ID = station_ids, name = station_namelist, time_stop = time_stop_list, enable_stop = enable_stop_list,itinerary_table = self.itinerary_table)
        
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
        
            # Para estatísticas gerais do modelo
        self.model_datacollector = DataCollector(
            model_reporters={
                "n_trains": lambda m: m.get_n_trains(),
                "mean speed": lambda m: m.get_mean_speed(),
                "n_crashed_trains": lambda m: m.get_n_crashes(),
                "Time": lambda m: (m.step_count) * STEP_SCALE
            }
        )
        
        self.model_events_datacollector = DataCollector(
            model_reporters={
                "itinerary_historian": lambda m: list(m.itinerary_historian)
            }
        )

                # Para os trens
        self.train_datacollector = DataCollector(
            agent_reporters={
                "Agent type": lambda a: a.agent_type if getattr(a, "agent_type", None) == "Train" else None,
                "Name": lambda a: a.name if getattr(a, "agent_type", None) == "Train" else None,
                "Node": lambda a: a.node if getattr(a, "agent_type", None) == "Train" else None,
                "Last Node": lambda a: a.last_node if getattr(a, "agent_type", None) == "Train" else None,
                "Next Mission": lambda a: a.next_mission if getattr(a, "agent_type", None) == "Train" else None,
                "Itinerary": lambda a: a.itinerary if getattr(a, "agent_type", None) == "Train" else None,
                "Train ID": lambda a: a.trainID if getattr(a, "agent_type", None) == "Train" else None,
                "Size": lambda a: a.size if getattr(a, "agent_type", None) == "Train" else None,
                "Crash": lambda a: a.crash if getattr(a, "agent_type", None) == "Train" else None,
                "Onstop": lambda a: a.OnStop if getattr(a, "agent_type", None) == "Train" else None,
                "Velocity": lambda a: a.velocity if getattr(a, "agent_type", None) == "Train" else None,
                "Time": lambda a: a.model.step_count * STEP_SCALE if getattr(a, "agent_type", None) == "Train" else None,
            }
        )
        
        # Para as estações
        self.station_datacollector = DataCollector(
            agent_reporters={
                "Agent type": lambda a: a.agent_type if getattr(a, "agent_type", None) == "Station" else None,
                "Name": lambda a: a.name if getattr(a, "agent_type", None) == "Station" else None,
                "Node": lambda a: a.node if getattr(a, "agent_type", None) == "Station" else None,
                "Station ID": lambda a: a.stationID if getattr(a, "agent_type", None) == "Station" else None,
                "Stop time": lambda a: a.stop_time if getattr(a, "agent_type", None) == "Station" else None,
                "Enable_stop": lambda a: a.enable_stop if getattr(a, "agent_type", None) == "Station" else None,
                "Trains at station": lambda a: a.currentTrains if getattr(a, "agent_type", None) == "Station" else None,
                "Time": lambda a: a.model.step_count * STEP_SCALE if getattr(a, "agent_type", None) == "Station" else None,
            }
        )

        
    def get_mean_speed(self):
        n_agents = len(self.Train_agents)
        if n_agents == 0:
            return 0.0  # ou None, dependendo do que faz sentido
        t_speed = sum(a.velocity for a in self.Train_agents)
        mean_speed = t_speed / n_agents
        return mean_speed

    
    def get_n_crashes (self):
        crashes_count = 0
        for a in self.Train_agents:
            if(a.crash == True):
                crashes_count += 1
        return crashes_count
    
    def get_n_trains (self):
        n_count = 0
        for a in self.Train_agents:
            n_count += 1
        return n_count
            
            
        
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
    
                # --- 2. Bloqueia arestas saindo do nó do trem b ---
                if b.node is not None:
                    neighbors = list(self.G_full.neighbors(b.node))
                    for neigh in neighbors:
                        if G_personal.has_edge(b.node, neigh):
                            G_personal.remove_edge(b.node, neigh)
    
                # --- 3. Bloqueia todas as arestas saindo do node_target de b ---
                if b.node_target is not None:
                    target_neighbors = list(G_personal.neighbors(b.node_target))
                    for neigh in target_neighbors:
                        if G_personal.has_edge(b.node_target, neigh):
                            G_personal.remove_edge(b.node_target, neigh)
    
            # Atualiza a visão do trem
            a.update_network_reference(G_personal)    




            
            
    def update_runtime_graph(self):
        """
        Cria uma cópia do grafo original e remove as arestas atualmente ocupadas
        pelos trens em movimento (ou seja, trens que estão efetivamente entre dois nós).
        Trens parados em estação (OnStop=True) não bloqueiam as vias.
        """
        # Copia apenas a estrutura do grafo. Uma cópia profunda tentaria copiar
        # agentes, modelo e NetworkGrid, que possuem referências circulares.
        self.G_runtime = self.grid.G.copy()
    
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

    
    def export_CSV(self, path):
        """
        Exporta os dados dos coletores para CSV.
        Caminhos relativos são resolvidos a partir do diretório de execução;
        caminhos absolutos são usados diretamente.
        """
        full_path = Path(path).expanduser().resolve()
        full_path.mkdir(parents=True, exist_ok=True)
    
        # Obtém os DataFrames
        df_trains   = self.train_datacollector.get_agent_vars_dataframe()
        df_stations = self.station_datacollector.get_agent_vars_dataframe()
        df_model    = self.model_datacollector.get_model_vars_dataframe()
        df_events = self.model_events_datacollector.get_model_vars_dataframe()
        
        if "Train ID" in df_trains.columns:
            df_trains = df_trains[df_trains["Train ID"].notna()]
        if "Station ID" in df_stations.columns:
            df_stations = df_stations[df_stations["Station ID"].notna()]
    
        # Monta caminhos completos
        trains_path = full_path / "trains.csv"
        stations_path = full_path / "stations.csv"
        model_path = full_path / "model.csv"
        events_path = full_path / "model_events.csv"
    
        # Salva em CSV
        df_trains.to_csv(trains_path, index=False)
        df_stations.to_csv(stations_path, index=False)
        df_model.to_csv(model_path, index=False)
        df_events.to_csv(events_path, index=False)
    
        print(f"Arquivos exportados para: {full_path}")
        
        
    def step(self):
        
        print("\n=== STEP ===")
        
        
        # (0) Limpa ao inicio de cada iteração os targets já bloqueados na própria interação 
    
        self.step_blocked_targets.clear()  # limpa o bloqueio de step anterior
        
        # (1) Cada trem define sua próxima missão (ex: destino, itinerário, etc.)
        for a in self.Train_agents:     
            print(f"Train {a.trainID}: displacement={a.displacement}, advance={a.advance_to_next_node}")
            a.set_next_mission()
            a.check_itinerary_status()
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
            # Informação para logar os trens parados na estação no step determinado
            s.currentTrains = trains_at_station
            
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
        
        # (9) Coleta os dados da simulação, caso a flag seja True
        if getattr(self, "LogMetrics", False):
            self.train_datacollector.collect(model=self)
            self.station_datacollector.collect(model=self)
            self.model_datacollector.collect(model=self)
       
        # (10) Atualiza a contagem de steps da simulação em 1
        self.step_count += 1
        
        
        


