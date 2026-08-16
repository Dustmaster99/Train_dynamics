# -*- coding: utf-8 -*-
"""
Created on Thu Sep 25 22:28:03 2025

@author: eosjo
"""

def zerar_diagonal_principal(adj_matrix):
    """
    Retorna uma cópia da matriz de adjacência com TODAS as tuplas/listas zeradas
    (substituídas por 0)
    """
    nova_matriz = []
    
    for i, linha in enumerate(adj_matrix):
        nova_linha = []
        for j, elemento in enumerate(linha):
            if isinstance(elemento, list):  # Se é uma lista/tupla
                nova_linha.append(0)  # Zera substituindo por 0
            else:
                nova_linha.append(elemento)  # Mantém números como estão
        nova_matriz.append(nova_linha)
    
    return nova_matriz


def extrair_diagonal_principal(adj_matrix):
    """
    Retorna duas listas: uma com os primeiros elementos e outra com os segundos elementos
    das tuplas da diagonal principal
    """
    station_nodes = []
    train_nodes = []
    
    for i in range(len(adj_matrix)):
        elemento_diagonal = adj_matrix[i][i]
        
        if isinstance(elemento_diagonal, list) and len(elemento_diagonal) >= 2:
            station_nodes.append(elemento_diagonal[0])
            train_nodes.append(elemento_diagonal[1])
        else:
            station_nodes.append(None)
            train_nodes.append(None)
    
    return station_nodes, train_nodes
