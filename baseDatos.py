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


def obtenerIdentifPostgres(credenciales):

    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    cursor = conn.cursor()

    cursor.execute("SELECT MAX(ID) FROM paciente")

    # Fetch the result
    max_id = cursor.fetchone()[0]

    # If there are no rows in the `paciente` table yet, set the max_id to 0
    if max_id is None:
        max_id = 0

    # Increment the max_id to get the next available ID for the `evaluaciones` table
    new_id = max_id

    # Close the cursor and the database connection
    cursor.close()
    conn.close()

    return new_id


def autoFillPostgres(credenciales,cedula):

    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM paciente "
                   "WHERE ID = "
                   "(SELECT MAX(ID) "
                   "FROM paciente "
                   "WHERE cedula = %s);",
                   (cedula,))

    # Fetch the result
    result = cursor.fetchall()

    # Convert the result into a list of dictionaries
    data = [dict(zip([desc[0] for desc in cursor.description], row)) for row in result]

    # Convert the data to JSON
    json_data = json.dumps(data)

    # Convert the result into a DataFrame
    # df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

        # Close the cursor and the database connection
    cursor.close()
    conn.close()

    return json_data
#
# cred= credenciales("prosalco")
# autoFillPostgres(cred,1212)

def guardarAnalisisPlanPostgres(credenciales,cedula, inicio_time, tratar_time, notas_time, ip_address, doctores, mc_ea, analisisyplan, ExFis, celular, herramientaRadio):

    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )
    cursor = conn.cursor()

    doctores=''

    query = f'''
        INSERT INTO notas (
            Cedula, inicio_time, tratar_time, notas_time, ip_address, doctores, mc_ea, analisisyplan, ExFis, celular, herramientaRadio
        ) VALUES ({cedula}, '{inicio_time}', '{tratar_time}', '{notas_time}', '{ip_address}', '{doctores}', '{mc_ea}', '{analisisyplan}', '{ExFis}', '{celular}', '{herramientaRadio}')
        '''

    # Ejecutar la consulta de inserción
    # cursor.execute(query, fila_ejemplo)
    cursor.execute(query)

    # Confirmar la transacción
    conn.commit()

    # Cerrar el cursor y la conexión
    cursor.close()
    conn.close()


import psycopg2
import datetime

def guardarPacientePostgres(cedula, edad, genero, altura, peso, imc, tfg, creatinina, hba1c, meta_hba1c,
            medicamento, antecedente, otros_medicamentos, otros_antecedentes, tolera_metform,
            hipos, glicemia, ultGlicada, ultCreatinina, tolera_aGLP1, cuantosADO,
            subGrupoMedicamento, timeInicio,funcionalidad,microalbuminuria,ult_microalbuminuria,credenciales,correo):

    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )


    # Crear un cursor
    cursor = conn.cursor()


    # Definir la consulta de inserción
    query = f"""
        INSERT INTO paciente (
            cedula, edad, genero, altura, peso, imc, tfg, creatinina, hba1c, meta_hba1c,
            medicamento, antecedente, otros_medicamentos, otros_antecedentes, tolera_metform,
            hipos, glicemia, ultGlicada, ultCreatinina, tolera_aGLP1, cuantosADO,
            subGrupoMedicamento, timeInicio,funcionalidad,microalbuminuria,ult_microalbuminuria,correo
        )
        VALUES (
        {cedula}, {edad}, '{genero}', {altura}, {peso}, {imc}, {tfg}, {creatinina}, {hba1c}, {meta_hba1c},
        '{medicamento}', '{antecedente}', '{otros_medicamentos}', '{otros_antecedentes}', '{tolera_metform}',
        '{hipos}', {glicemia}, {ultGlicada}, {ultCreatinina}, '{tolera_aGLP1}', '{cuantosADO}',
        '{subGrupoMedicamento}', '{timeInicio}','{funcionalidad}','{microalbuminuria}','{ult_microalbuminuria}','{correo}'
        )
        """


    # Ejecutar la consulta de inserción
    # cursor.execute(query, fila_ejemplo)
    cursor.execute(query)

    # Confirmar la transacción
    conn.commit()

    # Cerrar el cursor y la conexión
    cursor.close()
    conn.close()

def paciente_num_visitas(credenciales,cedula):

    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    cursor = conn.cursor()

    # Ejecutar la consulta SQL
    cursor.execute("SELECT COUNT(*) FROM paciente WHERE cedula = %s",
                   (cedula,))

    # Fetch the result
    result = cursor.fetchall()

    # Retornar el valor del conteo
    return result[0][0] if result else 0

# cred= credenciales("admin")
# valor=paciente_num_visitas(cred,'1212')
# print(valor)



def datosinstitucionBDs(credenciales):

    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    cursor = conn.cursor()

    cursor.execute("select * from paciente left join evaluaciones e on paciente.id = e.id where e.tipo = 'Zalida'")

    # Fetch the result
    queryData = cursor.fetchall()

    return queryData

def datossalidaconsultaBDs(credenciales):

    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    cursor = conn.cursor()

    cursor.execute("SELECT p.*,e.*, 'Salida Consulta' AS Clasificacion,'Unica' AS Seguimiento FROM paciente p "
                   "LEFT JOIN public.evaluaciones e ON p.id = e.id LEFT JOIN public.nuevos_registros n ON n.cedula = p.cedula and n.timeinicio=p.timeinicio "
                   "WHERE e.tipo = 'Zalida' AND e.evaluacion LIKE '%Iniciar%' "
                   "And n.procesado=false;")

    # Fetch the result

    queryData = cursor.fetchall()

    return queryData


def update_processed_status(credenciales,cedula, timeInicio):
    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE nuevos_registros
        SET procesado = TRUE
        WHERE Cedula = %s AND timeInicio = %s;
    """, (cedula, timeInicio))
    conn.commit()

def update_seguimientos(credenciales,cedula, timeInicio):
    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE nuevos_seguimientos
        SET procesado = TRUE
        WHERE Cedula = %s AND timeInicio = %s;
    """, (cedula, timeInicio))
    conn.commit()

def serieTiempohba1c(credenciales,cedula):

    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    cursor = conn.cursor()

    cursor.execute("SELECT hba1c, timeinicio FROM paciente "
                   "WHERE cedula = %s"
                   "ORDER BY ID;",
                   (cedula,))

    # Fetch the result
    result = cursor.fetchall()

    # Convert the result into a list of dictionaries
    data = [dict(zip([desc[0] for desc in cursor.description], row)) for row in result]

    # Convert the data to JSON
    json_data = json.dumps(data)

    # Convert the result into a DataFrame
    # df = pd.DataFrame(result, columns=[desc[0] for desc in cursor.description])

        # Close the cursor and the database connection
    cursor.close()
    conn.close()

    return json_data

def guardarTrello(credenciales, card_id, card_name, card_desc, card_date):

    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )

    cursor = conn.cursor()

    query = """
        INSERT INTO trello_cards (card_id, name, description, date_created)
        VALUES (?, ?, ?, ?)
    """
    cursor.execute(query, (card_id, card_name, card_desc, card_date))

    conn.commit()
    # Cerrar el cursor y la conexión
    conn.close()

def borrar_pruebas(credenciales,identif):
    # Establecer la conexión
    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )
    cursor = conn.cursor()

    cursor.execute("DELETE FROM evaluaciones WHERE ID IN (SELECT ID FROM paciente WHERE cedula = %s);"
             ,(identif,))
    # query = "DELETE FROM evaluaciones WHERE ID IN (SELECT ID FROM paciente WHERE timeinicio < '2024-08-23');"

    cursor.execute("DELETE FROM paciente WHERE cedula = %s;"
            , (identif,))

    cursor.execute("DELETE FROM nuevos_seguimientos WHERE cedula = %s;"
            , (identif,))

    conn.commit()
    # Cerrar el cursor y la conexión
    conn.close()
# Borra con la cedula
# cred= credenciales("admin")
# borrar_pruebas(cred,'1213')



def borrar_pruebasIDs(credenciales, identif):
    # Establish the connection
    conn = psycopg2.connect(
        database=credenciales["database"],
        user=credenciales["user"],
        password=credenciales["password"],
        host=credenciales["host"],
        port=credenciales["port"]
    )
    cursor = conn.cursor()

    try:
        # Delete from dependent tables first
        cursor.execute("DELETE FROM evaluaciones WHERE id = %s;", (identif,))
        cursor.execute("DELETE FROM nuevos_seguimientos WHERE id = %s;", (identif,))

        # Delete from the main table
        cursor.execute("DELETE FROM paciente WHERE id = %s;", (identif,))

        # Commit the transaction
        conn.commit()
    except Exception as e:
        print("Error:", e)
        conn.rollback()
    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()


# Execute the deletion
# cred = credenciales("admin")
# borrar_pruebasIDs(cred, '482')

