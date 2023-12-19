import dash
from dash import dcc
from dash import html
from dash import dash_table

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Menú de Navegación'),

    dcc.Link('Formulario de Usuarios', href='/formulario'),
    html.Br(),
    dcc.Link('Tabla de Usuarios', href='/tabla_usuarios'),
    html.Br(),

    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/formulario':
        return html.Div([
            html.H1('Formulario de Usuarios'),
            dcc.Input(id='nombre', type='text', placeholder='Nombre', value=''),
            dcc.Input(id='email', type='email', placeholder='Email', value=''),
            html.Button('Enviar', id='submit-button', n_clicks=0),
            html.Div(id='output-container-button', children='Hit the button to update.')
        ])
    elif pathname == '/tabla_usuarios':
        # Puedes hacer una solicitud HTTP a la segunda Lambda para obtener datos de DynamoDB
        # y mostrarlos en la tabla
        # data = obtener_datos_lambda_segunda()
        return html.Div([
            html.H1('Usuarios registrados'),
            dash_table.DataTable(
                columns=[{'name': key, 'id': key} for key in data[0].keys()],
                data=data
            )
        ])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=80, debug=True)
