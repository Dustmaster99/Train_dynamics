# -*- coding: utf-8 -*-
"""
Created on Thu Sep  4 15:30:51 2025

@author: eosjo
"""

import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import webbrowser
import os

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


def plot_network_state(G, time):
    """
    Plota o grafo de forma visual e organizada:
    - Estações com formato quadrado e cor laranja
    - Trens com formato circular e cor verde
    - Nomes das estações e IDs dos trens
    - Pesos das arestas
    - Ignora elementos None nos nós
    """
    pos = nx.spring_layout(G, seed=42)

    # Desenha nós por tipo de agente
    for n in G.nodes():
        if n is None:
            continue  # ignora elementos None
        agents = G.nodes[n].get('agent', [])
        if agents:
            station_present = any(type(agent).__name__ == "Station" for agent in agents)
            if station_present:
                nx.draw_networkx_nodes(G, pos, nodelist=[n], node_color='orange', node_shape='s', node_size=900)
            else:
                nx.draw_networkx_nodes(G, pos, nodelist=[n], node_color='skyblue', node_shape='o', node_size=800)
        else:
            nx.draw_networkx_nodes(G, pos, nodelist=[n], node_color='lightgray', node_shape='o', node_size=600)

    # Labels dos nós
    labels_nodes = {}
    for n in G.nodes():
        if n is None:
            continue
        label = str(n)
        agents = G.nodes[n].get('agent', [])
        for agent in agents:
            if type(agent).__name__ == "Station":
                label += f"\nStation: {getattr(agent,'name','')}"
        labels_nodes[n] = label
    nx.draw_networkx_labels(G, pos, labels=labels_nodes, font_size=10)

    # Arestas e pesos
    edge_labels = {}
    for u, v, data in G.edges(data=True):
        if u is None or v is None:
            continue
        edge_labels[(u, v)] = f"{data.get('weight','')}"
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, edge_color='gray')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    # IDs dos trens sobrepostos
    for n, (x, y) in pos.items():
        if n is None:
            continue
        agents = G.nodes[n].get('agent', [])
        y_offset = 0.1
        for agent in agents:
            if type(agent).__name__ == "Train":
                train_id = getattr(agent,'trainID','N/A')
                plt.text(x, y + y_offset, f"Train: {train_id}", fontsize=9,
                         fontweight='bold', color='green',
                         horizontalalignment='center')
                y_offset += 0.1

    plt.title(f"Network State - Step {time}")
    plt.axis('off')
    plt.show()




def plot_network_state_pyvis(G, time):
    """
    Plota o grafo interativo usando Pyvis:
    - Estações: quadrados laranja grandes
    - Trens: círculos verdes menores
    - Nomes das estações e IDs dos trens
    - Pesos das arestas
    - Respeita posições fixas
    """
    import webbrowser
    import networkx as nx
    from pyvis.network import Network

    # Layout fixo
    pos = nx.spring_layout(G, seed=42, k=0.5)  # k controla distância entre nós

    # Cria rede Pyvis
    net = Network(height="750px", width="100%", bgcolor="#f9f9f9", font_color="black")
    
    # Adiciona nós
    for n in G.nodes():
        if n is None:
            continue

        agents = G.nodes[n].get('agent', [])
        label = str(n)
        node_color = "#d3d3d3"  # cinza neutro
        shape = "dot"
        size = 20

        if agents:
            # Estações
            station_present = any(type(agent).__name__ == "Station" for agent in agents)
            if station_present:
                shape = "square"
                node_color = "#FF8C00"  # laranja mais escuro
                size = 40
                station_names = [getattr(agent,'name','') for agent in agents if type(agent).__name__ == "Station"]
                label += "\n" + ", ".join(station_names)
            # Trens
            train_labels = []
            for agent in agents:
                if type(agent).__name__ == "Train":
                    train_id = getattr(agent,'trainID','N/A')
                    train_labels.append(f"Train: {train_id}")
            if train_labels:
                label += "\n" + "\n".join(train_labels)
                node_color = "#32CD32"  # verde limão
                size = 25
                shape = "circle"

        # Adiciona nó com posições fixas
        x, y = pos[n]
        net.add_node(
            n,
            label=label,
            color=node_color,
            shape=shape,
            size=size,
            x=x*1200,  # multiplicador maior para melhor espaçamento
            y=y*1200,
            physics=False
        )

    # Adiciona arestas
    for u, v, data in G.edges(data=True):
        if u is None or v is None:
            continue
        weight = data.get('weight', 1)
        net.add_edge(u, v, value=float(weight), title=str(weight), color='#888888')

    # Configurações visuais adicionais
    net.set_options("""
    var options = {
      "nodes": {
        "font": {"size": 14, "face": "Arial"},
        "borderWidth": 2,
        "borderWidthSelected": 4
      },
      "edges": {
        "color": {"inherit": true},
        "smooth": {"type": "continuous"}
      },
      "physics": {"enabled": false},
      "interaction": {"hover": true}
    }
    """)


    os.chdir(r'C:\Kegle_Jojo\Train_Dynamics\Step_images')
    # Define o nome do arquivo dentro da pasta
    filename = f"network_step_{time}.html"
    net.write_html(filename, notebook=False)



