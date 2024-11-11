import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Cargar los archivos CSV
nodes_df = pd.read_csv('lima_streets_nodes.csv')
edges_df = pd.read_csv('lima_streets_edges.csv')

# Crear el grafo
G = nx.Graph()

# Añadir nodos al grafo
for _, row in nodes_df.iterrows():
    G.add_node(row['node_id'], pos=(row['x'], row['y']))

# Añadir aristas al grafo con la distancia como peso
for _, row in edges_df.iterrows():
    G.add_edge(row['node1'], row['node2'], weight=row['distance'])

# Extraer posiciones de los nodos
pos = nx.get_node_attributes(G, 'pos')
x_nodes = [pos[n][0] for n in G.nodes()]  # Coordenadas X
y_nodes = [pos[n][1] for n in G.nodes()]  # Coordenadas Y
node_ids = list(G.nodes())  # IDs de nodos

# Crear aristas para el gráfico
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

# Crear el grafo con geovizualización
edge_trace = go.Scattermapbox(
    mode='lines',
    lon=edge_x,
    lat=edge_y,
    line=dict(width=0.5, color='#888'),
    hoverinfo='none'
)

node_trace = go.Scattermapbox(
    mode='markers',
    lon=x_nodes,
    lat=y_nodes,
    marker=dict(
        size=10,  # Tamaño de los nodos
        color='blue',  # Color de los nodos
    ),
    text=node_ids,  # Texto que aparece al pasar el cursor
    hoverinfo='text'
)

# Crear la figura de Plotly
fig = go.Figure(data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Grafo de Calles de Lima',
                    showlegend=False,
                    hovermode='closest',
                    mapbox=dict(
                        style="open-street-map",  # Estilo del mapa
                        center=dict(lon=-77.03, lat=-12.04),  # Coordenadas aproximadas de Lima
                        zoom=12
                    ),
                    margin=dict(b=0, l=0, r=0, t=40)
                )
)

# Crear la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout de la aplicación Dash
app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Visualización del Grafo de Calles de Lima"), width=12)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig), width=12)
        ])
    ])
])

# Ejecutar el servidor de Dash
if __name__ == '__main__':
    app.run_server(debug=True)
