# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 15:43:12 2025

@author: eosjo
"""

import networkx as nx
import numpy as np
import pandas as pd
import random
import string
from Configuration.definitions import *

def gerar_matriz_adjacencia_1(topo_type: str, **kwargs) -> np.ndarray:
    """
    Gera matriz de adjacência baseada em diversas topologias de rede
    
    Parâmetros:
    -----------
    topo_type : str
        Tipo de topologia:
        - "erdos_renyi": Grafo aleatório de Erdős-Rényi
        - "watts_strogatz": Grafo small-world de Watts-Strogatz
        - "barabasi_albert": Grafo scale-free de Barabási-Albert
        - "regular": Grafo regular
        - "geometrico": Grafo geométrico aleatório
        - "bipartido": Grafo bipartido aleatório
        - "complete": Grafo completo
        - "star": Grafo estrela
        - "wheel": Grafo roda
        - "grid": Grafo grade 2D
        - "hypercube": Hipercubo
        - "powerlaw": Grafo com distribuição power-law
        - "random_tree": Árvore aleatória
        - "random_lobster": Grafo lobster aleatório
        - "social": Grafo com estrutura social (community)
    
    Retorna:
    --------
    np.ndarray
        Matriz de adjacência do grafo gerado
    """
    
    # Mapeamento de parâmetros padrão para cada topologia
    default_params = {
        "erdos_renyi": {"n": 10, "p": 0.3},
        "watts_strogatz": {"n": 10, "k": 4, "p": 0.3},
        "barabasi_albert": {"n": 10, "m": 2},
        "regular": {"n": 10, "d": 3},
        "geometrico": {"n": 10, "radius": 0.3, "dim": 2},
        "bipartido": {"n": 5, "m": 5, "p": 0.4},
        "complete": {"n": 10},
        "star": {"n": 10},
        "wheel": {"n": 10},
        "grid": {"dim": [3, 3]},
        "hypercube": {"n": 4},
        "powerlaw": {"n": 10, "gamma": 2.5},
        "random_tree": {"n": 10},
        "random_lobster": {"n": 10, "p1": 0.7, "p2": 0.5},
        "social": {"n": 10, "k": 3, "p": 0.1, "q": 0.01}
    }
    
    # Combinar parâmetros padrão com os fornecidos pelo usuário
    params = default_params.get(topo_type, {}).copy()
    params.update(kwargs)
    
    try:
        # Gerar grafo baseado na topologia selecionada
        if topo_type == "erdos_renyi":
            G = nx.erdos_renyi_graph(n=params["n"], p=params["p"])
            
        elif topo_type == "watts_strogatz":
            G = nx.watts_strogatz_graph(n=params["n"], k=params["k"], p=params["p"])
            
        elif topo_type == "barabasi_albert":
            G = nx.barabasi_albert_graph(n=params["n"], m=params["m"])
            
        elif topo_type == "regular":
            G = nx.random_regular_graph(d=params["d"], n=params["n"])
            
        elif topo_type == "geometrico":
            G = nx.random_geometric_graph(n=params["n"], radius=params["radius"], dim=params["dim"])
            
        elif topo_type == "bipartido":
            G = nx.bipartite.random_graph(n=params["n"], m=params["m"], p=params["p"])
            
        elif topo_type == "complete":
            G = nx.complete_graph(params["n"])
            
        elif topo_type == "star":
            G = nx.star_graph(params["n"] - 1)  # Ajuste pois star_graph(k) tem k+1 nós
            
        elif topo_type == "wheel":
            G = nx.wheel_graph(params["n"])
            
        elif topo_type == "grid":
            if isinstance(params["dim"], int):
                G = nx.grid_2d_graph(params["dim"], params["dim"])
            else:
                G = nx.grid_2d_graph(params["dim"][0], params["dim"][1])
            # Converter para grafo com nós numerados (não coordenadas)
            G = nx.convert_node_labels_to_integers(G)
            
        elif topo_type == "hypercube":
            G = nx.hypercube_graph(params["n"])
            
        elif topo_type == "powerlaw":
            G = nx.powerlaw_cluster_graph(n=params["n"], m=3, p=0.05)
            
        elif topo_type == "random_tree":
            G = nx.random_tree(n=params["n"])
            
        elif topo_type == "random_lobster":
            G = nx.random_lobster(n=params["n"], p1=params["p1"], p2=params["p2"])
            
        elif topo_type == "social":
            # Grafo com estrutura de comunidade (mais realista para redes sociais)
            G = nx.connected_caveman_graph(l=params["n"]//2, k=params["k"])
            
        else:
            raise ValueError(f"Topologia '{topo_type}' não é suportada")
        
        # Converter para matriz de adjacência
        adj_matrix = nx.adjacency_matrix(G).todense()
        
        # Adicionar pesos aleatórios se solicitado
        if kwargs.get("weighted", False):
            for u, v in G.edges():
                G[u][v]['weight'] = np.random.uniform(0.1, 1.0)
            adj_matrix = nx.adjacency_matrix(G).todense()
        
        return np.array(adj_matrix)
        
    except Exception as e:
        raise ValueError(f"Erro ao gerar grafo do tipo '{topo_type}': {str(e)}")

# Função auxiliar para visualizar a matriz
def visualizar_matriz_adjacencia(matriz_adjacencia, titulo="Matriz de Adjacência"):
    """
    Exibe a matriz de adjacência de forma formatada
    """
    df = pd.DataFrame(matriz_adjacencia)
    print(f"{titulo}:\n")
    print(df.to_string())
    print(f"\nDimensão: {matriz_adjacencia.shape}")
    print(f"Densidade: {np.sum(matriz_adjacencia > 0) / (matriz_adjacencia.shape[0] * matriz_adjacencia.shape[1]):.3f}")



import numpy as np
import random

import numpy as np
import random

def gerar_matriz_adjacencia_2(num_nos, peso_min, peso_max, direcionado=False):
    """
    Gera matriz de adjacência replicando um padrão de rede em camadas:
    - Nó 0 e nó n-1 são de grau 1
    - Nós intermediários formam duas camadas (ou mais) com ramificações e convergências
    - Rede é sempre conectada
    - Pesos aleatórios entre peso_min e peso_max
    """
    adj_matrix = np.zeros((num_nos, num_nos), dtype=int)
    
    # Dividir nós em camadas
    camada_entrada = [0]
    camada_saida = [num_nos-1]
    
    # Distribuir nós intermediários em duas "sub-camadas"
    intermediarios = list(range(1, num_nos-1))
    meio = len(intermediarios) // 2
    camada_1 = intermediarios[:meio]
    camada_2 = intermediarios[meio:]
    
    # Conectar entrada à primeira camada
    for i in camada_1:
        peso = random.randint(peso_min, peso_max)
        adj_matrix[0, i] = peso
        if not direcionado:
            adj_matrix[i, 0] = peso
    
    # Conectar primeira camada à segunda camada
    for i in camada_1:
        j = random.choice(camada_2)
        peso = random.randint(peso_min, peso_max)
        adj_matrix[i, j] = peso
        if not direcionado:
            adj_matrix[j, i] = peso
    
    # Conectar segunda camada à saída
    for j in camada_2:
        peso = random.randint(peso_min, peso_max)
        adj_matrix[j, num_nos-1] = peso
        if not direcionado:
            adj_matrix[num_nos-1, j] = peso
    
    return adj_matrix


def insert_random_nones(station_nodes, n):
    if n < len(station_nodes):
        raise ValueError("n deve ser maior ou igual ao tamanho da lista original")
    
    result = station_nodes[:]  # cópia da lista
    extra_nones = n - len(station_nodes)

    # posições válidas para inserção (apenas entre 1 e len(result)-1)
    positions = list(range(1, len(result)))  
    
    for _ in range(extra_nones):
        pos = random.choice(positions)
        result.insert(pos, None)
        # atualizar posições (mas sempre mantendo início e fim fixos)
        positions = list(range(1, len(result)))  
    
    return result


# =============================================
# Função principal
# =============================================
def criar_rede_completa(n, i, z, p=100, STEP_SCALE=1):
    """
    Gera:
      1. adj_matrix formatada (com rótulos)
      2. TRAIN_TABLE com objetos train_data
      3. ITINERARY_TABLE com objetos itinerary_data

    Parâmetros:
      n : número de nós de entrada
      i : número de nós intermediários
      z : número de nós de saída
      p : peso padrão
      STEP_SCALE : fator de escala de velocidade

    Retorna:
      adj_matrix, TRAIN_TABLE, ITINERARY_TABLE
    """

    letras = list(string.ascii_uppercase)
    total = n + i + z

    # ==========================================================
    # 1️⃣ MATRIZ DE ADJACÊNCIA
    # ==========================================================
    adj_matrix = [[0]*total for _ in range(total)]
    entrada_idx = range(0, n)
    inter_idx = range(n, n+i)
    saida_idx = range(n+i, total)

    # --- Diagonal: Entradas
    for j, e in enumerate(entrada_idx):
        adj_matrix[e][e] = [f"S_{letras[j]}", f"T_{letras[j]}"]

    # --- Diagonal: Intermediárias
    for h in inter_idx:
        adj_matrix[h][h] = 0  # intermediária permanece sem rótulo

    # --- Diagonal: Saídas
    for k, s in enumerate(saida_idx, start=n):
        adj_matrix[s][s] = [f"S_{letras[k]}", None]

    # --- Conexões (bidirecionais)
    for e in entrada_idx:
        for h in inter_idx:
            adj_matrix[e][h] = p
            adj_matrix[h][e] = p
    for h in inter_idx:
        for s in saida_idx:
            adj_matrix[h][s] = p
            adj_matrix[s][h] = p

    # ==========================================================
    # 2️⃣ TRAIN_TABLE (usando train_data)
    # ==========================================================
    TRAIN_TABLE = {}
    for idx, letra in enumerate(letras[:n], start=1):
        TRAIN_TABLE[f"T_{letra}"] = train_data(
            name=f"T_{letra}",
            ID=idx,
            itinerary=f"I_{letra}",
            size=10,
            init_velocity=round(20 * STEP_SCALE)
        )

    # ==========================================================
    # 3️⃣ ITINERARY_TABLE (usando itinerary_data)
    # ==========================================================
    ITINERARY_TABLE = {}

    if n > z:
        print("AVISO: há mais entradas do que saídas únicas. Algumas não terão destino exclusivo.")

    for j in range(n):
        entrada_letra = letras[j]
        saida_letra = letras[j + n]  # desloca n posições no alfabeto

        path = [f"S_{entrada_letra}", f"S_{saida_letra}"]

        ITINERARY_TABLE[f"I_{entrada_letra}"] = itinerary_data(
            path=path,
            start_station=f"S_{entrada_letra}",
            end_station=f"S_{saida_letra}"
        )

    return adj_matrix, TRAIN_TABLE, ITINERARY_TABLE
