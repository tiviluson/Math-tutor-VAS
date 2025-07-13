import dash
from dash import dcc
import dash_ag_grid as dag
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, clientside_callback, no_update, callback

dash.register_page(__name__, path='/tutor')

chat_div = dmc.Stack(id="chat-history", children=[], style={"flexGrow": 1})

layout = dbc.Row(
    [
        dbc.Col(
            [
                html.Div(
                    [
                        dmc.Stack(
                            children=[
                                dbc.Button("Image", id="btn-image-load", color="secondary", className="dbc-button"),
                                dbc.Button("Camera", id="btn-camera-load", color="secondary", className="dbc-button"),
                            ],
                            spacing=1,
                            justify="center",
                            align="flex-start",
                        ),
                        dbc.Input(
                            id="input-text-box",
                            placeholder="Input text box",
                            type="text",
                            className="form-control input-text-box-col",
                            style={
                                    "height": "100px",
                                    "width": "100%",
                                }
                        ),
                        dmc.Stack(
                            children=[
                                dbc.Button("Validate", id="btn-validate", color="primary", className="dbc-button"),
                                dbc.Button("Hint", id="btn-toggle-hint", color="info", className="dbc-button"),
                                dbc.Button("Submit", id="btn-submit", color="success", className="dbc-button"),
                            ],
                            spacing=1,
                            justify="center",
                            align="flex-start",
                        ),
                    ],
                    className="input-section",
                ),
                html.Div(
                        chat_div,
                        id="chat-history-container",
                        style={
                            "border": "1px solid #e0e0e0",
                            "borderRadius": "8px",
                            "padding": "10px",
                            "marginBottom": "10px",
                            "backgroundColor": "#fff",
                            "minHeight": "60vh",
                            "maxHeight": "60vh",
                            "overflowY": "auto"
                        }
                    ),
                    html.Div(
                        [
                            dmc.Textarea(
                                id="input-textarea",
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
                    dcc.Store(id='chat-scroll-trigger', data=0),
            ],
            id="input-section-col",
        )
    ],
    id="input-section-row",
)
