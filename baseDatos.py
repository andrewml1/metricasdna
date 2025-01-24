import json
import psycopg2
import pandas as pd

#####Postgres Azure

def conectarCredenciales(usuario):
    # Specify the filename
    filename = "database_config.json"

    # Load the JSON data from the file
    with open(filename, "r") as json_file:
        data = json.load(json_file)

    # Choose a user (e.g., "Admin" or "SanPedro")
    chosen_user = usuario

    # Get the attributes for the chosen user
    user_attributes = data.get(chosen_user, None)
    return user_attributes

def crearTablasPostgres(credenciales):

    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    cursor = conn.cursor()

    cursor = conn.cursor()
    # Verificar si la tabla existe
    table_name = 'integrantes'
    cursor.execute(
        f"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name}';"
    )
    result = cursor.fetchone()

    if result is None:
        # Crear la tabla si no existe
        cursor.execute('''
            CREATE TABLE integrantes (
                ID SERIAL PRIMARY KEY,        -- ID autoincremental como clave primaria
                correo TEXT NOT NULL,         -- Correo del integrante
                nombre TEXT NOT NULL,         -- Nombre del integrante
                habilitado BOOLEAN DEFAULT TRUE -- Indica si el integrante está habilitado (por defecto TRUE)
            );
        ''')

    cursor = conn.cursor()
    # Verificar si la tabla existe
    table_name = 'proyectos'
    cursor.execute(
        f"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name}';"
    )
    result = cursor.fetchone()

    if result is None:
        # Crear la tabla si no existe
        cursor.execute('''
            CREATE TABLE proyectos (
                ID SERIAL PRIMARY KEY,        -- ID autoincremental como clave primaria
                nombre_proyecto TEXT NOT NULL, -- Nombre del proyecto (obligatorio)
                habilitado BOOLEAN DEFAULT TRUE -- Indica si el proyecto está habilitado (por defecto TRUE)
            );
        ''')

    # Verificar si la tabla existe
    table_name = 'metricas'
    cursor.execute(
        f"SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name}';"
    )
    result = cursor.fetchone()

    if result is None:
        # Crear la tabla si no existe
        cursor.execute('''
            CREATE TABLE metricas (
                ID SERIAL PRIMARY KEY,                -- ID autoincremental como clave primaria
                integrante_id INTEGER NOT NULL,       -- Foreign key hacia la tabla integrantes
                proyecto_id INTEGER NOT NULL,         -- Foreign key hacia la tabla proyectos
                dedicacion NUMERIC(5, 2) NOT NULL,    -- Dedicación como porcentaje
                riesgo INTEGER NOT NULL,              -- Riesgo como entero
                valor INTEGER NOT NULL,               -- Valor como entero
                CONSTRAINT fk_integrante FOREIGN KEY (integrante_id) REFERENCES integrantes(ID) ON DELETE CASCADE,               -- Si se elimina el integrante, se eliminan sus métricas
                CONSTRAINT fk_proyecto FOREIGN KEY (proyecto_id) REFERENCES proyectos(ID) ON DELETE CASCADE                -- Si se elimina el proyecto, se eliminan sus métricas
            );
        ''')

    # Commit the transaction
    conn.commit()
    # Close the connection
    conn.close()

# cr=conectarCredenciales('admin')
# crearTablasPostgres(cr)

#Que pasa si se borra un integrante?
def guardar_datos_integrantes():

        credenciales=conectarCredenciales('admin')

        conn = psycopg2.connect(
            database=credenciales["database"],
            user=credenciales["user"],
            password=credenciales["password"],
            host=credenciales["host"],
            port=credenciales["port"]
        )

        # Leer el archivo CSV
        df = pd.read_csv('integrantes.csv', sep=';')

        cursor = conn.cursor()
        # Insertar los datos del DataFrame en la tabla
        # Insertar datos del DataFrame en la tabla
        for _, row in df.iterrows():
            query = '''
            INSERT INTO integrantes (correo, nombre, habilitado) 
            VALUES ({correo}, {nombre}, {habilitado})
            '''.format(
                correo=f"'{row['correo']}'",  # Envolver en comillas simples
                nombre=f"'{row['nombre']}'",  # Envolver en comillas simples
                habilitado=row['habilitado']  # Asegurar que sea un valor numérico o booleano
            )
            cursor.execute(query)

        conn.commit()
        conn.close()

#Que pasa si se borra un proyecto?
def guardar_datos_proyectos():
    credenciales = conectarCredenciales('admin')

    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    # Leer el archivo CSV
    df = pd.read_csv('proyectos.csv', sep=';')

    cursor = conn.cursor()
    # Insertar los datos del DataFrame en la tabla
    for _, row in df.iterrows():
        query = '''
            INSERT INTO proyectos (nombre_proyecto, habilitado) 
            VALUES ({nombre_proyecto},{habilitado})
            '''.format(
            nombre_proyecto=f"'{row['nombre_proyecto']}'",  # Envolver en comillas simples
            habilitado=row['habilitado']  # Asegurar que sea un valor numérico o booleano
        )
        cursor.execute(query)

    conn.commit()
    conn.close()

# guardar_datos_proyectos()

def integrantesCorreo(credenciales):

    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    cursor = conn.cursor()

    cursor.execute("SELECT correo FROM integrantes;") ##Poner el orderby

    # Fetch the result
    queryData = cursor.fetchall()

    return queryData

def listaProyectos(credenciales):

    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    cursor = conn.cursor()

    cursor.execute("SELECT nombre_proyecto FROM proyectos;") ##Poner el orderby

    # Fetch the result
    queryData = cursor.fetchall()

    return queryData

def obtenerIdIntegrantePorCorreo(credenciales, correo):
    # Conectar a la base de datos
    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )
    cursor = conn.cursor()

    # Consulta para obtener el ID del integrante según el correo
    query = "SELECT ID FROM integrantes WHERE correo = %s AND habilitado = TRUE"
    cursor.execute(query, (correo,))

    # Obtener el resultado
    result = cursor.fetchone()
    integrante_id = result[0] if result else None

    # Cerrar conexión
    cursor.close()
    conn.close()

    return integrante_id

def obtenerIdProyecto(credenciales, proyecto):
    # Conectar a la base de datos
    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )
    cursor = conn.cursor()

    # Consulta para obtener el ID del integrante según el correo
    query = "SELECT ID FROM proyectos WHERE nombre_proyecto = %s AND habilitado = TRUE"
    cursor.execute(query, (proyecto,))

    # Obtener el resultado
    result = cursor.fetchone()
    IdProyecto = result[0] if result else None

    # Cerrar conexión
    cursor.close()
    conn.close()

    return IdProyecto

def guardarMetricas(credenciales,idIntegrante, idProyecto, dedicacion, riesgo, valor):

    conn =psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    cursor = conn.cursor()

    query = f'''
    INSERT INTO metricas (
        integrante_id, proyecto_id, dedicacion, riesgo, valor
    ) VALUES ({idIntegrante}, '{idProyecto}', '{dedicacion}', '{riesgo}', '{valor}')
    '''

    cursor.execute(query)

    # Commit the transaction
    conn.commit()

    # Close the connection
    conn.close()

#
#
# def borrar_pruebas(credenciales,identif):
#     # Establecer la conexión
#     conn = psycopg2.connect(
#         database=credenciales["database"],
#         user=credenciales["user"],
#         password=credenciales["password"],
#         host=credenciales["host"],
#         port=credenciales["port"]
#     )
#     cursor = conn.cursor()
#
#     cursor.execute("DELETE FROM evaluaciones WHERE ID IN (SELECT ID FROM paciente WHERE cedula = %s);"
#              ,(identif,))
#     # query = "DELETE FROM evaluaciones WHERE ID IN (SELECT ID FROM paciente WHERE timeinicio < '2024-08-23');"
#
#     cursor.execute("DELETE FROM paciente WHERE cedula = %s;"
#             , (identif,))
#
#     cursor.execute("DELETE FROM nuevos_seguimientos WHERE cedula = %s;"
#             , (identif,))
#
#     conn.commit()
#     # Cerrar el cursor y la conexión
#     conn.close()
# # Borra con la cedula
# # cred= credenciales("admin")
# # borrar_pruebas(cred,'1213')


