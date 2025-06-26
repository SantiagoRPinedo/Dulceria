import oracledb
oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_21_9")

def JoinDulceria (usuario, cont):
    try:
        conexion = oracledb.connect(user= usuario, password=cont, dsn= 'localhost:1521/XEPDB1') 
    except Exception as error:
        print("No se pudo conectar compita :C" )
    else:
        print("Conexion LISTA!!!")
        return conexion
            


def ejecuta_select(sql,cursor):
    consulta = ""
    try:
        cursor.execute(sql)
        ejecucion = cursor.fetchall()
        return (ejecucion)
    except:
        print ("Verifica tu entrada bro unu")

def ejecuta_insert(sql,cursor):
    try:
        cursor.execute(sql)
        return ("Registro agregado correctamente")
    except:
        return ("Algo hiciste mal pero no se agrego nada la base de datos :c")

def ejecuta_delete(sql,cursor):
    try:
        cursor.execute(sql)
        return ("Se elimino el registro")
    except:
        return ("No se que paso la neta")

def ejecuta_update(sql,cursor):
    try:
        cursor.execute(sql)
        return ("Se modifico el registro")
    except:
        return ("No se modifico nada nadita")
    
def ejecuta_funcion(cursor, fechaI, fechaF):
    
    sql = """SELECT CalcularGanancias(TO_DATE('"""+ fechaI +"""', 'MM-DD-YYYY'),
        TO_DATE('"""+ fechaF +"""', 'MM-DD-YYYY')) AS ganancias
        FROM dual"""
    print(sql)
    try:
        cursor.execute(sql)
        ejecucion = cursor.fetchone()
        return (ejecucion)
    except:
        return ("Algo salio mal no hubo ventas o que?")
    
def ejecuta_procedimiento(proc, cursor):
    try:
        cursor.callproc(proc)
        ejecucion = "Deudas actualizadas"
        return (ejecucion)
    except:
        return ("nop")