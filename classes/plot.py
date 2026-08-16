# -*- coding: utf-8 -*-
"""
Created on Thu Sep  4 15:30:51 2025

@author: eosjo
"""

import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

def print_network_state(G, time):
    """
    Imprime informações detalhadas do grafo e dos agentes de forma legível:
    - Destaca atributos principais de Train e Station.
    - Lista outros atributos de forma resumida.
    """
    print(f"\n{'='*40} Starting Step {time} {'='*40}\n")
    
    print("=== NODES ===")
    for node, data in G.nodes(data=True):
        agents = data.get('agent', [])
        if agents:
            for agent in agents:
                agent_type = type(agent).__name__
                attrs = vars(agent)
                
                print(f"Nó {node} -> Agente tipo {agent_type}:")
                
                if agent_type == 'Train':
                    # Destacar atributos principais
                    main_attrs = ['trainID', 'node', 'next_mission', 'node_target', 'displacement', 'advance_to_next_node', 'velocity']
                    for attr in main_attrs:
                        if attr in attrs:
                            print(f"   {attr}: {attrs[attr]}")
                    
                elif agent_type == 'Station':
                    main_attrs = ['stationID', 'name', 'node']
                    for attr in main_attrs:
                        if attr in attrs:
                            print(f"   {attr}: {attrs[attr]}")
                
                # Exibe outros atributos de forma resumida
                other_attrs = {k: v for k, v in attrs.items() if k not in main_attrs}
                if other_attrs:
                    print("   Outros atributos:")
                    for k, v in other_attrs.items():
                        print(f"      {k}: {v}")
                
                print("-"*50)
        else:
            print(f"Nó {node} não tem agentes.")
    
    print("\n=== EDGES ===")
    for u, v, data in G.edges(data=True):
        weight = data.get('weight')
        if weight is not None:
            print(f"A aresta de {u} -> {v} tem peso: {weight}")
        else:
            print(f"A aresta de {u} -> {v} não tem peso.")
    
    print(f"{'='*100}\n")


def plot_network_state(G_original, G_runtime, time, output_file=None, show=True):
    """
    Plota o grafo mostrando:
    - Estações (quadrados laranja)
    - Trens (círculos verdes ou vermelhos se crash=True)
    - Arestas bloqueadas (removidas em G_runtime) em vermelho tracejado
    - Pesos das arestas
    """
    pos = nx.spring_layout(G_original, seed=42)

    # === (1) Identificar arestas bloqueadas ===
    edges_original = set(G_original.edges())
    edges_runtime = set(G_runtime.edges())
    blocked_edges = edges_original - edges_runtime
    active_edges = edges_runtime

    # === (2) Nós ===
    for n in G_original.nodes():
        if n is None:
            continue
        agents = G_original.nodes[n].get('agent', [])
        if agents:
            station_present = any(type(agent).__name__ == "Station" for agent in agents)
            if station_present:
                nx.draw_networkx_nodes(G_original, pos, nodelist=[n], node_color='orange', node_shape='s', node_size=900)
            else:
                nx.draw_networkx_nodes(G_original, pos, nodelist=[n], node_color='skyblue', node_shape='o', node_size=800)
        else:
            nx.draw_networkx_nodes(G_original, pos, nodelist=[n], node_color='lightgray', node_shape='o', node_size=600)

    # === (3) Labels dos nós ===
    labels_nodes = {}
    for n in G_original.nodes():
        if n is None:
            continue
        label = str(n)
        agents = G_original.nodes[n].get('agent', [])
        for agent in agents:
            if type(agent).__name__ == "Station":
                label += f"\nStation: {getattr(agent,'name','')}"
        labels_nodes[n] = label
    nx.draw_networkx_labels(G_original, pos, labels=labels_nodes, font_size=10)

    # === (4) Desenha arestas ===
    nx.draw_networkx_edges(G_original, pos, edgelist=list(active_edges),
                           width=2, alpha=0.6, edge_color='gray')

    if blocked_edges:
        nx.draw_networkx_edges(G_original, pos, edgelist=list(blocked_edges),
                               width=3, alpha=0.9, edge_color='red', style='dashed')

    # === (5) Labels dos pesos ===
    edge_labels = {}
    for u, v, data in G_original.edges(data=True):
        if u is None or v is None:
            continue
        edge_labels[(u, v)] = f"{data.get('weight','')}"
    nx.draw_networkx_edge_labels(G_original, pos, edge_labels=edge_labels, font_color='black', font_size=8)

    # === (6) Trens e labels ===
    for n, (x, y) in pos.items():
        if n is None:
            continue
        agents = G_original.nodes[n].get('agent', [])
        y_offset = 0.1
        for agent in agents:
            if type(agent).__name__ == "Train":
                color = 'red' if getattr(agent, 'crash', False) else 'green'
                name = getattr(agent, 'name', getattr(agent,'trainID','N/A'))
                displacement = getattr(agent, 'displacement', 0)
                label = f"{name} ({displacement:.1f})"
                plt.text(x, y + y_offset, label, fontsize=9, fontweight='bold',
                         color=color, horizontalalignment='center')
                y_offset += 0.1

    # === (7) Título e layout ===
    plt.title(f"Network State - Step {time}\n"
              f"Blocked edges: {len(blocked_edges)}", fontsize=12)
    plt.axis('off')
    plt.tight_layout()

    if output_file is not None:
        output_path = Path(output_file).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close()
