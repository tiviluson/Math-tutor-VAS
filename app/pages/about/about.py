import dash
from dash import dcc
import dash_ag_grid as dag
from dash_iconify import DashIconify
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, clientside_callback, no_update, callback

dash.register_page(__name__, path='/about')

layout = dcc.Markdown('''
### **This is the about page**
''')
