import dash
from dash import Dash
from dash import Input, Output, callback, html, dcc
import dash_bootstrap_components as dbc

import dotenv
dotenv.load_dotenv()

app = Dash(__name__,
           use_pages=True,
           assets_folder="assets",
           pages_folder="pages",
           external_stylesheets=[dbc.themes.SANDSTONE, dbc.icons.FONT_AWESOME],
           )

sidebar = html.Div(
    [
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    [html.I(className="fas fa-home me-2"), html.Span("Home")],
                    href="/",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-graduation-cap me-2"),
                        html.Span("Tutor"),
                    ],
                    href="/tutor",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fas fa-address-card me-2"),
                        html.Span("About"),
                    ],
                    href="/about",
                    active="exact",
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className="sidebar",
)

app.title = "Math Tutor VAS"
server = app.server
app.config.suppress_callback_exceptions = True

navbar = dbc.NavbarSimple(
    children=[
        # dbc.NavItem(dbc.NavLink("About", href="/about"), ),
    ],
    brand="Math Tutor VAS",
    brand_href="#",
    color="#00A86B",
    # dark=False,
    style={"margin": 0, "height": "7vh",}
)

app.layout = html.Div([
    navbar,
    html.Div(
        [
            sidebar,
            dash.page_container,
        ],
        className="content app-flex-wrapper",
    ),
])

if __name__ == "__main__":
    app.run(debug=True)
