from flask import Blueprint,render_template, request,flash
from flask_login import login_required, current_user
from . import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy import exc
from werkzeug.security import generate_password_hash, check_password_hash
import json
import datetime
from datetime import date
import re

views = Blueprint('views', __name__)

@views.route('/',methods=['GET','POST'])
def home():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        products = connection.execute(text("EXEC CRUD_producto @opcion=6,@nombre=null, @descripcion=null, @categoria_ID = null, @tiene_impuesto =null, @minimo =null, @maximo =null,@fecha_produccion=null, @fecha_expiracion=null, @en_descuento=null, @precio=null, @estado_ID=null, @sucursal_ID=null,@cantidad=null,@producto_ID=null,@proveedor_ID=null,@porcentaje_descuento=null")).fetchall()

        return render_template("home.html",products=products,comprado=False)

@views.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('email')
        password = request.form.get('password')
        tipo_usuario = request.form.get('clientOrEmployee')

        usuario = None

        sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
        if tipo_usuario == 'Cliente':
            with sqlcon.connect() as connection:
                try:
                    usuario = connection.execute(text("EXEC CRUD_cliente @opcion=6,@cedula=null,@nombre=null,@apellido=null,@correo=:correo,@password='',@telefono=null,@domicilio=null,@direccion=null,@pais=null,@estado_ID=null"),correo=correo).fetchall()
                    test_password=usuario[0][8]
                    if (check_password_hash(test_password, password))==True:
                        flash('Se ha iniciado sesión correctamente!', category='success')
                        products = connection.execute(text("EXEC CRUD_producto @opcion=6,@nombre=null, @descripcion=null, @categoria_ID = null, @tiene_impuesto =null, @minimo =null, @maximo =null,@fecha_produccion=null, @fecha_expiracion=null, @en_descuento=null, @precio=null, @estado_ID=null, @sucursal_ID=null,@cantidad=null,@producto_ID=null,@proveedor_ID=null,@porcentaje_descuento=null")).fetchall()
                        return render_template("home.html",usuario=usuario,products=products,comprado=False)
                    else:
                        flash('Password incorrecto, intente de nuevo', category='error')
                        return render_template("login.html")
                except exc.SQLAlchemyError as e:
                    print(type(e))
                    flash('Usuario no encontrado', category='error')
                    return render_template("login.html")

        elif tipo_usuario == 'Empleado':
            with sqlcon.connect() as connection:
                try:
                    usuario = connection.execute(text("EXEC CRUD_Empleado @opcion=6,@tipo_consulta=null,@cedula=null,@nombre=null,@apellido=null,@correo=:correo, @telefono=null,@fecha_contratacion=null,@sucursal_ID=null,@pais=null,@puesto=null,@foto_filename=null,@administrador =null,@salario_base=null,@estado_ID=null,@password=null,@fecha2=null"),correo=correo).fetchall()
                    test_password=usuario[0][4]
                    print(usuario)
                    if (check_password_hash(test_password, password))==True:
                        flash('Se ha iniciado sesión correctamente!', category='success')
                        products = connection.execute(text("EXEC CRUD_producto @opcion=6,@nombre=null, @descripcion=null, @categoria_ID = null, @tiene_impuesto =null, @minimo =null, @maximo =null,@fecha_produccion=null, @fecha_expiracion=null, @en_descuento=null, @precio=null, @estado_ID=null, @sucursal_ID=null,@cantidad=null,@producto_ID=null,@proveedor_ID=null,@porcentaje_descuento=null")).fetchall()
                        return render_template("home.html",usuario=usuario,products=products,comprado=False,es_empleado=True)
                    else:
                        flash('Password incorrecto, intente de nuevo', category='error')
                        return render_template("login.html")
                except exc.SQLAlchemyError as e:
                    print(e)
                    flash('Empleado no encontrado', category='error')
                    return render_template("login.html")

    return render_template("login.html")

@views.route('/logout', methods=['GET','POST'])
def logout():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        products = connection.execute(text("EXEC CRUD_producto @opcion=6,@nombre=null, @descripcion=null, @categoria_ID = null, @tiene_impuesto =null, @minimo =null, @maximo =null,@fecha_produccion=null, @fecha_expiracion=null, @en_descuento=null, @precio=null, @estado_ID=null, @sucursal_ID=null,@cantidad=null,@producto_ID=null,@proveedor_ID=null,@porcentaje_descuento=null")).fetchall()

        return render_template("home.html",products=products,comprado=False)

@views.route('/micuenta', methods=['GET','POST'])
def micuenta():
    return render_template("micuenta.html")

@views.route('/signup', methods=['GET','POST'])
def signup():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    domicilio = request.args.get('ubicacion', default = '*', type = str)

    if request.method == 'POST':
        cedula = int(request.form.get('cedula'))
        correo = request.form.get('email')
        nombre = request.form.get('firstName')
        apellido = request.form.get('lastName')
        telefono = int(request.form.get('telefono'))
        direccion = request.form.get('direccion')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        pais = request.form.get('pais')
        print(request.form)
        if (password1 != password2):
            flash("Las passwords deben ser iguales.",category='error')
        elif nombre == None or nombre == "" or nombre == " ":
            flash("El nombre no puede estar vacío.",category='error')
        elif(bool(re.match('[a-zA-Z\s]+$', nombre))==False):
            flash("Solo puede usar caracteres de A-Z.",category='error')
        elif apellido == None or apellido == "" or apellido == " ":
            flash("El apellido no puede estar vacío.",category='error')
        elif(bool(re.match('[a-zA-Z\s]+$', apellido))==False):
            flash("Solo puede usar caracteres de A-Z.",category='error')
        elif direccion == None or direccion == "" or direccion == " ":
            flash("El nombre no puede estar vacío.",category='error')
        elif(bool(re.match('[0-9a-zA-Z\s]+$', direccion))==False):
            flash("Solo puede usar caracteres de A-Z y números.",category='error')
        else:
            password = generate_password_hash(password1)
            print(password)
            try:
                with sqlcon.begin() as connection:
                    connection.execution_options(isolation_level="AUTOCOMMIT")
                    connection.execute(text("DECLARE @punto geography;"+"SET @punto = geography::STPointFromText('POINT("+domicilio+")', 4326);"+"EXEC CRUD_cliente @opcion=1,@cedula=:cedula,@nombre=:nombre,@apellido=:apellido,@correo=:correo,@password=:password,@telefono=:telefono,@domicilio=@punto,@direccion=:direccion,@pais=:pais,@estado_ID=1"),cedula=cedula,nombre=nombre,apellido=apellido,correo=correo,password=password,telefono=telefono,direccion=direccion,pais=pais)
                    flash('Se ha creado una cuenta correctamente!', category='success')
                    products = connection.execute(text("EXEC CRUD_producto @opcion=6,@nombre=null, @descripcion=null, @categoria_ID = null, @tiene_impuesto =null, @minimo =null, @maximo =null,@fecha_produccion=null, @fecha_expiracion=null, @en_descuento=null, @precio=null, @estado_ID=null, @sucursal_ID=null,@cantidad=null,@producto_ID=null,@proveedor_ID=null,@porcentaje_descuento=null")).fetchall()
                    return render_template("home.html",products=products,comprado=False)
            except exc.SQLAlchemyError as e:
                print(e.__cause__)
                flash("El cliente ya está registrado en la base de datos.", category='error')
                return render_template("signup.html")
            

    return render_template("signup.html")

@views.route('/producto',methods=['GET','POST'])
def product():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        producto_ID = request.args.get('producto_ID', default = 0, type = int)
        products = connection.execute(text("EXEC CRUD_producto @opcion=7,@nombre=null, @descripcion=null, @categoria_ID = null, @tiene_impuesto =null, @minimo =null, @maximo =null,@fecha_produccion=null, @fecha_expiracion=null, @en_descuento=null, @precio=null, @estado_ID=null, @sucursal_ID=null,@cantidad=null,@producto_ID=:producto_ID,@proveedor_ID=null,@porcentaje_descuento=null"),producto_ID=producto_ID).fetchall()
        products_images = connection.execute(text("select producto_ID,foto_ID,filename,thumbnail from Productos_Fotos where producto_ID=:producto_ID"),producto_ID=producto_ID)

        return render_template("producto.html",products=products,products_images=products_images)

@views.route('/checkout',methods=['GET','POST'])
def checkout():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    ubicacion = request.args.get('ubicacion', default = '*', type = str)
    if request.method == 'POST':
        print(request.form)
        pais = request.form.get('pais')
        payment_method = request.form.get('paymentMethod')
        metodo_pago_ID = 4
        tipo_entrega = request.form.get('tipo_entrega')
        tipo_entrega_ID = 2
        productos = json.loads(request.form.get('productos'))
        cedula = int(request.form.get('usuario'))
        sucursal_ID = int(request.form.get('sucursal_ID'))
        tipo_compra_ID = 1

        if pais == 'Costa Rica':
            tipo_compra_ID = 1
            if tipo_entrega == 'Domicilio':
                tipo_entrega_ID = 1
            else:
                tipo_entrega_ID = 2
            if payment_method == 'Efectivo':
                metodo_pago_ID = 4
            elif payment_method == 'Cheque':
                metodo_pago_ID = 3
            elif payment_method == 'Tarjeta de débito':
                metodo_pago_ID = 5
            elif payment_method == 'Tarjeta de crédito':
                metodo_pago_ID = 2
            elif payment_method == 'Criptomonedas':
                metodo_pago_ID = 1
            elif payment_method == 'Paypal':
                metodo_pago_ID = 6
        elif pais == 'Guatemala':
            tipo_compra_ID = 3000
            if tipo_entrega == 'Domicilio':
                tipo_entrega_ID = 3000
            else:
                tipo_entrega_ID = 3001
            if payment_method == 'Efectivo':
                metodo_pago_ID = 3000
            elif payment_method == 'Cheque':
                metodo_pago_ID = 3001
            elif payment_method == 'Tarjeta de débito':
                metodo_pago_ID = 3002
            elif payment_method == 'Tarjeta de crédito':
                metodo_pago_ID = 3003
            elif payment_method == 'Criptomonedas':
                metodo_pago_ID = 3004
            elif payment_method == 'Paypal':
                metodo_pago_ID = 3005
        elif pais == 'Panama':
            tipo_compra_ID = 4000
            if tipo_entrega == 'Domicilio':
                tipo_entrega_ID = 4000
            else:
                tipo_entrega_ID = 4001
            if payment_method == 'Efectivo':
                metodo_pago_ID = 4000
            elif payment_method == 'Cheque':
                metodo_pago_ID = 4001
            elif payment_method == 'Tarjeta de débito':
                metodo_pago_ID = 4002
            elif payment_method == 'Tarjeta de crédito':
                metodo_pago_ID = 4003
            elif payment_method == 'Criptomonedas':
                metodo_pago_ID = 4004
            elif payment_method == 'Paypal':
                metodo_pago_ID = 4005

        fecha = datetime.datetime.now()

        print(pais)
        print(metodo_pago_ID)
        print(tipo_entrega_ID)
        print(tipo_compra_ID)
        print(cedula)
        print(sucursal_ID)

        with sqlcon.begin() as connection:
            try:
                connection.execution_options(isolation_level="AUTOCOMMIT")
                query2 = text("DECLARE @punto geography;"+"SET @punto = geography::STPointFromText('POINT("+ubicacion+")', 4326);"+"EXEC comprar_producto @opcion =1,@producto_ID=:producto_ID,@cliente_ID=:cedula,@facturador_ID =null,@sucursal_ID=:sucursal_ID,@tipo_compra_ID=:tipo_compra_ID,@tipo_entrega_ID=:tipo_entrega_ID,@metodo_pago_ID=:metodo_pago_ID,@fecha=:fecha,@descripcion=:descripcion,@cantidad=:cantidad")
                for producto in productos:
                    producto_ID = producto['producto_ID']
                    cantidad = producto['cantidad']
                    print(producto_ID)
                    connection.execute(query2,producto_ID=producto_ID,cedula=cedula,sucursal_ID=sucursal_ID,tipo_compra_ID=tipo_compra_ID,tipo_entrega_ID=tipo_entrega_ID,metodo_pago_ID=metodo_pago_ID,fecha=fecha,descripcion="Facturación de compra de productos",cantidad=cantidad)
                    print("Producto ordenado")

                flash('Se ha ordenado los productos correctamente!', category='success')

                query = text("DECLARE @punto geography;"+"SET @punto = geography::STPointFromText('POINT("+ubicacion+")', 4326);"+"EXEC consultar_supermercado @opcion =7,@localizacion =@punto,@sucursal_ID =null,@pais_ID =null,@horario_inicio =null,@horario_fin=null")
                products = connection.execute(text("EXEC CRUD_producto @opcion=6,@nombre=null, @descripcion=null, @categoria_ID = null, @tiene_impuesto =null, @minimo =null, @maximo =null,@fecha_produccion=null, @fecha_expiracion=null, @en_descuento=null, @precio=null, @estado_ID=null, @sucursal_ID=null,@cantidad=null,@producto_ID=null,@proveedor_ID=null,@porcentaje_descuento=null")).fetchall()
                return render_template("home.html",products=products,comprado=True)
            except exc.SQLAlchemyError as e:
                print(e)
                flash(e, category='error')
                query = text("DECLARE @punto geography;"+"SET @punto = geography::STPointFromText('POINT("+ubicacion+")', 4326);"+"EXEC consultar_supermercado @opcion =7,@localizacion =@punto,@sucursal_ID =null,@pais_ID =null,@horario_inicio =null,@horario_fin=null")
                sucursales = connection.execute(query).fetchall()
                return render_template("checkout.html",ubicacion=ubicacion,sucursales=sucursales)
            
    else:
        with sqlcon.connect() as connection:
            try:
                query = text("DECLARE @punto geography;"+"SET @punto = geography::STPointFromText('POINT("+ubicacion+")', 4326);"+"EXEC consultar_supermercado @opcion =7,@localizacion =@punto,@sucursal_ID =null,@pais_ID =null,@horario_inicio =null,@horario_fin=null")
                sucursales = connection.execute(query).fetchall()
                return render_template("checkout.html",ubicacion=ubicacion,sucursales=sucursales)
            except exc.SQLAlchemyError as e:
                print(e.__cause__)
                flash('Error de memoria, intente de nuevo.', category='error')
                query = text("DECLARE @punto geography;"+"SET @punto = geography::STPointFromText('POINT("+ubicacion+")', 4326);"+"EXEC consultar_supermercado @opcion =7,@localizacion =@punto,@sucursal_ID =null,@pais_ID =null,@horario_inicio =null,@horario_fin=null")
                sucursales = connection.execute(query).fetchall()
                return render_template("checkout.html",ubicacion=ubicacion,sucursales=sucursales)

@views.route('/busqueda_producto',methods=['GET','POST'])
def busqueda_producto():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    busqueda = request.args.get('busqueda', default = '*', type = str)
    busqueda=busqueda.upper()
    if (len(busqueda)<3):
        return render_template("busqueda_producto.html",products=None,busqueda=busqueda)
    else:
        with sqlcon.connect() as connection:
            products = connection.execute(text("EXEC CRUD_producto @opcion=6,@nombre=null, @descripcion=null, @categoria_ID = null, @tiene_impuesto =null, @minimo =null, @maximo =null,@fecha_produccion=null, @fecha_expiracion=null, @en_descuento=null, @precio=null, @estado_ID=null, @sucursal_ID=null,@cantidad=null,@producto_ID=null,@proveedor_ID=null,@porcentaje_descuento=null")).fetchall()
            return render_template("busqueda_producto.html",products=products,busqueda=busqueda)

@views.route('/informacion_sucursales',methods=['GET','POST'])
def informacion_sucursales():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    ubicacion = request.args.get('ubicacion', default = '*', type = str)
    coordenadas_mapa = ubicacion.split()
    longitud = coordenadas_mapa[0]
    latitud = coordenadas_mapa[1]
    print(coordenadas_mapa)
    print(longitud)
    print(latitud)
    with sqlcon.connect() as connection:

        try:
            query = text("DECLARE @punto geography;"+"SET @punto = geography::STPointFromText('POINT("+ubicacion+")', 4326);"+"EXEC consultar_supermercado @opcion =8,@localizacion =@punto,@sucursal_ID =null,@pais_ID =null,@horario_inicio =null,@horario_fin=null")
            sucursales = connection.execute(query).fetchall()
            return render_template("informacion_sucursales.html",ubicacion=ubicacion,sucursales=sucursales,longitud=longitud,latitud=latitud)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo.', category='error')
            return render_template("informacion_sucursales.html")

@views.route('/mapa_sucursal',methods=['GET','POST'])
def mapa_sucursal():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    ubicacion = request.args.get('ubicacion', default = '*', type = str)
    coordenadas_mapa = ubicacion.split()
    longitud = coordenadas_mapa[0]
    latitud = coordenadas_mapa[1]
    nombre = request.args.get('nombre', default = '*', type = str)
    print(longitud)
    print(latitud)
    with sqlcon.connect() as connection:
        try:
            return render_template("mapa_sucursal.html",longitud=longitud,latitud=latitud,nombre=nombre)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo.', category='error')
            return render_template("mapa_sucursal.html")

@views.route('/categoria',methods=['GET','POST'])
def categoria():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    nombre_categoria = request.args.get('nombre_categoria', default = '*', type = str)
    with sqlcon.connect() as connection:
        products = connection.execute(text("EXEC poner_en_exhibidor @opcion =4,@producto_ID =null,@sucursal_ID =null,@nombre_categoria = :nombre_categoria"),nombre_categoria=nombre_categoria).fetchall()
        return render_template("categorias_producto.html",products=products)

@views.route('/proveedores',methods=['GET','POST'])
def proveedores():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        proveedores = connection.execute(text("EXEC consultar_proveedor @opcion=5,@producto_nombre=null,@proveedor_nombre=null,@localizacion=null,@pais=null,@ciudad=null")).fetchall()
        return render_template("proveedores.html",proveedores=proveedores)

@views.route('/busqueda_producto_proveedor',methods=['GET','POST'])
def busqueda_producto_proveedor():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    busqueda = request.args.get('busqueda', default = '*', type = str)
    busqueda=busqueda.upper()
    if (len(busqueda)<3):
        return render_template("busqueda_producto_proveedor.html",products=None,busqueda=busqueda)
    else:
        with sqlcon.connect() as connection:
            products = connection.execute(text("EXEC consultar_proveedor @opcion=6,@producto_nombre=null,@proveedor_nombre=null,@localizacion=null,@pais=null,@ciudad=null")).fetchall()
            return render_template("busqueda_producto_proveedor.html",products=products,busqueda=busqueda)

@views.route('/detalle_producto_proveedor',methods=['GET','POST'])
def detalle_producto_proveedor():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        producto_nombre = request.args.get('producto_nombre', default = '*', type = str)
        products = connection.execute(text("EXEC consultar_proveedor @opcion=1,@producto_nombre=:producto_nombre,@proveedor_nombre=null,@localizacion=null,@pais=null,@ciudad=null"),producto_nombre=producto_nombre).fetchall()
        products_images = connection.execute(text("select producto_ID,producto,foto_ID,filename,thumbnail from Proveedores_Productos_Fotos where producto=:producto_nombre and thumbnail=1"),producto_nombre=producto_nombre).fetchall()
        return render_template("detalle_producto_proveedor.html",products=products,products_images=products_images)

@views.route('/busqueda_nombre_proveedor',methods=['GET','POST'])
def busqueda_nombre_proveedor():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    busqueda = request.args.get('busqueda', default = '*', type = str)
    busqueda = busqueda.upper()
    print(busqueda)
    if (len(busqueda)<3):
        return render_template("busqueda_nombre_proveedor.html",proveedores=None,busqueda=busqueda)
    elif(bool(re.match('[a-zA-Z\s]+$', busqueda))==False):
        return render_template("productos_proveedor.html",products=None,busqueda=busqueda)
    else:
        with sqlcon.connect() as connection:
            proveedores = connection.execute(text("EXEC consultar_proveedor @opcion=5,@producto_nombre=null,@proveedor_nombre=null,@localizacion=null,@pais=null,@ciudad=null")).fetchall()
            return render_template("busqueda_nombre_proveedor.html",proveedores=proveedores,busqueda=busqueda)

@views.route('/busqueda_pais_proveedor',methods=['GET','POST'])
def busqueda_pais_proveedor():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    busqueda = request.args.get('busqueda', default = '*', type = str)
    busqueda = busqueda.upper()
    print(busqueda)
    if (len(busqueda)<3):
        return render_template("busqueda_pais_proveedor.html",proveedores=None,busqueda=busqueda)
    else:
        with sqlcon.connect() as connection:
            proveedores = connection.execute(text("EXEC consultar_proveedor @opcion=5,@producto_nombre=null,@proveedor_nombre=null,@localizacion=null,@pais=null,@ciudad=null")).fetchall()
            return render_template("busqueda_pais_proveedor.html",proveedores=proveedores,busqueda=busqueda)

@views.route('/busqueda_ciudad_proveedor',methods=['GET','POST'])
def busqueda_ciudad_proveedor():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    busqueda = request.args.get('busqueda', default = '*', type = str)
    busqueda = busqueda.upper()
    print(busqueda)
    if (len(busqueda)<3):
        return render_template("busqueda_ciudad_proveedor.html",proveedores=None,busqueda=busqueda)
    elif(bool(re.match('[a-zA-Z\s]+$', busqueda))==False):
        return render_template("productos_proveedor.html",products=None,busqueda=busqueda)
    else:
        with sqlcon.connect() as connection:
            proveedores = connection.execute(text("EXEC consultar_proveedor @opcion=7,@producto_nombre=null,@proveedor_nombre=null,@localizacion=null,@pais=null,@ciudad=:busqueda"),busqueda=busqueda).fetchall()
            return render_template("busqueda_ciudad_proveedor.html",proveedores=proveedores,busqueda=busqueda)

@views.route('/productos_proveedor',methods=['GET','POST'])
def productos_proveedor():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    busqueda = request.args.get('busqueda', default = '*', type = str)
    busqueda=busqueda.upper()
    print(busqueda)
    if (len(busqueda)<3):
        return render_template("productos_proveedor.html",products=None,busqueda=busqueda)
    elif(bool(re.match('[a-zA-Z\s]+$', busqueda))==False):
        return render_template("productos_proveedor.html",products=None,busqueda=busqueda)
    else:
        with sqlcon.connect() as connection:
            products = connection.execute(text("EXEC consultar_proveedor @opcion=6,@producto_nombre=null,@proveedor_nombre=null,@localizacion=null,@pais=null,@ciudad=null")).fetchall()
            print(products)
            return render_template("productos_proveedor.html",products=products,busqueda=busqueda)

@views.route('/todos_productos',methods=['GET','POST'])
def todos_productos():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        products = connection.execute(text("EXEC CRUD_producto @opcion=6,@nombre=null, @descripcion=null, @categoria_ID = null, @tiene_impuesto =null, @minimo =null, @maximo =null,@fecha_produccion=null, @fecha_expiracion=null, @en_descuento=null, @precio=null, @estado_ID=null, @sucursal_ID=null,@cantidad=null,@producto_ID=null,@proveedor_ID=null,@porcentaje_descuento=null")).fetchall()

        return render_template("todos_productos.html",products=products)

@views.route('/consultar_ganancias_netas',methods=['GET','POST'])
def consultar_ganancias_netas():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        ganancias_CR = connection.execute(text("EXEC informacion_ganancias @opcion=5,@fecha_inicio=null,@fecha_fin=null,@pais=null,@sucursal=null,@categoria=null,@moneda_nombre='colones'")).fetchall()
        ganancias_Guatemala = connection.execute(text("EXEC informacion_ganancias @opcion=5,@fecha_inicio=null,@fecha_fin=null,@pais=null,@sucursal=null,@categoria=null,@moneda_nombre='quetzales'")).fetchall()
        ganancias_Panama = connection.execute(text("EXEC informacion_ganancias @opcion=5,@fecha_inicio=null,@fecha_fin=null,@pais=null,@sucursal=null,@categoria=null,@moneda_nombre='balboas'")).fetchall()
        ganancias=[ganancias_CR,ganancias_Guatemala,ganancias_Panama]
        print(ganancias)
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(sucursales)
        return render_template("consultar_ganancias_netas.html",ganancias=ganancias,sucursales=sucursales)

@views.route('/consultar_bonos',methods=['GET','POST'])
def consultar_bonos():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        bonos = connection.execute(text("EXEC informacion_bonos_recibidos @opcion =5,@fecha_inicio=null,@fecha_fin=null,@empleado_ID =null,@pais=null,@sucursal=null")).fetchall()
        print(bonos)
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(sucursales)
        return render_template("consultar_bonos.html",bonos=bonos,sucursales=sucursales)

@views.route('/consultar_montos_recolectados',methods=['GET','POST'])
def consultar_montos_recolectados():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        montos_CR = connection.execute(text("EXEC consultar_montos_recolectados @opcion=6,@fecha_inicio='',@fecha_fin='',@sucursal=4,@cedula=118180815,@moneda_nombre='colones'")).fetchall()
        montos_Guatemala = connection.execute(text("EXEC consultar_montos_recolectados @opcion=6,@fecha_inicio='',@fecha_fin='',@sucursal=4,@cedula=118180815,@moneda_nombre='quetzales'")).fetchall()
        montos_Panama = connection.execute(text("EXEC consultar_montos_recolectados @opcion=6,@fecha_inicio='',@fecha_fin='',@sucursal=4,@cedula=118180815,@moneda_nombre='balboas'")).fetchall()
        montos = [montos_CR,montos_Guatemala,montos_Panama]
        print(montos)
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(sucursales)
        return render_template("consultar_montos_recolectados.html",montos=montos,sucursales=sucursales)

@views.route('/consultar_montos_recolectados_facturas',methods=['GET','POST'])
def consultar_montos_recolectados_facturas():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        montos = connection.execute(text("EXEC consultar_montos_recolectados @opcion=5,@fecha_inicio='',@fecha_fin='',@sucursal=4,@cedula=118180815,@moneda_nombre=null")).fetchall()
        print(montos)
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(sucursales)
        return render_template("consultar_montos_recolectados_facturas.html",montos=montos,sucursales=sucursales)

@views.route('/consultar_montos_recolectados_envios',methods=['GET','POST'])
def consultar_montos_recolectados_envios():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        montos_CR = connection.execute(text("EXEC consultar_montos_recolectados @opcion=4,@fecha_inicio='',@fecha_fin='',@sucursal=4,@cedula=118180815,@moneda_nombre='colones'")).fetchall()
        montos_Guatemala = connection.execute(text("EXEC consultar_montos_recolectados @opcion=4,@fecha_inicio='',@fecha_fin='',@sucursal=4,@cedula=118180815,@moneda_nombre='quetzales'")).fetchall()
        montos_Panama = connection.execute(text("EXEC consultar_montos_recolectados @opcion=4,@fecha_inicio='',@fecha_fin='',@sucursal=4,@cedula=118180815,@moneda_nombre='balboas'")).fetchall()
        montos = [montos_CR,montos_Guatemala,montos_Panama]
        print(montos)
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(sucursales)
        return render_template("consultar_montos_recolectados_envios.html",montos=montos,sucursales=sucursales)

@views.route('/consultar_montos_recolectados_sucursal',methods=['GET','POST'])
def consultar_montos_recolectados_sucursal():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    sucursal = request.args.get('sucursal', default = '*', type = str)
    print(sucursal)
    with sqlcon.connect() as connection:
        monedas = connection.execute(text("select moneda_nombre from Sucursales where nombre=:sucursal"),sucursal=sucursal).fetchall()
        moneda = monedas[0][0]
        print(moneda)
        montos = connection.execute(text("EXEC consultar_montos_recolectados @opcion=2,@fecha_inicio='',@fecha_fin='',@sucursal=:sucursal,@cedula=118180815,@moneda_nombre=:moneda"),sucursal=sucursal,moneda=moneda).fetchall()
        print(montos)
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(sucursales)
        return render_template("consultar_montos_recolectados_sucursal.html",montos=montos,sucursales=sucursales,moneda=moneda,sucursal=sucursal)
    
@views.route('/consultar_montos_recolectados_cliente',methods=['GET','POST'])
def consultar_montos_recolectados_cliente():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    cedula = request.args.get('cedula', default = '*', type = str)
    print(cedula)
    with sqlcon.connect() as connection:
        try:
            montos_CR = connection.execute(text("EXEC consultar_montos_recolectados @opcion=3,@fecha_inicio='',@fecha_fin='',@sucursal=null,@cedula=:cedula,@moneda_nombre='colones'"),cedula=cedula).fetchall()
            montos_Guatemala = connection.execute(text("EXEC consultar_montos_recolectados @opcion=3,@fecha_inicio='',@fecha_fin='',@sucursal=null,@cedula=:cedula,@moneda_nombre='quetzales'"),cedula=cedula).fetchall()
            montos_Panama = connection.execute(text("EXEC consultar_montos_recolectados @opcion=3,@fecha_inicio='',@fecha_fin='',@sucursal=null,@cedula=:cedula,@moneda_nombre='balboas'"),cedula=cedula).fetchall()
            montos = [montos_CR,montos_Guatemala,montos_Panama]
            print(montos)
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            print(sucursales)
            return render_template("consultar_montos_recolectados_cliente.html",montos=montos,sucursales=sucursales,cedula=cedula)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Por favor escriba un número de cédula válido.', category='error')
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            print(sucursales)
            return render_template("consultar_montos_recolectados_cliente.html",sucursales=sucursales,cedula=cedula)

@views.route('/consultar_montos_recolectados_fechas',methods=['GET','POST'])
def consultar_montos_recolectados_fechas():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    fecha1 = request.args.get('fecha1', default = '*', type = str)
    fecha2 = request.args.get('fecha2', default = '*', type = str)
    print(fecha1)
    print(fecha2)
    with sqlcon.connect() as connection:
        try:
            montos_CR = connection.execute(text("EXEC consultar_montos_recolectados @opcion=1,@fecha_inicio=:fecha1,@fecha_fin=:fecha2,@sucursal=null,@cedula=null,@moneda_nombre='colones'"),fecha1=fecha1,fecha2=fecha2).fetchall()
            montos_Guatemala = connection.execute(text("EXEC consultar_montos_recolectados @opcion=1,@fecha_inicio=:fecha1,@fecha_fin=:fecha2,@sucursal=null,@cedula=null,@moneda_nombre='quetzales'"),fecha1=fecha1,fecha2=fecha2).fetchall()
            montos_Panama = connection.execute(text("EXEC consultar_montos_recolectados @opcion=1,@fecha_inicio=:fecha1,@fecha_fin=:fecha2,@sucursal=null,@cedula=null,@moneda_nombre='balboas'"),fecha1=fecha1,fecha2=fecha2).fetchall()
            montos = [montos_CR,montos_Guatemala,montos_Panama]
            print(montos)
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            print(sucursales)
            return render_template("consultar_montos_recolectados_fechas.html",montos=montos,sucursales=sucursales,fecha1=fecha1,fecha2=fecha2)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Por favor escriba un rango de fechas válido y use el formato YYYY-MM-DD.', category='error')
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            print(sucursales)
            fecha1=None
            fecha2=None
            return render_template("consultar_montos_recolectados_fechas.html",sucursales=sucursales,fecha1=fecha1,fecha2=fecha2)

@views.route('/consultar_bonos_pais',methods=['GET','POST'])
def consultar_bonos_pais():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    pais = request.args.get('pais', default = '*', type = str)
    with sqlcon.connect() as connection:
        bonos = connection.execute(text("EXEC informacion_bonos_recibidos @opcion =2,@fecha_inicio=null,@fecha_fin=null,@empleado_ID =null,@pais=:pais,@sucursal=null"),pais=pais).fetchall()
        print(bonos)
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(sucursales)
        return render_template("consultar_bonos_pais.html",bonos=bonos,sucursales=sucursales)

@views.route('/consultar_bonos_sucursal',methods=['GET','POST'])
def consultar_bonos_sucursal():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    sucursal = request.args.get('sucursal', default = '*', type = str)
    with sqlcon.connect() as connection:
        bonos = connection.execute(text("EXEC informacion_bonos_recibidos @opcion =3,@fecha_inicio=null,@fecha_fin=null,@empleado_ID =null,@pais=null,@sucursal=:sucursal"),sucursal=sucursal).fetchall()
        print(bonos)
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(sucursales)
        return render_template("consultar_bonos_sucursal.html",bonos=bonos,sucursales=sucursales)

@views.route('/consultar_bonos_fechas',methods=['GET','POST'])
def consultar_bonos_fechas():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    fecha1 = request.args.get('fecha1', default = '*', type = str)
    fecha2 = request.args.get('fecha2', default = '*', type = str)
    print(fecha1)
    print(fecha2)
    with sqlcon.connect() as connection:
        try:
            bonos = connection.execute(text("EXEC informacion_bonos_recibidos @opcion =1,@fecha_inicio=:fecha1,@fecha_fin=:fecha2,@empleado_ID =null,@pais=null,@sucursal=null"),fecha1=fecha1,fecha2=fecha2).fetchall()
            print(bonos)
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            (sucursales)
            return render_template("consultar_bonos_fechas.html",bonos=bonos,sucursales=sucursales,fecha1=fecha1,fecha2=fecha2)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            fecha1=None
            fecha2=None
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            flash('Las fechas deben utilizar el formato YYYY-MM-DD', category='error')
            return render_template("consultar_bonos_fechas.html",sucursales=sucursales,fecha1=fecha1,fecha2=fecha2)

@views.route('/consultar_bonos_empleado',methods=['GET','POST'])
def consultar_bonos_empleado():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    empleado = request.args.get('cedula', default = '*', type = str)
    with sqlcon.connect() as connection:
        try:
            bonos = connection.execute(text("EXEC informacion_bonos_recibidos @opcion =4,@fecha_inicio=null,@fecha_fin=null,@empleado_ID =:empleado,@pais=null,@sucursal=null"),empleado=empleado).fetchall()
            print(bonos)
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            print(sucursales)
            return render_template("consultar_bonos_empleado.html",bonos=bonos,sucursales=sucursales)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Por favor digite una cédula válida.', category='error')
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            return render_template("consultar_bonos_empleado.html.html",sucursales=sucursales)

@views.route('/consultar_ganancias_netas_pais',methods=['GET','POST'])
def consultar_ganancias_netas_pais():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    pais = request.args.get('pais', default = '*', type = str)
    moneda = ""
    if pais == "Costa Rica":
        moneda = "colones"
    elif pais == "Guatemala":
        moneda = "quetzales"
    elif pais == "Panama":
        moneda = "balboas"
    print(pais)
    print(moneda)
    with sqlcon.connect() as connection:
        ganancias = connection.execute(text("EXEC informacion_ganancias @opcion=2,@fecha_inicio=null,@fecha_fin=null,@pais=:pais,@sucursal=null,@categoria=null,@moneda_nombre=:moneda"),pais=pais,moneda=moneda).fetchall()
        print(ganancias)
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(sucursales)
        return render_template("consultar_ganancias_netas_pais.html",ganancias=ganancias,sucursales=sucursales,pais=pais,moneda=moneda)

@views.route('/consultar_ganancias_netas_sucursal',methods=['GET','POST'])
def consultar_ganancias_netas_sucursal():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    sucursal = request.args.get('sucursal', default = '*', type = str)
    moneda = ""
    with sqlcon.connect() as connection:
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        moneda = connection.execute(text("select moneda_nombre from Sucursales where nombre=:nombre"),nombre=sucursal).fetchall()
        ganancias = connection.execute(text("EXEC informacion_ganancias @opcion=3,@fecha_inicio=null,@fecha_fin=null,@pais=null,@sucursal=:sucursal,@categoria=null,@moneda_nombre=:moneda"),sucursal=sucursal,moneda=moneda[0][0]).fetchall()
        
        print(ganancias)
        print(sucursales)
        print(moneda)
        print(moneda[0][0])
        return render_template("consultar_ganancias_netas_sucursal.html",ganancias=ganancias,sucursales=sucursales,sucursal=sucursal,moneda=moneda)

@views.route('/consultar_ganancias_netas_categoria',methods=['GET','POST'])
def consultar_ganancias_netas_categoria():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    categoria = request.args.get('categoria', default = '*', type = str)
    print(categoria)
    with sqlcon.connect() as connection:
        ganancias_CR = connection.execute(text("EXEC informacion_ganancias @opcion=4,@fecha_inicio=null,@fecha_fin=null,@pais=null,@sucursal=null,@categoria=:categoria,@moneda_nombre='colones'"),categoria=categoria).fetchall()
        ganancias_Guatemala = connection.execute(text("EXEC informacion_ganancias @opcion=5,@fecha_inicio=null,@fecha_fin=null,@pais=null,@sucursal=null,@categoria=:categoria,@moneda_nombre='quetzales'"),categoria=categoria).fetchall()
        ganancias_Panama = connection.execute(text("EXEC informacion_ganancias @opcion=5,@fecha_inicio=null,@fecha_fin=null,@pais=null,@sucursal=null,@categoria=:categoria,@moneda_nombre='balboas'"),categoria=categoria).fetchall()
        ganancias=[ganancias_CR,ganancias_Guatemala,ganancias_Panama]
        print(ganancias)
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(sucursales)
        return render_template("consultar_ganancias_netas_categoria.html",ganancias=ganancias,sucursales=sucursales,categoria=categoria)

@views.route('/consultar_ganancias_netas_fechas',methods=['GET','POST'])
def consultar_ganancias_netas_fechas():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    fecha1 = request.args.get('fecha1', default = '*', type = str)
    fecha2 = request.args.get('fecha2', default = '*', type = str)
    print(fecha1)
    print(fecha2)
    with sqlcon.connect() as connection:
        try:
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            print(sucursales)
            ganancias_CR = connection.execute(text("EXEC informacion_ganancias @opcion=1,@fecha_inicio=:fecha1,@fecha_fin=:fecha2,@pais=null,@sucursal=null,@categoria=null,@moneda_nombre='colones'"),fecha1=fecha1,fecha2=fecha2).fetchall()
            ganancias_Guatemala = connection.execute(text("EXEC informacion_ganancias @opcion=1,@fecha_inicio=:fecha1,@fecha_fin=:fecha2,@pais=null,@sucursal=null,@categoria=null,@moneda_nombre='quetzales'"),fecha1=fecha1,fecha2=fecha2).fetchall()
            ganancias_Panama = connection.execute(text("EXEC informacion_ganancias @opcion=1,@fecha_inicio=:fecha1,@fecha_fin=:fecha2,@pais=null,@sucursal=null,@categoria=null,@moneda_nombre='balboas'"),fecha1=fecha1,fecha2=fecha2).fetchall()
            ganancias=[ganancias_CR,ganancias_Guatemala,ganancias_Panama]
            print(ganancias)
            return render_template("consultar_ganancias_netas_fechas.html",ganancias=ganancias,sucursales=sucursales,fecha1=fecha1,fecha2=fecha2)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            fecha1=None
            fecha2=None
            flash('Las fechas deben utilizar el formato YYYY-MM-DD', category='error')
            return render_template("consultar_ganancias_netas_fechas.html",sucursales=sucursales,fecha1=fecha1,fecha2=fecha2)

@views.route('/consultar_empleados',methods=['GET','POST'])
def consultar_empleados():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        try:
            empleados = connection.execute(text("EXEC CRUD_Empleado @opcion=5,@tipo_consulta=null,@cedula=null,@nombre=null,@apellido=null,@correo=null, @telefono=null,@fecha_contratacion=null,@sucursal_ID=null,@pais=null,@puesto=null,@foto_filename=null,@administrador =null,@salario_base=null,@estado_ID=null,@password=null,@fecha2=null")).fetchall()
            print(empleados)
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            print(sucursales)
            puestos = connection.execute(text("SELECT nombre from Puestos")).fetchall()
            print(sucursales)
            return render_template("consultar_empleados.html",empleados=empleados,sucursales=sucursales,puestos=puestos)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            puestos = connection.execute(text("SELECT nombre from Puestos")).fetchall()
            return render_template("consultar_empleados.html",sucursales=sucursales,puestos=puestos)

@views.route('/consultar_empleados_fechas',methods=['GET','POST'])
def consultar_empleados_fechas():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    fecha1 = request.args.get('fecha1', default = '*', type = str)
    fecha2 = request.args.get('fecha2', default = '*', type = str)
    print(fecha1)
    print(fecha2)
    
    with sqlcon.connect() as connection:
        try:
            empleados = connection.execute(text("EXEC CRUD_Empleado @opcion=2,@tipo_consulta=2,@cedula=null,@nombre=null,@apellido=null,@correo=null, @telefono=null,@fecha_contratacion=:fecha1,@sucursal_ID=null,@pais=null,@puesto=null,@foto_filename=null,@administrador =null,@salario_base=null,@estado_ID=null,@fecha2=:fecha2,@password=null"),fecha1=fecha1,fecha2=fecha2).fetchall()
            print(empleados)
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            print(sucursales)
            puestos = connection.execute(text("SELECT nombre from Puestos")).fetchall()
            print(sucursales)
            return render_template("consultar_empleados_fechas.html",empleados=empleados,sucursales=sucursales,puestos=puestos)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            fecha1=None
            fecha2=None
            flash('Las fechas deben utilizar el formato YYYY-MM-DD', category='error')
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            print(sucursales)
            puestos = connection.execute(text("SELECT nombre from Puestos")).fetchall()
            print(sucursales)
            return render_template("consultar_empleados_fechas.html",sucursales=sucursales,puestos=puestos)

@views.route('/consultar_empleados_sucursal',methods=['GET','POST'])
def consultar_empleados_sucursal():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    sucursal = request.args.get('sucursal', default = '*', type = str)
    with sqlcon.connect() as connection:
        sucursal_ID_query = connection.execute(text("SELECT sucursal_ID from Sucursales where nombre=:sucursal"),sucursal=sucursal).fetchall()
        sucursal_ID = sucursal_ID_query[0][0]
        empleados = connection.execute(text("EXEC CRUD_Empleado @opcion=2,@tipo_consulta=3,@cedula=null,@nombre=null,@apellido=null,@correo=null, @telefono=null,@fecha_contratacion=null,@sucursal_ID=:sucursal_ID,@pais=null,@puesto=null,@foto_filename=null,@administrador =null,@salario_base=null,@estado_ID=null,@fecha2=null,@password=null"),sucursal_ID=sucursal_ID).fetchall()
        print(empleados)
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(sucursales)
        puestos = connection.execute(text("SELECT nombre from Puestos")).fetchall()
        print(sucursal)
        print(puestos)
        return render_template("consultar_empleados_sucursal.html",empleados=empleados,sucursales=sucursales,puestos=puestos)

@views.route('/consultar_empleados_puestos',methods=['GET','POST'])
def consultar_empleados_puestos():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    puesto = request.args.get('puesto', default = '*', type = str)
    with sqlcon.connect() as connection:
        empleados = connection.execute(text("EXEC CRUD_Empleado @opcion=2,@tipo_consulta=1,@cedula=null,@nombre=null,@apellido=null,@correo=null, @telefono=null,@fecha_contratacion=null,@sucursal_ID=null,@pais=null,@puesto=:puesto,@foto_filename=null,@administrador =null,@salario_base=null,@estado_ID=null,@fecha2=null,@password=null"),puesto=puesto).fetchall()
        print(empleados)
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(sucursales)
        puestos = connection.execute(text("SELECT nombre from Puestos")).fetchall()
        print(puestos)
        print(puesto)
        return render_template("consultar_empleados_puestos.html",empleados=empleados,sucursales=sucursales,puestos=puestos)

@views.route('/generar_reportes',methods=['GET','POST'])
def generar_reportes():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        return render_template("generar_reportes.html")

@views.route('/productos_mas_vendidos',methods=['GET','POST'])
def productos_mas_vendidos():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
        proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
        return render_template("productos_mas_vendidos.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores)

@views.route('/productos_mas_vendidos_pais',methods=['GET','POST'])
def productos_mas_vendidos_pais():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    pais = request.args.get('pais', default = '*', type = str)
    moneda = 'colones'
    if pais=='Costa Rica':
        moneda='colones'
    elif pais=='Guatemala':
        moneda='quetzales'
    elif pais=='Panama':
        moneda='balboas'
    with sqlcon.connect() as connection:
        try:
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            reporte = connection.execute(text("EXEC generar_reporte_estadisticas @opcion =1,@subopcion =1,@sucursal_ID =null,@administrador_cedula =null,@pais =:pais,@producto_ID =null,@fecha_inicio =null,@fecha_fin =null,@proveedor_ID =null"),pais=pais).fetchall()
            print(reporte)
            return render_template("productos_mas_vendidos_pais.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,reporte=reporte,moneda=moneda,pais=pais)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            return render_template("productos_mas_vendidos_pais.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,moneda=moneda,pais=pais)
    
@views.route('/productos_mas_vendidos_productos',methods=['GET','POST'])
def productos_mas_vendidos_productos():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    producto = request.args.get('producto', default = '*', type = str)
    with sqlcon.connect() as connection:
        try:
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            producto_ID_list = connection.execute(text("SELECT producto_ID from Productos_Fotos where thumbnail=1 and nombre=:producto"),producto=producto).fetchall()
            producto_ID = producto_ID_list[0][0]
            print(producto_ID)
            reporte = connection.execute(text("EXEC generar_reporte_estadisticas @opcion =1,@subopcion =2,@sucursal_ID =null,@administrador_cedula =null,@pais =null,@producto_ID = :producto_ID,@fecha_inicio =null,@fecha_fin =null,@proveedor_ID =null"),producto_ID=producto_ID).fetchall()
            print(reporte)
            return render_template("productos_mas_vendidos_productos.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,reporte=reporte)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            return render_template("productos_mas_vendidos_productos.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores)

@views.route('/productos_mas_vendidos_proveedor',methods=['GET','POST'])
def productos_mas_vendidos_proveedor():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    proveedor = request.args.get('proveedor', default = '*', type = str)
    with sqlcon.connect() as connection:
        try:
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            proveedor_ID_list = connection.execute(text("SELECT proveedor_ID from Proveedores where nombre=:proveedor"),proveedor=proveedor).fetchall()
            proveedor_ID = proveedor_ID_list[0][0]
            print(proveedor_ID)
            reporte = connection.execute(text("EXEC generar_reporte_estadisticas @opcion =1,@subopcion =4,@sucursal_ID =null,@administrador_cedula =null,@pais =null,@producto_ID = null,@fecha_inicio =null,@fecha_fin =null,@proveedor_ID =:proveedor_ID"),proveedor_ID=proveedor_ID).fetchall()
            print(reporte)
            return render_template("productos_mas_vendidos_proveedor.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,reporte=reporte,proveedor=proveedor)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            return render_template("productos_mas_vendidos_proveedor.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores)

@views.route('/productos_mas_vendidos_fechas',methods=['GET','POST'])
def productos_mas_vendidos_fechas():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    fecha1 = request.args.get('fecha1', default = '*', type = str)
    fecha2 = request.args.get('fecha2', default = '*', type = str)

    with sqlcon.connect() as connection:
        try:
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            reporte = connection.execute(text("EXEC generar_reporte_estadisticas @opcion =1,@subopcion =3,@sucursal_ID =null,@administrador_cedula =null,@pais =null,@producto_ID = null,@fecha_inicio =:fecha1,@fecha_fin =:fecha2,@proveedor_ID =null"),fecha1=fecha1,fecha2=fecha2).fetchall()
            print(reporte)
            return render_template("productos_mas_vendidos_fechas.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,reporte=reporte)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Fechas inválidas, intente de nuevo', category='error')
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            return render_template("productos_mas_vendidos_fechas.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores)

@views.route('/clientes_mas_frecuentes',methods=['GET','POST'])
def clientes_mas_frecuentes():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
        proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
        return render_template("clientes_mas_frecuentes.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores)

@views.route('/clientes_mas_frecuentes_pais',methods=['GET','POST'])
def clientes_mas_frecuentes_pais():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    pais = request.args.get('pais', default = '*', type = str)
    moneda = 'colones'
    if pais=='Costa Rica':
        moneda='colones'
    elif pais=='Guatemala':
        moneda='quetzales'
    elif pais=='Panama':
        moneda='balboas'
    with sqlcon.connect() as connection:
        try:
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            reporte = connection.execute(text("EXEC generar_reporte_estadisticas @opcion =2,@subopcion =1,@sucursal_ID =null,@administrador_cedula =null,@pais =:pais,@producto_ID =null,@fecha_inicio =null,@fecha_fin =null,@proveedor_ID =null"),pais=pais).fetchall()
            print(reporte)
            return render_template("clientes_mas_frecuentes_pais.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,reporte=reporte,moneda=moneda,pais=pais)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            return render_template("clientes_mas_frecuentes_pais.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,moneda=moneda,pais=pais)
    
@views.route('/clientes_mas_frecuentes_productos',methods=['GET','POST'])
def clientes_mas_frecuentes_productos():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    producto = request.args.get('producto', default = '*', type = str)
    with sqlcon.connect() as connection:
        try:
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            producto_ID_list = connection.execute(text("SELECT producto_ID from Productos_Fotos where thumbnail=1 and nombre=:producto"),producto=producto).fetchall()
            producto_ID = producto_ID_list[0][0]
            print(producto_ID)
            reporte = connection.execute(text("EXEC generar_reporte_estadisticas @opcion =2,@subopcion =2,@sucursal_ID =null,@administrador_cedula =null,@pais =null,@producto_ID = :producto_ID,@fecha_inicio =null,@fecha_fin =null,@proveedor_ID =null"),producto_ID=producto_ID).fetchall()
            print(reporte)
            return render_template("clientes_mas_frecuentes_productos.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,reporte=reporte)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            return render_template("clientes_mas_frecuentes_productos.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores)

@views.route('/clientes_mas_frecuentes_proveedor',methods=['GET','POST'])
def clientes_mas_frecuentes_proveedor():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    proveedor = request.args.get('proveedor', default = '*', type = str)
    with sqlcon.connect() as connection:
        try:
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            proveedor_ID_list = connection.execute(text("SELECT proveedor_ID from Proveedores where nombre=:proveedor"),proveedor=proveedor).fetchall()
            proveedor_ID = proveedor_ID_list[0][0]
            print(proveedor_ID)
            reporte = connection.execute(text("EXEC generar_reporte_estadisticas @opcion =2,@subopcion =4,@sucursal_ID =null,@administrador_cedula =null,@pais =null,@producto_ID = null,@fecha_inicio =null,@fecha_fin =null,@proveedor_ID =:proveedor_ID"),proveedor_ID=proveedor_ID).fetchall()
            print(reporte)
            return render_template("clientes_mas_frecuentes_proveedor.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,reporte=reporte,proveedor=proveedor)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            return render_template("clientes_mas_frecuentes_proveedor.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores)

@views.route('/clientes_mas_frecuentes_fechas',methods=['GET','POST'])
def clientes_mas_frecuentes_fechas():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    fecha1 = request.args.get('fecha1', default = '*', type = str)
    fecha2 = request.args.get('fecha2', default = '*', type = str)

    with sqlcon.connect() as connection:
        try:
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            reporte = connection.execute(text("EXEC generar_reporte_estadisticas @opcion =2,@subopcion =3,@sucursal_ID =null,@administrador_cedula =null,@pais =null,@producto_ID = null,@fecha_inicio =:fecha1,@fecha_fin =:fecha2,@proveedor_ID =null"),fecha1=fecha1,fecha2=fecha2).fetchall()
            print(reporte)
            return render_template("clientes_mas_frecuentes_fechas.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,reporte=reporte)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Fechas inválidas, intente de nuevo', category='error')
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            return render_template("clientes_mas_frecuentes_fechas.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores)

@views.route('/productos_expirados',methods=['GET','POST'])
def productos_expirados():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
        proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
        return render_template("productos_expirados.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores)

@views.route('/productos_expirados_pais',methods=['GET','POST'])
def productos_expirados_pais():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    pais = request.args.get('pais', default = '*', type = str)
    moneda = 'colones'
    if pais=='Costa Rica':
        moneda='colones'
    elif pais=='Guatemala':
        moneda='quetzales'
    elif pais=='Panama':
        moneda='balboas'
    with sqlcon.connect() as connection:
        try:
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            reporte = connection.execute(text("EXEC generar_reporte_estadisticas @opcion =3,@subopcion =1,@sucursal_ID =null,@administrador_cedula =null,@pais =:pais,@producto_ID =null,@fecha_inicio =null,@fecha_fin =null,@proveedor_ID =null"),pais=pais).fetchall()
            print(reporte)
            return render_template("productos_expirados_pais.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,reporte=reporte,moneda=moneda,pais=pais)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            return render_template("productos_expirados_pais.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,moneda=moneda,pais=pais)
    
@views.route('/productos_expirados_productos',methods=['GET','POST'])
def productos_expirados_productos():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    producto = request.args.get('producto', default = '*', type = str)
    with sqlcon.connect() as connection:
        try:
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            producto_ID_list = connection.execute(text("SELECT producto_ID from Productos_Fotos where thumbnail=1 and nombre=:producto"),producto=producto).fetchall()
            producto_ID = producto_ID_list[0][0]
            print(producto_ID)
            reporte = connection.execute(text("EXEC generar_reporte_estadisticas @opcion =3,@subopcion =2,@sucursal_ID =null,@administrador_cedula =null,@pais =null,@producto_ID = :producto_ID,@fecha_inicio =null,@fecha_fin =null,@proveedor_ID =null"),producto_ID=producto_ID).fetchall()
            print(reporte)
            return render_template("productos_expirados_productos.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,reporte=reporte)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            return render_template("productos_expirados_productos.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores)

@views.route('/productos_expirados_proveedor',methods=['GET','POST'])
def productos_expirados_proveedor():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    proveedor = request.args.get('proveedor', default = '*', type = str)
    with sqlcon.connect() as connection:
        try:
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            proveedor_ID_list = connection.execute(text("SELECT proveedor_ID from Proveedores where nombre=:proveedor"),proveedor=proveedor).fetchall()
            proveedor_ID = proveedor_ID_list[0][0]
            print(proveedor_ID)
            reporte = connection.execute(text("EXEC generar_reporte_estadisticas @opcion =3,@subopcion =4,@sucursal_ID =null,@administrador_cedula =null,@pais =null,@producto_ID = null,@fecha_inicio =null,@fecha_fin =null,@proveedor_ID =:proveedor_ID"),proveedor_ID=proveedor_ID).fetchall()
            print(reporte)
            return render_template("productos_expirados_proveedor.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,reporte=reporte,proveedor=proveedor)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            return render_template("productos_expirados_proveedor.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores)

@views.route('/productos_expirados_fechas',methods=['GET','POST'])
def productos_expirados_fechas():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    fecha1 = request.args.get('fecha1', default = '*', type = str)
    fecha2 = request.args.get('fecha2', default = '*', type = str)

    with sqlcon.connect() as connection:
        try:
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            reporte = connection.execute(text("EXEC generar_reporte_estadisticas @opcion =3,@subopcion =3,@sucursal_ID =null,@administrador_cedula =null,@pais =null,@producto_ID = null,@fecha_inicio =:fecha1,@fecha_fin =:fecha2,@proveedor_ID =null"),fecha1=fecha1,fecha2=fecha2).fetchall()
            print(reporte)
            return render_template("productos_expirados_fechas.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores,reporte=reporte)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Fechas inválidas, intente de nuevo', category='error')
            paises = connection.execute(text("SELECT nombre from Paises")).fetchall()
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            productos = connection.execute(text("SELECT nombre from Productos_Fotos where thumbnail=1")).fetchall()
            proveedores = connection.execute(text("SELECT nombre from Proveedores")).fetchall()
            return render_template("productos_expirados_fechas.html",paises=paises,sucursales=sucursales,productos=productos,proveedores=proveedores)

@views.route('/ingresar_empleado', methods=['GET','POST'])
def ingresar_empleado():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')

    if request.method == 'POST':
        cedula = int(request.form.get('cedula'))
        correo = request.form.get('email')
        nombre = request.form.get('firstName')
        apellido = request.form.get('lastName')
        telefono = int(request.form.get('telefono'))
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        pais = request.form.get('pais')
        puesto = request.form.get('puesto')
        foto_filename = request.form.get('link_imagen')
        administrador = 0

        if puesto == 'Administrador':
            administrador = 1

        sucursal = request.form.get('sucursal')
        salario_base = int(request.form.get('salario_base'))
        print(request.form)

        if (password1 != password2):
            flash("Las passwords deben ser iguales.",category='error')
            with sqlcon.begin() as connection:
                sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
                puestos = connection.execute(text("SELECT nombre from Puestos")).fetchall()
                return render_template("ingresar_empleado.html",sucursales=sucursales,puestos=puestos)
        elif nombre == None or nombre == "" or nombre == " ":
            flash("El nombre no puede estar vacío.",category='error')
            with sqlcon.begin() as connection:
                sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
                puestos = connection.execute(text("SELECT nombre from Puestos")).fetchall()
                return render_template("ingresar_empleado.html",sucursales=sucursales,puestos=puestos)
        elif(bool(re.match('[a-zA-Z\s]+$', nombre))==False):
            flash("Solo puede usar caracteres de A-Z.",category='error')
            with sqlcon.begin() as connection:
                sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
                puestos = connection.execute(text("SELECT nombre from Puestos")).fetchall()
                return render_template("ingresar_empleado.html",sucursales=sucursales,puestos=puestos)
        elif apellido == None or apellido == "" or apellido == " ":
            flash("El apellido no puede estar vacío.",category='error')
            with sqlcon.begin() as connection:
                sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
                puestos = connection.execute(text("SELECT nombre from Puestos")).fetchall()
                return render_template("ingresar_empleado.html",sucursales=sucursales,puestos=puestos)
        elif(bool(re.match('[a-zA-Z\s]+$', apellido))==False):
            flash("Solo puede usar caracteres de A-Z.",category='error')
            with sqlcon.begin() as connection:
                sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
                puestos = connection.execute(text("SELECT nombre from Puestos")).fetchall()
                return render_template("ingresar_empleado.html",sucursales=sucursales,puestos=puestos)
        elif foto_filename == None or foto_filename == "" or foto_filename == " ":
            flash("El URL no puede estar vacío.",category='error')
            with sqlcon.begin() as connection:
                sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
                puestos = connection.execute(text("SELECT nombre from Puestos")).fetchall()
                return render_template("ingresar_empleado.html",sucursales=sucursales,puestos=puestos)

        else:
            password = generate_password_hash(password1)
            print(password)

            try:
                with sqlcon.begin() as connection:
                    connection.execution_options(isolation_level="AUTOCOMMIT")
                    sucursal_ID_list = connection.execute(text("SELECT sucursal_ID from Sucursales where nombre=:sucursal"),sucursal=sucursal).fetchall()
                    sucursal_ID = sucursal_ID_list[0][0]
                    connection.execute(text("DECLARE @fecha_actual datetime = getdate(); EXEC CRUD_Empleado @opcion=1,@tipo_consulta=null,@cedula=:cedula,@nombre=:nombre,@apellido=:apellido,@correo=:correo,@password=:password,@telefono=:telefono,@fecha_contratacion=@fecha_actual,@sucursal_ID=:sucursal_ID,@pais=:pais,@puesto=:puesto,@foto_filename=:foto_filename,@administrador=:administrador,@salario_base=:salario_base,@estado_ID=1,@fecha2=null"),cedula=cedula,nombre=nombre,apellido=apellido,correo=correo,password=password,telefono=telefono,sucursal_ID=sucursal_ID,pais=pais,puesto=puesto,foto_filename=foto_filename,administrador=administrador,salario_base=salario_base)
                    flash('Se ha ingresado un empleado correctamente!', category='success')
                    products = connection.execute(text("EXEC CRUD_producto @opcion=6,@nombre=null, @descripcion=null, @categoria_ID = null, @tiene_impuesto =null, @minimo =null, @maximo =null,@fecha_produccion=null, @fecha_expiracion=null, @en_descuento=null, @precio=null, @estado_ID=null, @sucursal_ID=null,@cantidad=null,@producto_ID=null,@proveedor_ID=null,@porcentaje_descuento=null")).fetchall()
                    return render_template("home.html",products=products,comprado=False)
            except exc.SQLAlchemyError as e:
                print(e.__cause__)
                flash("El empleado ya está registrado en la base de datos.", category='error')
                return render_template("ingresar_empleado.html")
            
    if request.method == 'GET':
        with sqlcon.begin() as connection:
            sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
            puestos = connection.execute(text("SELECT nombre from Puestos")).fetchall()
            return render_template("ingresar_empleado.html",sucursales=sucursales,puestos=puestos)

@views.route('/cambiar_foto_anual', methods=['GET','POST'])
def cambiar_foto_anual():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    filename = request.args.get('filename', default = '*', type = str)
    cedula = request.args.get('cedula', default = 0, type = int)
    print(filename)
    print(cedula)

    if request.method == 'POST':
        try:
            with sqlcon.begin() as connection:
                foto_ID_list = connection.execute(text("select foto_ID from Fotos inner join Empleados on Fotos.filename=Empleados.foto_filename where Empleados.cedula=:cedula"),cedula=cedula).fetchall()
                foto_ID = foto_ID_list[0][0]
                print(foto_ID)
                filename_cambiar = request.form.get('link_imagen')
                print(filename_cambiar)
                connection.execution_options(isolation_level="AUTOCOMMIT")
                if (foto_ID < 2999):
                    connection.execute(text("update Foto set filename=:filename_cambiar where foto_ID=:foto_ID"),filename_cambiar=filename_cambiar,foto_ID=foto_ID)
                elif (foto_ID >= 3000):
                    connection.execute(text("update Fotos_Guatemala set filename=:filename_cambiar where foto_ID=:foto_ID"),filename_cambiar=filename_cambiar,foto_ID=foto_ID)
                elif (foto_ID >= 4000):
                    connection.execute(text("update Fotos_Panama set filename=:filename_cambiar where foto_ID=:foto_ID"),filename_cambiar=filename_cambiar,foto_ID=foto_ID)
                flash('Se ha cambiado su imagen correctamente!', category='success')
                return render_template("cambiar_foto_anual.html",filename=filename,filename_cambiar=filename_cambiar)
        except exc.SQLAlchemyError as e:
            print(e)
            flash("Error al cambiar la imagen, intente de nuevo", category='error')
            return render_template("cambiar_foto_anual.html",filename=filename)
    
    return render_template("cambiar_foto_anual.html",filename=filename)

@views.route('/revisar_productos',methods=['GET','POST'])
def revisar_productos():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        productos = connection.execute(text("EXEC CRUD_producto @opcion=6,@nombre=null, @descripcion=null, @categoria_ID = null, @tiene_impuesto =null, @minimo =null, @maximo =null,@fecha_produccion=null, @fecha_expiracion=null, @en_descuento=null, @precio=null, @estado_ID=null, @sucursal_ID=null,@cantidad=null,@producto_ID=null,@proveedor_ID=null,@porcentaje_descuento=null")).fetchall()
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(productos)
        return render_template("revisar_productos.html",productos=productos,sucursales=sucursales)

@views.route('/revisar_expirados',methods=['GET','POST'])
def revisar_expirados():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    sucursal = request.args.get('sucursal', default = '*', type = str)
    with sqlcon.connect() as connection:
        sucursal_ID_list = connection.execute(text("SELECT sucursal_ID from Sucursales where nombre=:sucursal"),sucursal=sucursal).fetchall()
        sucursal_ID = sucursal_ID_list[0][0]
        productos = connection.execute(text("EXEC revisar_expirados @opcion =4,@producto_ID =null,@sucursal_ID =:sucursal_ID,@descuento_porcentaje = null"),sucursal_ID=sucursal_ID).fetchall()
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(productos)
        return render_template("revisar_expirados.html",productos=productos,sucursales=sucursales,sucursal_ID=sucursal_ID,sucursal=sucursal)

@views.route('/revisar_casi_expirados',methods=['GET','POST'])
def revisar_casi_expirados():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    sucursal = request.args.get('sucursal', default = '*', type = str)
    with sqlcon.connect() as connection:
        sucursal_ID_list = connection.execute(text("SELECT sucursal_ID from Sucursales where nombre=:sucursal"),sucursal=sucursal).fetchall()
        sucursal_ID = sucursal_ID_list[0][0]
        productos = connection.execute(text("EXEC revisar_expirados @opcion =1,@producto_ID =null,@sucursal_ID =:sucursal_ID,@descuento_porcentaje = null"),sucursal_ID=sucursal_ID).fetchall()
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(productos)
        return render_template("revisar_casi_expirados.html",productos=productos,sucursales=sucursales,sucursal=sucursal,sucursal_ID=sucursal_ID)

@views.route('/revisar_expirados_quitar_exhibidor',methods=['GET','POST'])
def revisar_expirados_quitar_exhibidor():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    sucursal_ID = request.args.get('sucursal_ID', default = '*', type = int)
    sucursal = request.args.get('sucursal', default = '*', type = str)
    with sqlcon.begin() as connection:
        connection.execution_options(isolation_level="AUTOCOMMIT")
        connection.execute(text("EXEC revisar_expirados @opcion =3,@producto_ID =null,@sucursal_ID =:sucursal_ID,@descuento_porcentaje = null"),sucursal_ID=sucursal_ID)
        productos = connection.execute(text("EXEC revisar_expirados @opcion =4,@producto_ID =null,@sucursal_ID =:sucursal_ID,@descuento_porcentaje = null"),sucursal_ID=sucursal_ID).fetchall()
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(productos)
        flash('Se han puesto en descuento los productos expirados correctamente.', category='success')
        return render_template("revisar_expirados.html",productos=productos,sucursales=sucursales,sucursal_ID=sucursal_ID,sucursal=sucursal)

@views.route('/revisar_casi_expirados_descuento',methods=['GET','POST'])
def revisar_casi_expirados_descuento():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    sucursal_ID = request.args.get('sucursal_ID', default = 0, type = int)
    sucursal = request.args.get('sucursal', default = '*', type = str)
    descuento = request.form.get('descuento', default = 0, type = int)
    print(sucursal_ID)
    print(sucursal)
    print(descuento)
    with sqlcon.begin() as connection:
        connection.execution_options(isolation_level="AUTOCOMMIT")
        connection.execute(text("EXEC revisar_expirados @opcion =2,@producto_ID =null,@sucursal_ID =:sucursal_ID,@descuento_porcentaje = :descuento"),sucursal_ID=sucursal_ID,descuento=descuento)
        productos = connection.execute(text("EXEC revisar_expirados @opcion =1,@producto_ID =null,@sucursal_ID =:sucursal_ID,@descuento_porcentaje = null"),sucursal_ID=sucursal_ID).fetchall()
        sucursales = connection.execute(text("SELECT nombre from Sucursales")).fetchall()
        print(productos)
        flash('Se han puesto en descuento los productos cerca de expirar correctamente.', category='success')
        return render_template("revisar_casi_expirados.html",productos=productos,sucursales=sucursales,sucursal_ID=sucursal_ID,sucursal=sucursal)

@views.route('/reordenar_producto',methods=['GET','POST'])
def reordenar_producto():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        productos = connection.execute(text("select producto_ID,sucursal_ID,sucursal,pais,moneda_nombre,nombre,descripcion,categoria,impuesto_porcentaje,minimo,maximo,(Productos_Fotos.maximo-Productos_Fotos.cantidad) as faltan_para_maximo,precio,proveedor,proveedor_ID,proveedor_porcentaje,cantidad,porcentaje_descuento from Productos_Fotos where Productos_Fotos.cantidad < Productos_Fotos.minimo and thumbnail=1")).fetchall()
        return render_template("reordenar_producto.html",productos=productos)

@views.route('/reordenar_producto_pedido',methods=['GET','POST'])
def reordenar_producto_pedido():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    sucursal_ID = request.args.get('sucursal_ID', default = '*', type = int)
    producto_ID = request.args.get('producto_ID', default = '*', type = int)
    print(sucursal_ID)
    print(producto_ID)

    with sqlcon.begin() as connection:
        cantidad_list = connection.execute(text("select (Productos_Fotos.maximo-Productos_Fotos.cantidad) as faltan_para_maximo from Productos_Fotos where Productos_Fotos.cantidad < Productos_Fotos.minimo and thumbnail=1 and producto_ID=1")).fetchall()
        cantidad = cantidad_list[0][0]
        print(cantidad)
        proveedor_list = connection.execute(text("EXEC reordenar_producto @opcion =2,@producto_ID =:producto_ID,@sucursal_ID =:sucursal_ID,@descripcion ='Reorden de productos',@cantidad=:cantidad"),producto_ID=producto_ID,sucursal_ID=sucursal_ID,cantidad=cantidad).fetchall()
        proveedor = proveedor_list[0][1]
        print(proveedor)
        with sqlcon.begin() as connection:
            try:
                connection.execution_options(isolation_level="AUTOCOMMIT")
                connection.execute(text("EXEC reordenar_producto @opcion =1,@producto_ID =:producto_ID,@sucursal_ID =:sucursal_ID,@descripcion ='Reorden de productos',@cantidad=:cantidad"),producto_ID=producto_ID,sucursal_ID=sucursal_ID,cantidad=cantidad).fetchall()
                flash('Se reordenó el producto correctamente del proveedor: '+proveedor,category='success')
                productos = connection.execute(text("select producto_ID,sucursal_ID,sucursal,pais,moneda_nombre,nombre,descripcion,categoria,impuesto_porcentaje,minimo,maximo,(Productos_Fotos.maximo-Productos_Fotos.cantidad) as faltan_para_maximo,precio,proveedor,proveedor_ID,proveedor_porcentaje,cantidad,porcentaje_descuento from Productos_Fotos where Productos_Fotos.cantidad < Productos_Fotos.minimo and thumbnail=1")).fetchall()
                return render_template("reordenar_producto.html",productos=productos)
            except exc.SQLAlchemyError as e:
                print(e)
                flash('No se pudo reordenar el producto del proveedor: '+proveedor,category='error')
                productos = connection.execute(text("select producto_ID,sucursal_ID,sucursal,pais,moneda_nombre,nombre,descripcion,categoria,impuesto_porcentaje,minimo,maximo,(Productos_Fotos.maximo-Productos_Fotos.cantidad) as faltan_para_maximo,precio,proveedor,proveedor_ID,proveedor_porcentaje,cantidad,porcentaje_descuento from Productos_Fotos where Productos_Fotos.cantidad < Productos_Fotos.minimo and thumbnail=1")).fetchall()
                return render_template("reordenar_producto.html",productos=productos)

@views.route('/pagar_salario',methods=['GET','POST'])
def pagar_salario():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        try:
            empleados = connection.execute(text("EXEC CRUD_Empleado @opcion=5,@tipo_consulta=null,@cedula=null,@nombre=null,@apellido=null,@correo=null, @telefono=null,@fecha_contratacion=null,@sucursal_ID=null,@pais=null,@puesto=null,@foto_filename=null,@administrador =null,@salario_base=null,@estado_ID=null,@password=null,@fecha2=null")).fetchall()
            print(empleados)
            return render_template("pagar_salario.html",empleados=empleados)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            return render_template("pagar_salario.html")

@views.route('/pagar_salario_empleado',methods=['GET','POST'])
def pagar_salario_empleado():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    cedula = request.args.get('cedula', default = 0, type = int)
    today = date.today()
    fecha = today.strftime("%Y-%d-%m")
    print(cedula)
    print(fecha)
    with sqlcon.begin() as connection:
        try:
            connection.execution_options(isolation_level="AUTOCOMMIT")
            connection.execute(text("EXEC pagar_salario @opcion = 1,@pago_ID =null,@empleado_cedula=:cedula, @fecha_pago=:fecha , @descripcion ='Pago de salario mensual'"),cedula=cedula,fecha=fecha)
            flash('Salario para el empleado '+str(cedula)+' pagado correctamente.', category='success')
            return render_template("pagar_salario.html")
        except exc.SQLAlchemyError as e:
            print(e)
            flash('Error, intente de nuevo', category='error')
            return render_template("pagar_salario.html")

@views.route('/pagar_salario_ver_pagos',methods=['GET','POST'])
def pagar_salario_ver_pagos():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        try:
            pagos = connection.execute(text("EXEC pagar_salario @opcion = 5,@pago_ID =null,@empleado_cedula=118180816, @fecha_pago=null , @descripcion ='Pago de salario mensual'")).fetchall()
            print(pagos)
            return render_template("pagar_salario_ver_pagos.html",pagos=pagos)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            return render_template("pagar_salario_ver_pagos.html")

@views.route('/pagar_salario_ver_bonos',methods=['GET','POST'])
def pagar_salario_ver_bonos():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        try:
            bonos = connection.execute(text("EXEC informacion_bonos_recibidos @opcion =5,@fecha_inicio=null,@fecha_fin=null,@empleado_ID =118180816,@pais=null,@sucursal=null")).fetchall()
            print(bonos)
            return render_template("pagar_salario_ver_bonos.html",bonos=bonos)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            return render_template("pagar_salario_ver_bonos.html")

@views.route('/pagar_salario_bono_facturador',methods=['GET','POST'])
def pagar_salario_bono_facturador():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    with sqlcon.connect() as connection:
        try:
            bonos = connection.execute(text("EXEC informacion_bonos_recibidos @opcion =5,@fecha_inicio=null,@fecha_fin=null,@empleado_ID =118180816,@pais=null,@sucursal=null")).fetchall()
            print(bonos)
            return render_template("pagar_salario_bono_facturador.html",bonos=bonos)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Error de memoria, intente de nuevo', category='error')
            return render_template("pagar_salario_bono_facturador.html")

@views.route('/pagar_salario_bono_facturador_fechas',methods=['GET','POST'])
def pagar_salario_bono_facturador_fechas():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    fecha1 = request.args.get('fecha1', default = '*', type = str)
    fecha2 = request.args.get('fecha2', default = '*', type = str)
    print(fecha1)
    print(fecha2)
    with sqlcon.connect() as connection:
        try:
            bonos = connection.execute(text("EXEC bono_facturador @opcion=4,@empleado_cedula=null,@sucursal_ID=null,@fecha_comparar=:fecha1,@fecha_bono=:fecha2"),fecha1=fecha1,fecha2=fecha2).fetchall()
            print(bonos)
            return render_template("pagar_salario_bono_facturador_fechas.html",bonos=bonos,fecha1=fecha1,fecha2=fecha2)
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Por favor use el formato YYYY-MM-DD y escriba fechas con una semana de diferencia.', category='error')
            return render_template("pagar_salario_bono_facturador_fechas.html")

@views.route('/pagar_salario_bono_facturador_fechas_otorgar',methods=['GET','POST'])
def pagar_salario_bono_facturador_fechas_otorgar():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')
    fecha1 = request.args.get('fecha1', default = '*', type = str)
    fecha2 = request.args.get('fecha2', default = '*', type = str)
    cedula = request.args.get('cedula', default = '*', type = str)
    print(fecha1)
    print(fecha2)
    print(cedula)
    with sqlcon.connect() as connection:
        try:
            sucursal_list = connection.execute(text("select sucursal_ID from Empleados where cedula=:cedula"),cedula=cedula).fetchall()
            sucursal = sucursal_list[0][0]
            print(sucursal)
            connection.execute(text("EXEC bono_facturador @opcion=1,@empleado_cedula=:cedula,@sucursal_ID=:sucursal,@fecha_comparar=:fecha1,@fecha_bono=:fecha2"),cedula=cedula,sucursal=sucursal,fecha1=fecha1,fecha2=fecha2).fetchall()
            return render_template("pagar_salario.html")
        except exc.SQLAlchemyError as e:
            print(e.__cause__)
            flash('Este empleado no ha facturado 1000 productos en la semana dada.', category='error')
            return render_template("pagar_salario.html")

@views.route('/ingresar_proveedor', methods=['GET','POST'])
def ingresar_proveedor():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')

    if request.method == 'POST':
        correo = request.form.get('email')
        nombre = request.form.get('firstName')
        telefono = int(request.form.get('telefono'))
        ciudad = request.form.get('ciudad')
        porcentaje = float(request.form.get('porcentaje'))
        pais = request.form.get('pais')
        longitud = request.form.get('longitud')
        latitud = request.form.get('latitud')
        print(request.form)

        ubicacion = longitud + " " + latitud
        print(ubicacion)

        if nombre == None or nombre == "" or nombre == " ":
            flash("El nombre no puede estar vacío.",category='error')
        elif(bool(re.match('[a-zA-Z\s]+$', nombre))==False):
            flash("Solo puede usar caracteres de A-Z.",category='error')
        elif ciudad == None or ciudad == "" or ciudad == " ":
            flash("La ciudad no puede estar vacía.",category='error')
        elif(bool(re.match('[a-zA-Z\s]+$', ciudad))==False):
            flash("Solo puede usar caracteres de A-Z.",category='error')
        elif latitud == None or latitud == "" or latitud == " ":
            flash("La latitud no puede estar vacía.",category='error')
        elif longitud == None or longitud == "" or longitud == " ":
            flash("La longitud no puede estar vacía.",category='error')
        else:
            try:
                with sqlcon.begin() as connection:
                    connection.execution_options(isolation_level="AUTOCOMMIT")
                    connection.execute(text("DECLARE @punto geography;"+"SET @punto = geography::STPointFromText('POINT("+ubicacion+")', 4326);"+"EXEC CRUD_proveedor @opcion=1,@nombre=:nombre,@porcentaje=:porcentaje,@correo=:correo,@ciudad=:ciudad,@telefono=:telefono,@ubicacion=@punto,@pais=:pais,@estado_ID=2000"),nombre=nombre,porcentaje=porcentaje,correo=correo,ciudad=ciudad,telefono=telefono,pais=pais)
                    flash('Se ha ingresado un proveedor correctamente!', category='success')
                    products = connection.execute(text("EXEC CRUD_producto @opcion=6,@nombre=null, @descripcion=null, @categoria_ID = null, @tiene_impuesto =null, @minimo =null, @maximo =null,@fecha_produccion=null, @fecha_expiracion=null, @en_descuento=null, @precio=null, @estado_ID=null, @sucursal_ID=null,@cantidad=null,@producto_ID=null,@proveedor_ID=null,@porcentaje_descuento=null")).fetchall()
                    return render_template("home.html",products=products,comprado=False)
            except exc.SQLAlchemyError as e:
                print(e.__cause__)
                flash(e.__cause__, category='error')
                return render_template("ingresar_proveedor.html")


            

    return render_template("ingresar_proveedor.html")

@views.route('/ingresar_sucursal', methods=['GET','POST'])
def ingresar_sucursal():
    sqlcon = db.create_engine('mssql+pyodbc://@' + 'DESKTOP-UIDL72I\ALESQLSERVER' + '/' + 'CostaRica_BD' + '?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server')

    if request.method == 'POST':
        nombre = request.form.get('name')
        cedula = int(request.form.get('cedula-admin'))
        ciudad = request.form.get('distrito')
        horario_inicio = request.form.get('horario_inicio')
        horario_fin = request.form.get('horario_fin')
        pais = request.form.get('pais')
        longitud = request.form.get('longitud')
        latitud = request.form.get('latitud')
        telefono = int(request.form.get('telefono'))
        print(request.form)

        estado_ID = 0
        if pais=='Costa Rica':
            estado_ID = 1
        elif pais=='Guatemala':
            estado_ID = 3000
        elif pais=='Panama':
            estado_ID = 4000
        
        print(estado_ID)

        ubicacion = longitud + " " + latitud
        print(ubicacion)

        if nombre == None or nombre == "" or nombre == " ":
            flash("El nombre no puede estar vacío.",category='error')
        elif(bool(re.match('[a-zA-Z\s]+$', nombre))==False):
            flash("Solo puede usar caracteres de A-Z.",category='error')
        elif ciudad == None or ciudad == "" or ciudad == " ":
            flash("La ciudad no puede estar vacía.",category='error')
        elif(bool(re.match('[a-zA-Z\s]+$', ciudad))==False):
            flash("Solo puede usar caracteres de A-Z.",category='error')
        elif latitud == None or latitud == "" or latitud == " ":
            flash("La latitud no puede estar vacía.",category='error')
        elif longitud == None or longitud == "" or longitud == " ":
            flash("La longitud no puede estar vacía.",category='error')
        else:
            try:
                with sqlcon.begin() as connection:
                    connection.execution_options(isolation_level="AUTOCOMMIT")
                    connection.execute(text("DECLARE @punto geography;"+"SET @punto = geography::STPointFromText('POINT("+ubicacion+")', 4326);"+"EXEC CRUD_sucursal @opcion=1,@nombre=:nombre,@cedula_administrador=:cedula,@horario_inicio=:horario_inicio,@horario_fin=:horario_fin,@ciudad=:ciudad,@telefono=:telefono,@ubicacion=@punto,@pais=:pais,@estado_ID=:estado_ID"),nombre=nombre,cedula=cedula,horario_inicio=horario_inicio,horario_fin=horario_fin,ciudad=ciudad,telefono=telefono,pais=pais,estado_ID=estado_ID)
                    flash('Se ha ingresado una sucursal correctamente!', category='success')
                    products = connection.execute(text("EXEC CRUD_producto @opcion=6,@nombre=null, @descripcion=null, @categoria_ID = null, @tiene_impuesto =null, @minimo =null, @maximo =null,@fecha_produccion=null, @fecha_expiracion=null, @en_descuento=null, @precio=null, @estado_ID=null, @sucursal_ID=null,@cantidad=null,@producto_ID=null,@proveedor_ID=null,@porcentaje_descuento=null")).fetchall()
                    return render_template("home.html",products=products,comprado=False)
            except exc.SQLAlchemyError as e:
                print(e.__cause__)
                flash(e.__cause__, category='error')
                return render_template("ingresar_sucursal.html")


            

    return render_template("ingresar_sucursal.html")