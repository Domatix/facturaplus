# Facturaplus

Importación de datos de Facturaplus a Odoo.

### Requisitos iniciales

* Se ha utilizado Ubuntu 16.04 / 18.04 y python2 para ejecutar el script.
* Instalar ydbf: [ydbf](https://github.com/y10h/ydbf/blob/master/setup.py)
* Instalar erppeek: `pip install erppeek`
* Crear una carpeta llamada **dbf** en el lugar donde se vayan a ejecutar los scripts y dejar dentro los .dbf de facturaplus

### Datos que se importarán a Odoo

Los datos que importa el script **import_product** son los siguientes:
#### Articulo.dbf
* Nombre de producto
* Tipo de producto

Los datos que importa el script **import_factura** son los siguientes:
#### FacCliT.dbf
* Clientes de la factura (Nombre, dirección y NIF)
* Cabecera de las facturas

Los datos que importa el script **import_factura_linea** son los siguientes:
#### FacCliL.dbf
* Líneas de la factura a la que pertenece(Producto, descripción, precio unitario, subtotal, IVA, cantidad, descuento,origen)


### Ejecución de scripts

```
#-*- coding: utf-8 -*-
import ydbf
import sys
import erppeek
import csv
import datetime
import requests
import os.path
import vatnumber

SERVER_origen = 'http://localhost:8069'
DATABASE_origen = 'base_de_datos'
USERNAME = 'username'
PASSWORD = 'password'

debug = True

# Conectar al ERP
origen = erppeek.Client(SERVER_origen, DATABASE_origen, USERNAME, PASSWORD)
```
Es necesario cambiar las variables **SERVER_origen**, **DATABASE_origen**, **USERNAME** y **PASSWORD** para que coincidan con nuestra configuración de Odoo. 
* SERVER_origen: Dirección de la instancia de Odoo que tenemos ejecutándose.
* DATABASE_origen: Nombre de la base de datos donde se va a ejecutar la migración de datos.
* USERNAME: Usuario con el que se va a conectar a Odoo (por ejemplo admin).
* PASSWORD: Contraseña del usuario con el que se va a conectar a Odoo.

Una vez guardados los cambios en los dos ficheros, los ejecutaremos en este orden mediante la siguiente línea de comando:
* `python import_product.py`
* `python import_factura.py`
* `python import_factura_linea.py`
