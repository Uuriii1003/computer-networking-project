import dash
from dash import html, dcc, Input, Output
import dash_cytoscape as cyto
import json

# Load the JSON file you produced earlier
try:
    with open('results.json', 'r') as f:
        trace_data = json.load(f)
except FileNotFoundError:
    # Placeholder data if the file isn't found yet
    trace_data = {"Example": []}

def build_elements(data):
    elements = []
    # Starting Node
    elements.append({'data': {'id': 'root', 'label': '💻 My Computer', 'ip': 'Local', 'name': 'localhost', 'rtt': 0}})
    
    for target_ip, hops in data.items():
        prev_node = 'root'
        for i, series in enumerate(hops):
            # Check for a valid response in the series
            valid_responses = [p for p in series if p['ip'] is not None]
            
            if not valid_responses:
                # Handle a complete timeout (The '*' in traceroute)
                node_id = f"timeout_{i}"
                label = f"Hop {i+1}: TIMEOUT"
                node_ip, node_name, node_rtt = "Unknown", "*", 0
                weight = 1 # Thin line for timeouts
            else:
                # Use the first successful response for the node data
                res = valid_responses[0]
                node_id = res['ip']
                label = f"Hop {i+1}: {node_id}"
                node_ip, node_name, node_rtt = res['ip'], res['name'], res['rtt']
                
                #Thickness based on successful packets in series (out of 3)
                weight = (len(valid_responses) / 3) * 6

            # Add the Node
            elements.append({
                'data': {
                    'id': node_id, 
                    'label': label, 
                    'ip': node_ip, 
                    'name': node_name, 
                    'rtt': node_rtt
                }
            })
            
            # Add the Edge (Link)
            elements.append({
                'data': {
                    'source': prev_node, 
                    'target': node_id, 
                    'weight': weight
                }
            })
            prev_node = node_id
            
    return elements

# --- INITIALIZE APP ---
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Header([
        html.H1("Network Topology Visualizer", style={'color': 'white', 'margin': '0'}),
        html.P("Interactive Traceroute Tree: UDP, TCP, and ICMP Analysis", style={'color': '#bdc3c7'})
    ], style={'backgroundColor': '#2c3e50', 'padding': '20px', 'textAlign': 'center', 'marginBottom': '20px'}),

    html.Div([
        # LEFT PANEL: PERSON 2 (Inspection & Stats)
        html.Div([
            html.H3("🕵️ Hop Inspector"),
            html.Div(id='inspector-output', children=[
                html.P("Click a node on the graph to see RTT and DNS details.", style={'fontStyle': 'italic', 'color': '#7f8c8d'})
            ], style={'padding': '15px', 'backgroundColor': '#ecf0f1', 'borderRadius': '8px', 'minHeight': '200px'})
        ], style={'width': '25%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),

        # RIGHT PANEL: PERSON 3 (The Graph)
        html.Div([
            cyto.Cytoscape(
                id='cytoscape-network',
                layout={'name': 'breadthfirst', 'roots': '[id = "root"]', 'padding': 30},
                style={'width': '100%', 'height': '600px', 'backgroundColor': '#f9f9f9', 'border': '1px solid #ddd'},
                elements=build_elements(trace_data),
                # PERSON 1: VISUAL STYLING
                stylesheet=[
                    {
                        'selector': 'node',
                        'style': {
                            'content': 'data(label)',
                            'text-valign': 'center',
                            'color': 'white',
                            'text-outline-width': 2,
                            'text-outline-color': '#2980b9',
                            'background-color': '#3498db',
                            'width': '40px',
                            'height': '40px'
                        }
                    },
                    {
                        'selector': 'edge',
                        'style': {
                            'width': 'data(weight)',
                            'line-color': '#95a5a6',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'opacity': 0.7
                        }
                    },
                    {
                        'selector': '[rtt > 50]', # Highlight slow hops
                        'style': {'background-color': '#e67e22'}
                    },
                    {
                        'selector': '[ip = "Unknown"]', # Highlight timeouts
                        'style': {'background-color': '#c0392b', 'shape': 'diamond'}
                    }
                ]
            )
        ], style={'width': '70%', 'display': 'inline-block', 'padding': '10px'})
    ], style={'display': 'flex', 'justifyContent': 'space-around'})
])

# --- PERSON 2: INTERACTIVE CALLBACKS ---
@app.callback(
    Output('inspector-output', 'children'),
    Input('cytoscape-network', 'tapNodeData')
)
def update_inspector(data):
    if not data:
        return html.P("Click a node to inspect.")
    
    return [
        html.B(f"Target IP: {data['ip']}", style={'fontSize': '18px'}),
        html.Hr(),
        html.P(f"📍 DNS Name: {data['name']}"),
        html.P(f"⏱️ Response Time: {data['rtt']:.2f} ms"),
        html.P(f"🚦 Status: {'Online' if data['ip'] != 'Unknown' else 'Request Timed Out'}", 
               style={'color': '#27ae60' if data['ip'] != 'Unknown' else '#c0392b', 'fontWeight': 'bold'})
    ]

if __name__ == '__main__':
    app.run(debug=True)