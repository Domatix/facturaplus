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
USERNAME = 'usuario'
PASSWORD = 'contraseña'

debug = True


# Conectar al ERP
origen = erppeek.Client(SERVER_origen, DATABASE_origen, USERNAME, PASSWORD)
VentasAccount = origen.model(name='account.account').browse([('code','=','700000')])[0]
iva21b = origen.model(name='account.tax').browse([('description','=','S_IVA21B')])[0]

def importar():
    dbf = ydbf.open(os.path.join('dbfs', 'FacCliL.dbf'), encoding='latin-1')
    for row in dbf:

        product_obj = origen.model('product.product')
        product_id = product_obj.browse([('default_code','=',row['CREF'].strip())])
        if product_id:
            product_id = product_id[0].id
        else:
            product_id = product_obj.browse([('default_code','=','Facturaplus')])
            if not product_id:
                product = {
                    'name': 'Producto',
                    'default_code': 'Facturaplus',
                    'type': 'product',
                }
                product_id = product_obj.create(product)
            else:
                product_id = product_id[0].id
        # BÚSQUEDA DE CABECERAS DE FACTURAS
        invoice_obj = origen.model('account.invoice')
        invoice_id = invoice_obj.browse([('name','=',str(row['CSERIE']) + '0' + str(row['NNUMFAC']))])

        if invoice_id:
            invoice_id = invoice_id[0]

        # CREACION DE LINEAS DE FACTURA

        invoice_vals = {
            'name': row['CDETALLE'].strip(),
            'invoice_id': invoice_id.id,
            'product_id': product_id,
            'quantity': float(row['NCANENT']),
            'discount': float(row['NDTO']),
            'account_id': VentasAccount.id,
            'invoice_line_tax_ids': [(4,iva21b.id)] if bool(float(row['NIVA'])) else False,
            'price_unit':float(row['NPREUNIT']),
            'price_subtotal':float(row['NTOTLINEA']),
            'origin': str(row['NNUMFAC']),
            'facturaplus': True,

        }

        invoice_line_obj = origen.model('account.invoice.line')
        invoice_line_id = invoice_line_obj.create(invoice_vals)
        invoice_id.compute_taxes()



importar()
