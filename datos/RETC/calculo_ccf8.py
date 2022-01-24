#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 01:47:30 2022

@author: diegonaranjo
"""

import numpy as np
import pandas as pd

path = '/home/diegonaranjo/Documentos/Thenergy/sun4heat/'



def ReadIndus():
    """
    Esta función lee csv 'emisiones_aire_año_cart.csv' y entrega un DF.
    
    Parameters
    ----------
        header
            Encabezados del DF.
    
    Returns
    -------
    indus: Data Frame
        DF con los headers expuestos abajo.
    
    Headers DataFrame 
    -----------------
  'ano','ID', 'nombre', 'raz_social', 'ciiu4', 'ciiu6'
            ,	'rubro', 'region', 'provincia', 'comuna', 'huso',
            'Latitud', 'Longitud', 'fuente_emision', 'tipo_fuente, 'combustible_prim', 'ccf8',
            'tipo_contaminante','EMISION PRIMARIO', 'combustible_sec', 'CCF8 SECUNDARIO', 'CONTAMINANTE 2', 'EMISION SECUNDARIO', 
            'CCF8 MATERIA PRIMA','CONTAMINANTE 3',  'EMISION MATERIA PRIMA', 'ton_emision', 'ORIGEN', 'NIVEL ACTIVIDAD EXTERNO'
        
    """
    header = ['ano','ID', 'nombre', 'raz_social', 'ciiu4', 'ciiu6'
              ,	'rubro', 'region', 'provincia', 'comuna', 'huso',
              'Latitud', 'Longitud', 'fuente_emision', 'tipo_fuente', 'combustible_prim', 'ccf8',
              'tipo_contaminante','EMISION PRIMARIO', 'combustible_sec', 'CCF8 SECUNDARIO', 'CONTAMINANTE 2', 'EMISION SECUNDARIO', 
              'CCF8 MATERIA PRIMA','CONTAMINANTE 3',  'EMISION MATERIA PRIMA', 'ton_emision', 'ORIGEN', 'NIVEL ACTIVIDAD EXTERNO']
    
    

    indus = pd.read_csv(path + "datos/RETC/ruea_2020_ckan_final.csv", sep =';', decimal=',', thousands= '.', encoding = 'utf-8-sig', names = header)

      
    indus = indus.drop(0, axis=0)
    

    
    indus = indus.drop(['ano', 'CCF8 SECUNDARIO', 'CONTAMINANTE 2', 'EMISION SECUNDARIO', 
    'CCF8 MATERIA PRIMA','CONTAMINANTE 3', 'ORIGEN', 'NIVEL ACTIVIDAD EXTERNO' ], axis = 1)
    
    
    #Se necesita reemplazar los puntos por nada, y las comas por puntos (ya que los decimales en python son con puntos.)
    indus['ton_emision'] = indus['ton_emision'].str.replace(".", '')
    indus['ton_emision'] = indus['ton_emision'].str.replace(",", '.')
    
    indus['Latitud'] = indus['Latitud'].str.replace(",", '.')
    indus['Longitud'] = indus['Longitud'].str.replace(",", '.')



    indus.ton_emision = pd.to_numeric(indus.ton_emision, errors='coerce')
    # indus.ccf8.str.replace('.','')

    indus.ccf8 = pd.to_numeric(indus.ccf8, errors='coerce')
    

    indus.Longitud = pd.to_numeric(indus.Longitud, errors='coerce')
    indus.Latitud = pd.to_numeric(indus.Latitud, errors='coerce')

    indus = indus.dropna(subset=(['ton_emision','Longitud','Latitud']))
    # indus = indus['longitud'].dropna()
    # indus = indus['latitud'].dropna()
    # indus = indus['huso'].dropna()


    # indus.huso = pd.to_numeric(indus.huso, errors='coerce')
       

        
    return indus

def readccf8():
    
    
    header = ['ccf8', 'ener_emis']
    base = pd.read_csv(path + "datos/RETC/ccf8.csv",sep = ';', encoding = 'utf-8-sig', names = header)#dtype ={'ccf8':str,'ener_emis':np.float64})
    
    base = base.drop([0,1], axis=0)

    
    base['ccf8'] = base['ccf8'].str.replace("-", '')
    base['ener_emis'] = base['ener_emis'].str.replace(",", '.')
    
    base['ccf8'] = pd.to_numeric(base['ccf8'], errors = "coerce")
    base['ener_emis']= pd.to_numeric(base['ener_emis'], errors = "coerce")
    

    return base



def emission_to_energy(df,df2):
    for i in df.ccf8:
        for j in df2.ccf8:
            if i == j :
                df['ener_cons_CO2'] = df.ton_emision/df2.ener_emis
    
    return df


indus = ReadIndus()
base = readccf8()

indus = emission_to_energy(indus, base)

indus.to_csv(path + 'datos/RETC/indus_ll.csv', encoding="utf-8-sig",sep=';',decimal=',', index = False)















