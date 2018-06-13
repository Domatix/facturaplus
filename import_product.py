#-*- coding: utf-8 -*-
import ydbf
import sys
import erppeek
import csv
import datetime
import requests
import os.path

SERVER_origen = 'http://localhost:8069'
DATABASE_origen = 'base_de_datos'
USERNAME = 'usuario'
PASSWORD = 'contraseña'

debug = True

# Conectar al ERP
origen = erppeek.Client(SERVER_origen, DATABASE_origen, USERNAME, PASSWORD)


def importar():
    dbf = ydbf.open(os.path.join('dbf', 'Articulo.dbf'), encoding='latin-1')
    for row in dbf:

        product = {
            'name': row['CDETALLE'],
            'default_code': row['CREF'],
            'lst_price': float(row['NPVP']),
            'type': 'product'
        }

        product_obj = origen.model(name='product.product')
        product = product_obj.create(product)


importar()
