import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

# Rede circular regular (p = 0)
G_circular = nx.watts_strogatz_graph(n=12, k=2, p=0)

plt.figure(figsize=(8, 6))
nx.draw_circular(G_circular, node_size=300, with_labels=True, node_color='lightblue')
plt.title("Rede Circular Regular (p = 0)\nAlto Clustering, Alto Caminho Médio")
plt.show()

# Métricas
clustering = nx.average_clustering(G_circular)
path_length = nx.average_shortest_path_length(G_circular)
print(f"p=0: Clustering={clustering:.3f}, Caminho Médio={path_length:.3f}")



# Rede small-world (p = 0.05)
G_smallworld = nx.watts_strogatz_graph(n=12, k=2, p=0.05)

plt.figure(figsize=(8, 6))
nx.draw_circular(G_smallworld, node_size=300, with_labels=True, node_color='lightgreen')
plt.title("Rede Small-World (p = 0.05)\nAlto Clustering, Baixo Caminho Médio")
plt.show()

# Métricas
clustering = nx.average_clustering(G_smallworld)
path_length = nx.average_shortest_path_length(G_smallworld)
print(f"p=0.05: Clustering={clustering:.3f}, Caminho Médio={path_length:.3f}")

# Mostrar os atalhos criados
print("Atalhos criados (rewiring):")
for edge in G_smallworld.edges():
    node1, node2 = edge
    distance = min(abs(node1 - node2), 12 - abs(node1 - node2))
    if distance > 2:  # Conexões que não são entre vizinhos diretos
        print(f"  Atalho: {node1} ↔ {node2} (distância: {distance})")
        
        
# Rede de transição (p = 0.5)
G_transicao = nx.watts_strogatz_graph(n=12, k=2, p=0.5)

plt.figure(figsize=(8, 6))
nx.draw_circular(G_transicao, node_size=300, with_labels=True, node_color='orange')
plt.title("Rede de Transição (p = 0.5)\nClustering Médio, Caminho Médio")
plt.show()

# Métricas
clustering = nx.average_clustering(G_transicao)
path_length = nx.average_shortest_path_length(G_transicao)
print(f"p=0.5: Clustering={clustering:.3f}, Caminho Médio={path_length:.3f}")

# Análise da estrutura
print("Rede em estado de transição:")
print(f"- Aproximadamente {int(0.5 * 12 * 2)} conexões foram reconectadas")
print("- Nem totalmente regular, nem totalmente aleatória")



# Rede aleatória (p = 1)
G_aleatoria = nx.watts_strogatz_graph(n=12, k=2, p=1)

plt.figure(figsize=(8, 6))
nx.draw_circular(G_aleatoria, node_size=300, with_labels=True, node_color='lightcoral')
plt.title("Rede Aleatória (p = 1)\nBaixo Clustering, Baixo Caminho Médio")
plt.show()

# Métricas
clustering = nx.average_clustering(G_aleatoria)
path_length = nx.average_shortest_path_length(G_aleatoria)
print(f"p=1: Clustering={clustering:.3f}, Caminho Médio={path_length:.3f}")

# Comparação com Erdős-Rényi
G_er = nx.erdos_renyi_graph(n=12, p=0.15)  # Probabilidade similar
clustering_er = nx.average_clustering(G_er)
print(f"Erdős-Rényi similar: Clustering={clustering_er:.3f}")



# Análise comparativa de todas as redes
valores_p = [0, 0.05, 0.5, 1]
redes = []
nomes = ["Circular Regular", "Small-World", "Transição", "Aleatória"]

for p in valores_p:
    G = nx.watts_strogatz_graph(n=12, k=2, p=p)
    redes.append(G)

# Plot comparativo
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

for i, (G, p, nome) in enumerate(zip(redes, valores_p, nomes)):
    ax = axs[i//2, i%2]
    nx.draw_circular(G, ax=ax, node_size=200, with_labels=True)
    
    clustering = nx.average_clustering(G)
    path_length = nx.average_shortest_path_length(G)
    
    ax.set_title(f"{nome} (p={p})\nC={clustering:.2f}, L={path_length:.2f}")

plt.tight_layout()
plt.show()

# Tabela comparativa de métricas
print("COMPARAÇÃO DE MÉTRICAS:")
print("Tipo\t\t\tp\tClustering\tCaminho Médio")
print("-" * 55)
for G, p, nome in zip(redes, valores_p, nomes):
    clustering = nx.average_clustering(G)
    path_length = nx.average_shortest_path_length(G)
    print(f"{nome:20}\t{p}\t{clustering:.3f}\t\t{path_length:.3f}")
    
    
    
    
# Visualizar matrizes de adjacência
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

for i, (G, p, nome) in enumerate(zip(redes, valores_p, nomes)):
    ax = axs[i//2, i%2]
    matriz = nx.adjacency_matrix(G).todense()
    
    im = ax.imshow(matriz, cmap='Blues', interpolation='none')
    ax.set_title(f"{nome} (p={p})")
    ax.set_xlabel('Nó')
    ax.set_ylabel('Nó')
    plt.colorbar(im, ax=ax)

plt.tight_layout()
plt.show()

# Mostrar padrões das matrizes
print("PADRÕES NAS MATRIZES DE ADJACÊNCIA:")
print("• p=0: Diagonal com 1's próximos - padrão regular")
print("• p=0.05: Padrão regular com alguns 1's fora da diagonal - atalhos")
print("• p=0.5: Mistura de padrão regular e aleatório")
print("• p=1: Distribuição aleatória de 1's - padrão desorganizado")