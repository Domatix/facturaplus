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
customerAccount = origen.model(name='account.account').browse([('code','=','430000')])[0]


def getLetraDNI(dni):
    NIF='TRWAGMYFPDXBNJZSQVHLCKE'
    if type(dni) == str or type(dni) == unicode:
        dni = int(dni)
    return NIF[dni%23]


def decodeCIF(originalCIF):
    if len(originalCIF):
        # Quitar guiones, puntos y espacios
        decodedCIF = originalCIF.replace("-", "").replace(".", "").replace(" ", "")
        if decodedCIF[0].isdigit():
            # Es una persona física
            if decodedCIF[-1].isdigit():
                decodedCIF += getLetraDNI(decodedCIF) # Letra de control
            if len(decodedCIF) < 9:
                decodedCIF = "0" + decodedCIF # Añadir un 0 delante
        # Ver si lleva ya el prefijo de dos letras del país delante del código
        if decodedCIF[0:2].isalpha():
            return decodedCIF.upper()
        if not decodedCIF.startswith('ES'):
            decodedCIF = "ES" + decodedCIF
        return decodedCIF.upper()
    else:
        return originalCIF

def importar():
    dbf = ydbf.open(os.path.join('dbfs', 'FacCliT.dbf'), encoding='latin-1')
    for row in dbf:

        # COMPROBAR SI ESTA EL CLIENTE

        partner_obj = origen.model(name='res.partner')
        partner_id = partner_obj.browse([('name','=',row['CNOMCLI'].strip())])
        if partner_id:
            partner_id[0].ref = row['CCODCLI'].strip()
            if not partner_id[0].customer:
                partner_id[0].customer = True
            partner_id = partner_id[0].id

        # partner_id = partner_obj.search([('ref','=',row['CCODCLI'].strip())])

        else:

            country_obj = origen.model('res.country')
            country_id = country_obj.browse([('name','ilike',row['CNACCLI'])])

            if country_id:
                country_id = country_id[0].id

            else:
                country_id = False

            #CREACION DE CLIENTES SI NO ESTÁN

            partner = {
                'name': row['CNOMCLI'].strip(),
                'ref':row['CCODCLI'].strip(),
                'vat': decodeCIF(row['CDNICIF']),
                'supplier': False,
                'customer': True,
                'opt_out': True,
                'street': row['CDIRCLI'].strip(),
                'zip': row['CPTLCLI'].strip(),
                'city': row['CPOBCLI'],
                'country_id': country_id,
                # 'company_id': company_id.id

            }

            if not vatnumber.check_vat(partner['vat']):
                partner['vat'] = False

            partner = partner_obj.create(partner)
            partner_id = partner.id

        invoice_obj = origen.model('account.invoice')
        #CREACION DE FACTURAS RECTIFICATIVAS
        if 'Abono' in row['COBSERV']:
            invoice_rect_vals = {
                    'name': str(row['CSERIE']) + '0' + str(row['NNUMFAC']),
                    # 'account_id': invoice_id[0].account_id.id,
                    'partner_id': partner_id,
                    'date_invoice': row['DFECFAC'].strftime("%Y-%m-%d"),
                    'type': 'out_refund',
                    # 'company_id': company_id.id
            }
            invoice_obj.create(invoice_rect_vals)
        else:
            #CREACION DE FACTURAS

            invoice_vals = {
                'name': str(row['CSERIE']) + '0' + str(row['NNUMFAC']),
                # 'account_id': customerAccount.id,
                'partner_id': partner_id,
                'date_invoice': row['DFECFAC'].strftime("%Y-%m-%d"),
                'type': 'out_invoice',
                # 'company_id': company_id.id


            }
            invoice_obj.create(invoice_vals)



importar()
