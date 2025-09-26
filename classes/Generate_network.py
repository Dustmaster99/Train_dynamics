# -*- coding: utf-8 -*-
"""
Created on Fri Sep 19 15:43:12 2025

@author: eosjo
"""

import networkx as nx
import numpy as np
import pandas as pd
import random

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




def gerar_matriz_adjacencia_2(
    num_nos,
    min_ligacoes,
    max_ligacoes,
    peso_min,
    peso_max,
    direcionado=False
):
    """
    Gera uma matriz de adjacência para um grafo.

    Parâmetros:
    - num_nos (int): número de nós do grafo
    - min_ligacoes (int): número mínimo de ligações por nó
    - max_ligacoes (int): número máximo de ligações por nó
    - peso_min (int): peso mínimo das arestas
    - peso_max (int): peso máximo das arestas
    - direcionado (bool): se True, cria grafo direcionado; se False, não direcionado

    Retorna:
    - np.ndarray: matriz de adjacência (num_nos x num_nos)
    """
    adj_matrix = np.zeros((num_nos, num_nos), dtype=int)

    for i in range(num_nos):
        num_lig = random.randint(min_ligacoes, max_ligacoes)
        possiveis_vizinhos = list(range(num_nos))
        possiveis_vizinhos.remove(i)
        random.shuffle(possiveis_vizinhos)

        ligacoes = 0
        for j in possiveis_vizinhos:
            if ligacoes >= num_lig:
                break
            if adj_matrix[i, j] == 0:
                peso = random.randint(peso_min, peso_max)
                adj_matrix[i, j] = peso
                if not direcionado:
                    adj_matrix[j, i] = peso
                ligacoes += 1

    return adj_matrix