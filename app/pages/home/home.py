import dash
from dash import dcc
dash.register_page(__name__, path='/')


layout = dcc.Markdown('''
### **This is the home page**
''')
