import time 
import dash
import plotly.graph_objects as go
from dash_iconify import DashIconify
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, clientside_callback, no_update

from functions.chatbot import LLMCall, generate_user_bubble, generate_ai_bubble
import os, dotenv; dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")

# --- Global Variables and Helper Functions ---
app = dash.Dash(__name__, assets_folder="assets", external_stylesheets=[dbc.themes.BOOTSTRAP])

# Placeholder for chat history - REMOVED overflowY and maxHeight here
chat_div = dmc.Stack(id="chat-history", children=[], style={"flexGrow": 1})

llm_agent = None

def generate_placeholder_figure(message="Enter a prompt to generate a visualization."):
    fig = go.Figure()
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": message,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 20, "color": "#888"},
                "x": 0.5,
                "y": 0.5,
            }
        ],
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="#f8f9fa",
        plot_bgcolor="#ffffff",
        height=500
    )
    return fig

def generate_simple_plot_from_llm_output():
    data = {'Category': ['A', 'B', 'C', 'D'], 'Value': [10, 25, 13, 30]}
    fig = go.Figure(data=[go.Bar(x=data['Category'], y=data['Value'])])
    fig.update_layout(
        title="Sample Plot from LLM Suggestion",
        xaxis_title="Category",
        yaxis_title="Value",
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="#f8f9fa",
        plot_bgcolor="#ffffff",
        height=500
    )
    return fig


# --- Layout Definition ---
def left_column():
    return dbc.Col(
        [
            dmc.Stack(
                children=[
                    html.Div(
                        chat_div,
                        id="chat-history-container", # Add an ID to the scrollable div
                        style={
                            "border": "1px solid #e0e0e0",
                            "borderRadius": "8px",
                            "padding": "10px",
                            "marginBottom": "10px",
                            "backgroundColor": "#fff",
                            "minHeight": "70vh",
                            "maxHeight": "70vh",
                            "overflowY": "auto"
                        }
                    ),
                    dbc.Col(
                        [
                            dcc.Upload(
                                html.Button('Upload File', 
                                            className="upload-button",
                                ), id="image-loading-button",
                            ),
                            html.Button("Validate", 
                                       id="validate-button",
                                       className="upload-button",
                                       style={'height': '50px'}
                            ),
                        ],
                        style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "marginTop": "10px"
                            }
                    ),
                    html.Div(
                        [
                            dmc.Textarea(
                                id="input-textarea",
                                className="chat-input",
                                placeholder="Enter your prompt here.",
                                autosize=False,
                                radius='md',
                                minRows=1,
                                maxRows=4,
                                style={
                                        "width": "100%",
                                        "flexGrow": 1, # Allows textarea to take available space
                                        "border": "none", # Remove default border
                                        "outline": "none", # Remove outline on focus
                                        "padding": "10px 15px", # Adjust padding
                                        "backgroundColor": "transparent", # Transparent background
                                        "resize": "none", # Disable manual resize by user
                                        "minHeight": "40px"
                                    }
                            ),
                            dmc.Button(
                                dmc.Center(DashIconify(icon="radix-icons:arrow-right", width=24)), # Send icon
                                id="loading-button",
                                variant="filled", # Filled button
                                radius="xl", # Fully rounded button
                                size="md", # Medium size
                                style={
                                    # "marginTop": "10px",
                                    "width": "48px", # Fixed width for a circular/square button
                                    "height": "48px", # Fixed height
                                    "minWidth": "48px", # Prevent shrinking
                                    "padding": 0, # Remove padding to center icon
                                    "backgroundColor": "#339af0", # A nice blue color
                                    "color": "white",
                                    # "marginLeft": "8px", # Space between input and button
                                    # "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
                                    }
                            ),
                        ],
                        style={
                            "display": "flex",
                            "alignItems": "flex-end", # Align items to the bottom (for textarea growth)
                            "border": "1px solid #e0e0e0", # Subtle border for the container
                            "borderRadius": "25px", # Rounded corners for the entire container
                            "padding": "5px", # Padding inside the container
                            "backgroundColor": "#fff",
                            "boxShadow": "0 2px 8px rgba(0,0,0,0.05)", # Subtle shadow
                            "marginTop": "10px",
                        }
                    ),
                    # Hidden dcc.Store to trigger auto-scroll
                    dcc.Store(id='chat-scroll-trigger', data=0),
                    

                ],
                align="stretch",
                spacing="md",
                style={"padding": "20px", "height": "100%"}
            )
        ],
        width=5,
        style={"backgroundColor": "#f5f5f5", "borderRight": "1px solid #e0e0e0", "padding": 0}
    )


def right_column():
    return dbc.Col(
        [
            html.Div(
                [
                    html.H4("Visualization Space", style={"textAlign": "center", "marginBottom": "20px"}),
                    dcc.Graph(
                        id="visualization-graph",
                        figure=generate_placeholder_figure(),
                        style={"width": "100%", "height": "calc(100vh - 120px)"}
                    ),
                ],
                style={"padding": "20px", "height": "100%"}
            ),
        ],
        width=7,
        style={'backgroundColor': '#ffffff', 'padding': 0}
    )

navbar = dbc.NavbarSimple(
    brand="Geometry Tutor",
    brand_href="#",
    color="primary",
    dark=True,
    style={"margin": 0, "height": "7vh",}
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                left_column(),
                right_column()
            ],
            className="g-0",
            style={"minHeight": "100vh"}
        )
    ],
    fluid=True,
    style={"padding": 0}
)
# --- Callbacks ---

# Clientside callback for loading button state
clientside_callback(
    """
    function updateLoadingState(n_clicks) {
        return true;
    }
    """,
    Output("loading-button", "loading", allow_duplicate=True),
    Input("loading-button", "n_clicks"),
    prevent_initial_call=True,
)

def extract_text(node):
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        children = node.get('props', {}).get('children')
        if children is None:
            return "\n" if node.get('type') == 'Br' else ""
        if isinstance(children, list):
            return ''.join(extract_text(child) for child in children)
        return extract_text(children)
    return ''


# Callback to handle chat input and LLM response
@app.callback(
    Output("chat-history", "children"),
    Output("input-textarea", "value"),
    Output("loading-button", "loading"),
    Output("chat-scroll-trigger", "data"), # Add this output for scrolling
    State("chat-history", "children"),
    State("input-textarea", "value"),
    Input("loading-button", "n_clicks"),
    prevent_initial_call=True,
)
def add_chat_card(chat_history, input_text, n_clicks):
    _on_history = False
    if len(chat_history) > 0:
        _on_history = True
        prev_conversation = ''
        for msg in chat_history:
            span = msg['props']['children']
            prev_conversation += extract_text(span).strip() + '\n'

    if input_text is None or input_text.strip() == "":
        return no_update, no_update, False, no_update, no_update # No updates if input is empty

    global llm_agent

    if llm_agent is None:
        llm_agent = LLMCall(GEMINI_API_KEY, GEMINI_MODEL)

    user_card = generate_user_bubble(input_text)
    chat_history.append(user_card)

    llm_response_text = ""
    try:
        if llm_agent:
            if _on_history:
                input_text = f"{prev_conversation}\nStudent: {input_text}\nTutor:"
            else:
                input_text = f"Student: {input_text}\nTutor:"
            
            # Call the LLM agent with the input text
            result = llm_agent({"input": input_text})
            llm_response_text = result.get("output", "No response from Tutor.")
        else:
            llm_response_text = "Tutor agent not initialized!"

    except Exception as e:
        llm_response_text = f"An error occurred with the Tutor: {e}."
    ai_card = generate_ai_bubble(llm_response_text)
    chat_history.append(ai_card)

    # Return the updated chat history, clear input, stop loading, store LLM's raw response,
    # and update the scroll trigger with a new value (e.g., current timestamp)
    return chat_history, "", False, time.time()


# Callback to update the visualization graph based on LLM output
@app.callback(
    Output("visualization-graph", "figure"),
    Input("validate-button", "n_clicks"),
    prevent_initial_call=True,
)
def update_visualization_graph(n_clicks):
    if n_clicks:
        return generate_simple_plot_from_llm_output()
    return generate_placeholder_figure()

# Clientside Callback for Auto-Scrolling
app.clientside_callback(
    """
    function(trigger_data) {
        if (trigger_data === null || trigger_data === 0) { // Check for initial null or 0 value
            return window.dash_clientside.no_update;
        }
        const chatContainer = document.getElementById('chat-history-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        return window.dash_clientside.no_update; // No actual Dash output needed
    }
    """,
    Output('chat-scroll-trigger', 'data', allow_duplicate=True), # Output to itself to avoid warning
    Input('chat-scroll-trigger', 'data'),
    prevent_initial_call=True
)


if __name__ == '__main__':
    app.run(debug=True)