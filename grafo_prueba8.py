import networkx as nx
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
#El mejor código hasta ahora

# Cargar datos
nodes_ids_df = pd.read_csv('lima_streets_nodes.csv')  # Datos de los nodos con id
nodes_types_df = pd.read_csv('lima_streets_nodes_classified.csv')  # Datos de los nodos con tipo
edges_df = pd.read_csv('lima_streets_edges_2.csv')  # Datos de las aristas

# Asegúrate de que la columna 'type' existe y asigna un valor por defecto en caso de que falte
nodes_ids_df['type'] = nodes_types_df['type'].fillna('desconocido')

# Crear grafo y clasificar nodos principales
G = nx.Graph()

# Agregar nodos al grafo y asegurarse de que cada nodo tiene el atributo 'type'
for _, row in nodes_ids_df.iterrows():
    G.add_node(row['node_id'], pos=(row['x'], row['y']), type=row['type'])

# Usar las columnas correctas: 'u' y 'v' para los nodos, 'length' para la distancia
for _, row in edges_df.iterrows():
    G.add_edge(row['u'], row['v'], weight=row['length'])  # Usar 'u' y 'v' como nodos conectados

# Extraer posiciones de nodos
pos = nx.get_node_attributes(G, 'pos')

# Filtrar nodos que tienen el atributo 'type'
x_nodes_main = [pos[n][0] for n in G.nodes() if 'type' in G.nodes[n] and G.nodes[n]['type'] == 'principal']
y_nodes_main = [pos[n][1] for n in G.nodes() if 'type' in G.nodes[n] and G.nodes[n]['type'] == 'principal']
x_nodes_secondary = [pos[n][0] for n in G.nodes() if 'type' in G.nodes[n] and G.nodes[n]['type'] == 'secundario']
y_nodes_secondary = [pos[n][1] for n in G.nodes() if 'type' in G.nodes[n] and G.nodes[n]['type'] == 'secundario']

# Crear las capas de trazado de nodos
main_nodes_trace = go.Scattermapbox(
    mode='markers',
    lon=x_nodes_main,
    lat=y_nodes_main,
    marker=dict(size=10, color='blue'),
    text=[n for n in G.nodes if 'type' in G.nodes[n] and G.nodes[n]['type'] == 'principal'],
    hoverinfo='text',
    name="Nodos Principales"
)

secondary_nodes_trace = go.Scattermapbox(
    mode='markers',
    lon=x_nodes_secondary,
    lat=y_nodes_secondary,
    marker=dict(size=6, color='green'),
    text=[n for n in G.nodes if 'type' in G.nodes[n] and G.nodes[n]['type'] == 'secundario'],
    hoverinfo='text',
    name="Nodos Secundarios"
)

# Crear la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout con mapa base y un toggle para mostrar u ocultar el grafo completo
app.layout = html.Div([ 
    dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Visualización del Grafo de Calles de Lima"), width=12)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='map-graph', config={'scrollZoom': True}), width=12)
        ]),
        dbc.Row([
            dbc.Col(html.Label("Selecciona el nodo de inicio:"), width=2),
            dbc.Col(dcc.Dropdown(id='start-node', options=[{'label': str(node), 'value': node} for node in G.nodes], placeholder="Selecciona el nodo de inicio"), width=4),
            dbc.Col(html.Label("Selecciona el nodo de destino:"), width=2),
            dbc.Col(dcc.Dropdown(id='end-node', options=[{'label': str(node), 'value': node} for node in G.nodes], placeholder="Selecciona el nodo de destino"), width=4),
        ]),
        dbc.Row([
            dbc.Col(dcc.Checklist(
                id='toggle-graph',
                options=[{'label': 'Mostrar grafo completo', 'value': 'show_graph'}],
                value=[],  # Inicialmente no está seleccionado
                inline=True,
            ), width=12)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='shortest-path-graph', config={'scrollZoom': True}), width=12)
        ])
    ])
])

# Callback para calcular el camino más corto y actualizar los gráficos
@app.callback(
    [Output('map-graph', 'figure'),
     Output('shortest-path-graph', 'figure')],
    [Input('start-node', 'value'),
     Input('end-node', 'value'),
     Input('toggle-graph', 'value'),
     Input('map-graph', 'relayoutData')]  # Este es el zoom que se actualizará para el mapa de arriba
)
def update_graph(start_node, end_node, toggle_value, relayout_data):
    # Mapa principal (solo con nodos y sin aristas)
    zoom_level = relayout_data.get('mapbox.zoom', 10)
    
    data_main = [main_nodes_trace, secondary_nodes_trace]
    if 'show_graph' in toggle_value:  # Solo se agrega el grafo si el toggle está seleccionado
        pass  # No se agregan aristas en este mapa
    
    fig_main = go.Figure(
        data=data_main,
        layout=go.Layout(
            title='Mapa de Calles de Lima',
            mapbox=dict(
                style="open-street-map",
                center=dict(lon=-77.03, lat=-12.04),
                zoom=zoom_level
            ),
            margin=dict(b=0, l=0, r=0, t=40)
        )
    )
    
    # Si no se seleccionan nodos de inicio o destino, no se calcula el camino más corto
    if start_node is None or end_node is None:
        fig_path = go.Figure(
            data=[],
            layout=go.Layout(
                title='Camino Más Corto',
                mapbox=dict(
                    style="open-street-map",
                    center=dict(lon=-77.03, lat=-12.04),
                    zoom=12
                ),
                margin=dict(b=0, l=0, r=0, t=40)
            )
        )
    else:
        try:
            # Calcular el camino más corto
            shortest_path = nx.shortest_path(G, source=start_node, target=end_node, weight='weight')
            path_x = [pos[node][0] for node in shortest_path]
            path_y = [pos[node][1] for node in shortest_path]

            # Crear trazado del camino más corto
            path_trace = go.Scattermapbox(
                mode='markers+lines',
                lon=path_x,
                lat=path_y,
                line=dict(width=4, color='red'),
                marker=dict(size=10, color='red'),
                text=shortest_path,
                hoverinfo='text',
                name='Camino Más Corto'
            )

            # Mapa del camino más corto (solo se actualiza si ambos nodos están seleccionados)
            fig_path = go.Figure(
                data=[path_trace],
                layout=go.Layout(
                    title='Camino Más Corto',
                    mapbox=dict(
                        style="open-street-map",
                        center=dict(lon=-77.03, lat=-12.04),
                        zoom=12
                    ),
                    margin=dict(b=0, l=0, r=0, t=40)
                )
            )
        except nx.NetworkXNoPath:
            # Si no hay camino, devolver un mapa vacío
            fig_path = go.Figure(
                data=[],
                layout=go.Layout(
                    title='Camino Más Corto',
                    mapbox=dict(
                        style="open-street-map",
                        center=dict(lon=-77.03, lat=-12.04),
                        zoom=12
                    ),
                    margin=dict(b=0, l=0, r=0, t=40)
                )
            )

    # Retornar los dos mapas (principal y de camino corto)
    return fig_main, fig_path


if __name__ == '__main__':
    app.run_server(debug=True)
