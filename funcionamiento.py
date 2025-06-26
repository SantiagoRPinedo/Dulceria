import json
import Validaciones
import baseDatos as baseDatos
import functools
from flask import(
    Blueprint,flash, g, jsonify, render_template, request, url_for, session,Response,redirect
)
import oracledb
import requests

bp = Blueprint('index',__name__,url_prefix='/')
conexion = baseDatos.JoinDulceria("dulceria", "123")
vendido = ""

@bp.route('/', methods =['GET','POST'])
def index():
    usuario = ""
    passw=""
    if request.method == 'POST':
        usuario = request.form['usuario']
        passw   =request.form['contrasena']
    
    conexion = baseDatos.JoinDulceria(usuario, passw)
    if (conexion):
        return(redirect('/panel'))
    else:
        print("No se pudo conectar")
    return render_template("index.html")
    


@bp.route('/panel', methods=['GET','POST'])
def panel():
    cursor = conexion.cursor()
    consultad = baseDatos.ejecuta_select("""select * from dulces""", cursor)
    consdeu = baseDatos.ejecuta_select("""SELECT d.id_deuda, c.cliente_obj.nombre AS cliente, d.monto, d.fecha_deuda, d.pagada
        FROM deudas d
        JOIN clientes c ON d.cliente_id = c.id_cliente""", cursor)
    consVenD= baseDatos.ejecuta_select("""select * from ventas_diarias""",cursor)
    clientes = baseDatos.ejecuta_select("""
        SELECT c.cliente_obj.nombre,c.cliente_obj.deudat,c.cliente_obj.telefono
        FROM clientes c""",cursor)

    if (consVenD == []):
        actualiza = baseDatos.ejecuta_insert("""
            INSERT INTO ventas_diarias (fecha_venta,cliente, nombre, cantidad_vendida, total_vendido)
                SELECT
                TRUNC(ventas.fecha_venta),
                ventas.cliente,
                productos.nombre,
                SUM(detalle_venta.cantidad) AS cantidad_vendida,
                SUM(detalle_venta.precio) AS total_vendido
                FROM ventas
                JOIN detalle_venta ON ventas.id_venta = detalle_venta.id_venta
                JOIN productos ON detalle_venta.id_producto = productos.id_producto
                where ventas.fecha_venta = TRUNC(SYSDATE)
                GROUP BY ventas.fecha_venta, productos.nombre,ventas.cliente
                ORDER BY ventas.cliente
        """,cursor)
    else:
        consVenD= baseDatos.ejecuta_select("""select * from ventas_diarias""",cursor)

    if request.method == 'POST':
        sql = "obtener_saldo_deudas"
        r= baseDatos.ejecuta_procedimiento(sql,cursor)
        return redirect("/panel")
    return render_template('panelc.html', consultad=consultad, consdeu = consdeu, consVenD=consVenD, clientes=clientes)

import oracledb

@bp.route('/productos', methods=['GET', 'POST'])
def productos():
    # Establecer la conexión con la base de datos
    cursor = conexion.cursor()

    # Consulta para obtener los productos estrella
    consProdE = baseDatos.ejecuta_select("""select * from productos_estrella""", cursor)
    
    if consProdE == []:
        # Consulta para actualizar los productos estrella
        actualiza = baseDatos.ejecuta_insert("""
            INSERT INTO productos_estrella (nombre, cantidad_vendida, total_vendido)
            SELECT 
                nombre,
                SUM(cantidad) AS cantidad_vendida,
                SUM(precio) AS total_vendido
            FROM (
                SELECT 
                    productos.nombre,
                    detalle_venta.cantidad,
                    detalle_venta.precio
                FROM ventas
                JOIN detalle_venta ON ventas.id_venta = detalle_venta.id_venta
                JOIN productos ON detalle_venta.id_producto = productos.id_producto
            )
            GROUP BY nombre
            ORDER BY cantidad_vendida DESC
            FETCH FIRST 3 ROWS ONLY
        """, cursor)
        print(actualiza)
    else:
        print("Ya hay estrellas")
    if request.method == 'POST':
        dulce = request.form['dulce']
        costo = request.form['costo']
        cantidad = request.form['cantidad']

        costov = Validaciones.validar_float(costo)
        if (costov != 1):
            flash(costov + " El Costo" + costo)

        cantidadv = Validaciones.validar_int(cantidad)
        if (cantidadv != 1):
            flash(cantidadv + " La cantidad " + cantidad)

        
        if(cantidadv == 1 and costov == 1 ):
            # Realizar el INSERT con el valor obtenido de la secuencia
            sql = """
                DECLARE
                v_id_producto NUMBER;
                BEGIN
                pkg_secuencias.nextval_seq_id_producto;
                SELECT seq_id_producto.CURRVAL INTO v_id_producto FROM DUAL;
            
                INSERT INTO productos (id_producto, nombre, precio, cantidad)
                VALUES (v_id_producto, :1, :2, :3);
                END;
            """
            params = [dulce, costo, cantidad]
            cursor.execute(sql, params)
            conexion.commit()

            flash("Producto agregado correctamente")
    # Consulta para obtener la lista de productos
    consulta = baseDatos.ejecuta_select("""select * from dulces""", cursor)

    # Cerrar el cursor y la conexión con la base de datos
    cursor.close()

    return render_template('producto.html', consulta=consulta, consProdE=consProdE)



@bp.route('/ventas', methods=['GET','POST'])
def ventas():
    venta=1
    cursor = conexion.cursor()
    consulta = baseDatos.ejecuta_select("""select id_venta, fecha_venta, cliente, total from ventas""", cursor)
    consultap = baseDatos.ejecuta_select("""select nombre, id_producto, precio  from dulces""", cursor)
    clientes = baseDatos.ejecuta_select("""
        SELECT c.id_cliente, c.cliente_obj.nombre AS nombre_cliente
        FROM clientes c""",cursor)
    mensaje = ""
    total=""
    global vendido 
    if request.method == 'POST':
        if (request.form.get('rventa')):
            total = request.form['total']
            cliente = request.form['cliente']

            si = Validaciones.validar_float(total)

            if (si == 1):
                sql = """INSERT INTO ventas (id_venta, fecha_venta, total, cliente)
                VALUES (seq_id_venta.NEXTVAL,TO_DATE(TO_CHAR(SYSDATE, 'dd-mm-yyyy'), 'dd-mm-yyyy'), """ +total+ """, '""" +cliente+"""')
                """
                mensaje = baseDatos.ejecuta_insert(sql, cursor)
                print(mensaje)
                conexion.commit()
                return (redirect("/ventas"))
            if (si != 1): flash(si)
        elif (request.form.get('rdetalle')):
            id_venta = request.form.get("ventaD")
            producto = request.form.get("producto")
            cantidad =  request.form['cantidad']
            precio = request.form['precio']
            
            siC=Validaciones.validar_int(cantidad)

            if (siC):
                sql = """INSERT INTO detalle_venta (id_detalle,id_venta, id_producto, cantidad, precio)
                VALUES (seq_id_detalle.NEXTVAL,"""+id_venta+""", """ +producto+ """, """ +cantidad+""","""+precio+""")
                """
                print("AAAAAAAAAAAAAAAAA" + sql)

                mensaje = baseDatos.ejecuta_insert(sql, cursor)
                print("registrar detalle" +mensaje)
                conexion.commit()
                return (redirect("/ventas"))
            if (siC != 1): flash(siC)
        elif (request.form.get('presionado')):
            venta = request.form['presionado']
            sql = """select * from detalle_venta_con_clientes_y_productos
            WHERE id_venta="""+venta+""""""
            mensaje =  baseDatos.ejecuta_select(sql, cursor)
            sql = """SELECT SUM(precio) AS total_vendido
                FROM detalle_venta_con_clientes_y_productos
                WHERE id_venta="""+venta+""""""
            total = baseDatos.ejecuta_select(sql, cursor)
            total = total[0]
        elif (request.form.get('date-button')):
            fecha1= request.form['date-input1']
            fecha2= request.form['date-input2']
            vendido = baseDatos.ejecuta_funcion(cursor,fecha1,fecha2)
            vendido = vendido [0]
    return(render_template('ventas.html', consulta=consulta, consultap=consultap, mensaje=mensaje,total=total,clientes=clientes ))

@bp.route('/deudas', methods=['GET','POST'])
def deudas():
    cursor = conexion.cursor()
    consdeu = baseDatos.ejecuta_select("""SELECT d.id_deuda, c.cliente_obj.nombre AS cliente, d.monto, d.fecha_deuda, d.pagada
            FROM deudas d
            JOIN clientes c ON d.cliente_id = c.id_cliente""", cursor)
    clientes = baseDatos.ejecuta_select("""
        SELECT c.id_cliente, c.cliente_obj.nombre AS nombre_cliente
        FROM clientes c""",cursor)
    
    if request.method == 'POST':#para cuando se agregue nuevo producto
        id = request.form['id']
        monto  =request.form['monto']

        siM= Validaciones.validar_float(monto)
        
        cursor = conexion.cursor()
        if (siM==1):
            sql = """
                INSERT INTO deudas(id_deuda, cliente_id, monto, fecha_deuda, pagada)
                VALUES (seq_id_deuda.NEXTVAL, """+id+""", """+monto+""", SYSDATE, 'N')
            """
            
            mensaje = baseDatos.ejecuta_insert(sql, cursor)
            conexion.commit()
            flash(mensaje)
        
        flash(siM)
    return(render_template('deudas.html', consdeu=consdeu,clientes = clientes))

@bp.route('/provedores', methods=['GET','POST'])
def provedores():
    cursor = conexion.cursor()
    cons = baseDatos.ejecuta_select("""select * FROM proveedores_externos""", cursor)
    
    return(render_template('provedores.html', cons=cons))


@bp.route('/modificar', methods=['POST'])
def modificar_registro():
        id = request.form['id']
        cursor = conexion.cursor()
        sql = """UPDATE deudas
        SET pagada='S'
        WHERE id_deuda = """+id+"""
        """
        mensaje = baseDatos.ejecuta_update(sql, cursor)
        flash(mensaje)
        conexion.commit()
        return redirect('/deudas')
        

@bp.route('/busqueda', methods=['GET','POST'])
def busqueda():
    busco=""
    busco = request.args.get('buscado')
    cursor = conexion.cursor()
    if (busco != ""):
        consulta ="""SELECT d.cliente, SUM(d.monto) AS total_deuda, NULL AS precio, NULL AS cantidad, d.pagada, 'deuda' AS tipo
                FROM deudas d
                WHERE UPPER(d.cliente) LIKE UPPER('%"""+busco+"""%')
                GROUP BY d.cliente, d.pagada
                UNION
                SELECT p.nombre, NULL AS total_deuda, p.precio, p.cantidad, NULL AS pagada, 'producto' AS tipo
                FROM productos p
                WHERE UPPER(p.nombre) LIKE UPPER('%"""+busco+"""%')"""
        consulta = baseDatos.ejecuta_select(consulta, cursor)
        if (consulta==[]):
            flash('No se encontraron resultados para la búsqueda "{}"'.format(busco))
            return redirect(request.referrer)
        return (render_template('busqueda.html',consulta = consulta))
    else:
        return redirect(request.referrer)
    
@bp.route('/ruta_al_archivo_html_del_calendario')
def mostrar_calendario():
    global vendido
    return render_template('calendario.html', vendido=vendido)

