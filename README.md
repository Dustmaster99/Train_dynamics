# Train Dynamics

Simulador de dinâmica ferroviária baseado em agentes utilizando grafos, Mesa e NetworkX.

---

# Sobre o Projeto

O **Train Dynamics** é um simulador ferroviário desenvolvido em Python com foco em:

- Simulação multiagente
- Dinâmica ferroviária
- Controle de ocupação de vias
- Roteamento dinâmico
- Detecção de colisões
- Estudos operacionais ferroviários
- Pesquisa em sistemas complexos

O sistema modela a ferrovia como um grafo, onde:

- **Nós** representam estações ou pontos ferroviários
- **Arestas** representam trilhos
- **Trens** são agentes autônomos que navegam pela rede

---

# Tecnologias Utilizadas

- Python
- Mesa
- NetworkX
- NumPy
- Pandas
- Matplotlib

---

# Arquitetura do Projeto

```text
Train_Dynamics/
│
├── run.py
├── run_case_1.py
├── run_case_2.py
│
├── Configuration/
│   ├── definitions.py
│   └── classes.py
│
├── classes/
│   ├── Agents.py
│   ├── Generate_network.py
│   ├── plot.py
│   └── functions.py
│
└── Logs/
```

---

# Principais Componentes

## TrainFlowModel

Classe principal da simulação.

Responsável por:

- criação do grafo ferroviário
- gerenciamento dos agentes
- atualização temporal
- coleta de métricas
- gerenciamento da rede dinâmica

---

## Classe Train

Representa um trem em circulação.

### Funcionalidades:

- movimentação entre nós
- cálculo de deslocamento
- roteamento via Dijkstra
- detecção de colisão
- controle de velocidade
- controle de itinerário

---

## Classe Station

Representa estações ferroviárias.

### Funcionalidades:

- controle de parada
- gerenciamento de embarque lógico
- liberação de trens
- atualização de missões

---

# Modelo de Simulação

A simulação funciona em passos discretos de tempo:

```python
for t in range(n_steps):
    model.step()
```

Cada `step()` executa:

1. Atualização de itinerários
2. Escolha do próximo nó
3. Cálculo de deslocamento
4. Detecção de colisões
5. Atualização de posições
6. Processamento de estações
7. Atualização do grafo dinâmico
8. Coleta de métricas

---

# Sistema de Navegação

O projeto utiliza:

```python
nx.dijkstra_path()
```

para calcular o menor caminho entre:

- posição atual do trem
- próximo destino

O sistema suporta:

- bloqueios dinâmicos
- ocupação de vias
- reroteamento

---

# Sistema de Colisões

O simulador detecta:

- colisões na mesma via
- colisões frontais
- colisões em nós
- sobreposição física entre trens

As colisões são tratadas automaticamente:

```python
a1.crash = True
a2.crash = True
```

---

# Sistema Cinemático

Cada trem possui:

| Variável | Descrição |
|---|---|
| velocity | velocidade atual |
| displacement | posição atual na aresta |
| size | tamanho físico do trem |
| node | nó atual |
| node_target | próximo nó |

---

# Rede Dinâmica

Cada trem possui uma visão personalizada da rede ferroviária.

O sistema:

- remove arestas ocupadas
- bloqueia vias em uso
- evita conflitos
- permite reroteamento dinâmico

---

# Logging e Métricas

O projeto utiliza o `Mesa DataCollector` para registrar:

- velocidade média
- posição dos trens
- colisões
- eventos
- histórico de itinerários

Os dados podem ser exportados para CSV:

```python
model.export_CSV("Logs")
```

Arquivos gerados:

- trains.csv
- stations.csv
- model.csv
- model_events.csv

---

# Exemplo de Execução

```python
model = TrainFlowModel(
    adj_matrix,
    station_nodes_list,
    train_nodes_list,
    train_table,
    station_table,
    itinerary_table
)

for _ in range(100):
    model.step()
```

---

# Possíveis Aplicações

- Simulação ferroviária
- Estudos operacionais
- Pesquisa acadêmica
- Sistemas multiagentes
- Digital Twins
- Reinforcement Learning
- Controle de tráfego ferroviário
- Otimização logística

---

# Melhorias Futuras

- Paralelização em GPU
- Dijkstra em GPU
- Controle centralizado
- Sinalização ferroviária
- Reinforcement Learning
- Visualização 3D
- Interface gráfica
- Multi-linhas ferroviárias
- Sistema de prioridades

---

# Requisitos

Instale as dependências:

```bash
pip install mesa networkx numpy pandas matplotlib
```

---

# Execução

```bash
python run.py
```

---

# Repositório

:contentReference[oaicite:0]{index=0}

---

# Autor

José Henrique Alves de Oliveira

- Engenharia Elétrica — UNICAMP
- Mestrado em Sistemas Complexos e Machine Learning
- Pesquisa em:
  - sistemas complexos
  - modelagem
  - reinforcement learning
  - sistemas multiagentes
  - dinâmica ferroviária
