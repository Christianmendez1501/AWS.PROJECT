# Despliegue de formulario en la plataforma de Amazon Web Services (aws)

<div align="center">
  <img src="https://simpleicons.org/icons/amazonaws.svg" alt="AWS" width="100" />
  <img src="https://simpleicons.org/icons/amazonec2.svg" alt="EC2" width="100" />
  <img src="https://simpleicons.org/icons/amazondynamodb.svg" alt="DynamoDB" width="100" />
  <img src="https://simpleicons.org/icons/amazons3.svg" alt="S3" width="100" />
  <img src="https://simpleicons.org/icons/awslambda.svg" alt="Lambda" width="100" />
</div>



```markdown
## Miembros:
- Cristian Olaya
- Christian Mendez
``````
## Resumen:

### Configurar AWS en la máquina

```bash
aws configure
```

Esto te pedirá que ingreses la información de tus credenciales de AWS:

- AWS Access Key ID: Tu clave de acceso de AWS.
- AWS Secret Access Key: Tu clave secreta de acceso de AWS.
- Default region name: La región de AWS que deseas utilizar (por ejemplo, us-east-1).

## Creación EC2
<details>
<summary>Código</summary>

```bash
aws ec2 run-instances \
    --image-id AMI_ID \
    --instance-type INSTANCE_TYPE \
    --key-name KEY_PAIR_NAME \
    --subnet-id SUBNET_ID \
    --security-group-ids SECURITY_GROUP_ID \
    --region YOUR_REGION
```
</details>

### Creación S3
<details>
<summary>Código</summary>

```bash
aws s3 api create-bucket --bucket NOMBRE_DEL_CUBO --region REGION
```
</details>

Podrías tener problemas con tu región, por lo cual es recomendable usar una variable de entorno:

```bash
export NOMBRE_DE_VARIABLE=valor
```

Para establecerla de manera permanente, generalmente se agrega esa línea al archivo de perfil del usuario, como ~/.bashrc o ~/.bash_profile. Puedes editar estos archivos con un editor de texto como nano o vi. 

Por ejemplo:

```bash
echo 'export NOMBRE_DE_VARIABLE=valor' >> ~/.bashrc
source ~/.bashrc
```

### Creamos el código de la app que vamos a ejecutar
<details>
<summary>Código</summary>

```python
import json
import boto3
import dash
from dash import dcc, html, dash_table
import random
import datetime

# Creamos una aplicación Dash
app = dash.Dash(__name__)

# Configuramos la conexión a la tabla de DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='eu-west-3') #colocar la region que corresponde
tabla_usuarios = dynamodb.Table('formulario') #colocar nopmbre que le hayas puesto a la tabla

# Función para obtener los datos de la tabla de DynamoDB
def obtener_datos_dynamodb():
    response = tabla_usuarios.scan()
    items = response['Items']
    return items

# Definimos el estilo CSS para la página
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Definimos el diseño general de la aplicación
app.layout = html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'text-align': 'center'}, children=[
    html.Div([
        html.H1('Cloud App', style={'color': 'black'}),
    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'margin-bottom': '20px'}),

    # Menú de navegación
    html.Div([
        dcc.Link(html.Button('Formulario de Usuarios', id='btn-formulario', n_clicks=0,
                             style={'background-color': 'black', 'color': 'white', 'border': 'none', 'margin': '10px', 'box-shadow': '2px 2px 5px 0px #000000'}),
                 href='/formulario'),
        dcc.Link(html.Button('Tabla de Usuarios', id='btn-tabla-usuarios', n_clicks=0,
                             style={'background-color': 'black', 'color': 'white', 'border': 'none', 'margin': '10px', 'box-shadow': '2px 2px 5px 0px #000000'}),
                 href='/tabla_usuarios'),
    ], style={'display': 'flex', 'justify-content': 'center'}),

    # Aquí se mostrará el contenido
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
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
            html.H1('Formulario de Usuarios', style={'color': 'black'}),
            dcc.Input(id='nombre', type='text', placeholder='Nombre', value='', style={'margin-bottom': '10px'}),
            dcc.Input(id='email', type='email', placeholder='Email', value='', style={'margin-bottom': '10px'}),
            html.Button('Enviar', id='submit-button', n_clicks=0,
                        style={'background-color': 'black', 'color': 'white', 'border': 'none', 'box-shadow': '2px 2px 5px 0px #000000'}),
            html.Div(id='output-container-button', children='', style={'margin-top': '10px', 'color': 'black'})
        ])
    elif pathname == '/tabla_usuarios':
        # Si el usuario navega a la tabla de usuarios, muestra el contenido de la tabla
        data = obtener_datos_dynamodb()
        return html.Div([
            html.H1('Usuarios registrados', style={'color': 'black'}),
            dash_table.DataTable(
                columns=[{'name': key, 'id': key} for key in data[0].keys()],
                data=data,
                style_table={'overflowX': 'auto', 'border': '1px solid black', 'backgroundColor': 'white'},
                style_header={'backgroundColor': 'black', 'color': 'white', 'fontWeight': 'bold'},
                style_cell={'textAlign': 'left', 'border': '1px solid black'},
                style_data={'border': '1px solid black'},
                style_as_list_view=True
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
        'Fecha de registro': datetime.date.today().strftime('%Y-%m-%d')
    }
    tabla_usuarios.put_item(Item=usuario)
    return f'Se ha enviado el formulario: {nombre}, {email}'

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=80, debug=True)
```
</details>

## Creamos una base de datos en DynamoDB y una función Lambda

### Paso 1: Crear una tabla en DynamoDB
<details>
<summary>Código</summary>

```bash
aws dynamodb create-table \
    --table-name Usuarios \
    --attribute-definitions \
        AttributeName=ID,AttributeType=N \
    --key-schema AttributeName=ID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region tu-region
```
</details>

### Subir el código a un Bucket de S3
<details>
<summary>Código</summary>

Antes de ejecutar el comando para crear la función Lambda, necesitaremos tener el código de la función en un archivo ZIP y almacenarlo en un bucket de S3.

```bash
aws s3 cp tu-archivo-.zip s3://tu-cubo/
```
</details>

### Paso 2: Crear una función Lambda
<details>
<summary>Código</summary>

```bash
aws lambda create-function \
    --function-name GuardarUsuarioEnDynamoDB \
    --runtime python3.8 \
    --role arn:aws:iam::tu-id-de-cuenta:role/el-rol \
    --handler guardar_usuario.handler \
    --code S3Bucket=tu-bucket-con-el-codigo,Key=tu-archivo-zip-con-el-codigo.zip \
    --environment Variables={DYNAMODB_TABLE=Usuarios} \
    --region tu-region
```
</details>

### Paso 3: Crear una función Lambda que se active al crear un objeto en S3
<details>
<summary>Código</summary>

```bash
aws lambda create-function \
    --function-name TriggerLambda \
    --runtime python3.8 \
    --role arn:aws:iam::tu-id-de-cuenta:role/tu-rol \
    --handler trigger_lambda.handler \
    --code S3Bucket=tu-bucket-con-el-codigo,Key=tu-archivo-zip-con-el-codigo.zip \
    --environment Variables={TARGET_LAMBDA_NAME=GuardarUsuarioEnDynamoDB} \
    --region tu-region
```
</details>

### Paso 4: Configurar el evento de S3 para activar la función Lambda
<details>
<summary>Código</summary>

```bash
aws s3api put-bucket-notification-configuration \
    --bucket tu-bucket-s3 \
    --notification-configuration '{"LambdaFunctionConfigurations":[{"LambdaFunctionArn":"arn:aws:lambda:tu-region:tu-id-de-cuenta:function:TriggerLambda","Events":["s3:ObjectCreated:*"]}]}'
```
</details>
```

¡Espero que esto haga que tu README sea más atractivo y fácil de seguir! ¡Si tienes más ajustes o preguntas, házmelo saber!