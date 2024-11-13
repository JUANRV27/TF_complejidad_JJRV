import osmnx as ox
import pandas as pd

# Descargar el grafo de calles para Lima
G = ox.graph_from_place("Lima, Peru", network_type="drive")

# Extraer nodos y aristas con información detallada
nodes, edges = ox.graph_to_gdfs(G)

# Verificar las columnas y el índice de 'edges'
print("Índice de 'edges':", edges.index)
print("Columnas de 'edges':", edges.columns)

# Inicializar la columna de tipo "type" para los nodos
nodes['type'] = 'secundario'  # Establecer "secundario" como valor predeterminado

# Marcar nodos conectados a calles principales o carreteras como "principal" o "carretera"
for index, row in edges.iterrows():
    # Verificar que "highway" no sea NaN y sea un string
    highway = row.get('highway')
    if isinstance(highway, str):  # Asegurarse de que 'highway' es un string
        if 'motorway' in highway or 'primary' in highway:
            u, v, _ = index  # Obtener los nodos de origen y destino
            nodes.loc[nodes.index.isin([u, v]), 'type'] = 'principal'
        elif 'secondary' in highway or 'tertiary' in highway:
            u, v, _ = index  # Obtener los nodos de origen y destino
            nodes.loc[nodes.index.isin([u, v]), 'type'] = 'carretera'

# Crear las columnas 'u' y 'v' en el DataFrame de aristas a partir del índice
# Si las columnas 'u' y 'v' no están, agregamos estas a partir de la información de los nodos
if 'u' not in edges.columns or 'v' not in edges.columns:
    edges['u'], edges['v'], _ = zip(*edges.index)

# Guardar los nodos y aristas en archivos CSV
nodes[['x', 'y', 'type']].to_csv("lima_streets_nodes_classified.csv", index=False)

# Guardar el DataFrame de edges con las columnas 'u' y 'v'
edges[['u', 'v', 'length']].to_csv("lima_streets_edges_2.csv", index=False)
