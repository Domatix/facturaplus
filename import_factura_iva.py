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
account_iva = origen.model(name='account.account').browse([('code','=','477000')])[0]
tax_id = origen.model(name='account.tax').browse([('description','=','S_IVA21B')])[0]

def importar():
    dbf = ydbf.open(os.path.join('dbf', 'Facclib.dbf'), encoding='latin-1')
    for row in dbf:

        # BÚSQUEDA DE CABECERAS DE FACTURAS
        invoice_obj = origen.model('account.invoice')
        invoice_id =  invoice_obj.browse([('name','=',str(row['NNUMFAC']))])[0]

        if bool(float(row['NIVA'])):
            invoice_iva_vals = {
                        'invoice_id': invoice_id.id,
                        'amount': float(row['NIMPIVA']),
                        'tax_id':tax_id.id,
                        'name':tax_id.name,
                        'account_id': account_iva.id

            }
            invoice_tax_obj = origen.model('account.invoice.tax')
            invoice_tax_id = invoice_tax_obj.create(invoice_iva_vals)

importar()
