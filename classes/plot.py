# -*- coding: utf-8 -*-
"""
Created on Thu Sep  4 15:30:51 2025

@author: eosjo
"""

import networkx as nx
import matplotlib.pyplot as plt

# --- Função de print ---
def print_network_state(G, time):
    """
    Imprime informações detalhadas do grafo.
    """
    
    print("\n=========================================Starting Step" + f"{time}" + "============================================================== ===")
    print("=== NODES ===")
    
    for node, data in G.nodes(data=True):
        agents = data.get('agent', [])
        if agents:  # se houver algum agente no nó
            train = agents[0]  # pega o primeiro agente da lista
            print(f"Nó {node}, ID do agente: {train.trainID}")
        else:
            print(f"Nó {node} não tem agentes.")

    
    print("\n=== EDGES ===")
    for u, v, data in G.edges(data=True):
        weight = data.get('weight')
        if weight:  # se houver distancia no nó
            dist = weight  # pega o primeiro agente da lista
            print(f"a aresta de {u} -> [v] tem peso peso: {dist}")
        else:
            print(f"a aresta de {u} -> [v]  não tem pesos.")
    print("\n=================================================================================================================== ===")

def plot_network_state(G, time):
    pos = nx.spring_layout(G)

    # Nós
    labels_nodes = {n: f"{n}\n{G.nodes[n].get('label', '')}" for n in G.nodes()}
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=800)
    nx.draw_networkx_labels(G, pos, labels=labels_nodes, font_size=10)

    # Arestas
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, edge_color='gray')

    # Pesos das arestas
    edge_labels = {(u, v): f"{data.get('weight','')}" for u, v, data in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    # IDs dos trens sobrepostos
    for n, (x, y) in pos.items():
        agents = G.nodes[n].get('agent', [])
        if agents:
            train_id = agents[0].trainID
            plt.text(x, y + 0.1, f"Train: {train_id}", fontsize=9,
                     fontweight='bold', color='green',
                     horizontalalignment='center')

    plt.axis('off')
    plt.show()


