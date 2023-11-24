import json
import boto3
import dash
from dash import dcc
from dash import html
from dash import dash_table
import random
import datetime

# Creamos una aplicación Flask
app = dash.Dash(__name__)

# Creamos un cliente de boto3 para acceder a S3
s3 = boto3.client('s3', region_name="eu-west-3")

today = datetime.date.today().strftime('%Y-%m-%d')

# Configuramos la conexión a la tabla de DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')
tabla_usuarios = dynamodb.Table('formulario')

# Función para obtener los datos de la tabla de DynamoDB
def obtener_datos_dynamodb():
    response = tabla_usuarios.scan()
    items = response['Items']
    return items

# Definimos el diseño general de la aplicación
app.layout = html.Div([
    html.H1('Menú de Navegación'),  # Título de la página

    # Menú de navegación
    dcc.Link('Formulario de Usuarios', href='/formulario'),  # Enlace al formulario
    html.Br(),  # Salto de línea
    dcc.Link('Tabla de Usuarios', href='/tabla_usuarios'),  # Enlace a la tabla de usuarios
    html.Br(),  # Salto de línea

    # Aquí se mostrará el contenido de las páginas
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])
# Callback para cargar el contenido de las páginas
@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/formulario':
        # Si el usuario navega al formulario, muestra el contenido del formulario
        return html.Div([
            html.H1('Formulario de Usuarios'),
            dcc.Input(id='nombre', type='text', placeholder='Nombre', value=''),
            dcc.Input(id='email', type='email', placeholder='Email', value=''),
            html.Button('Enviar', id='submit-button', n_clicks=0),
            html.Div(id='output-container-button', children='Hit the button to update.')
        ])
    elif pathname == '/tabla_usuarios':
        # Si el usuario navega a la tabla de usuarios, muestra el contenido de la tabla
        data = obtener_datos_dynamodb()
        return html.Div([
            html.H1('Usuarios registrados'),
            dash_table.DataTable(
                columns=[{'name': key, 'id': key} for key in data[0].keys()],
                data=data
            )
        ])

# Ruta para manejar la subida de datos del formulario
@app.callback(
    dash.dependencies.Output('output-container-button', 'children'),
    [dash.Input('submit-button', 'n_clicks'),
     dash.State('nombre', 'value'),
     dash.State('email', 'value')]
)
def submit_form(n_clicks, nombre, email):
    # Obtenemos los datos del formulario
    usuario = {
        'ID': random.randint(100000, 999999),
        'Nombre': nombre,
        'Correo electrónico': email,
        'Fecha de registro': today
    }
    s3.put_object(Bucket='formulario11', Key=f'usuarios{today}.json', Body=json.dumps(usuario))

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=80, debug=True)