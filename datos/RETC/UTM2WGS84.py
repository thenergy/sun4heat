# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 16:28:00 2021

@author: diieg
"""

# path = '/home/diegonaranjo/Documentos/Thenergy/sun4heat/'
# path = "/home/ubuntu/Thenergy/diego/sun4heat/" #path ubuntu

import pandas as pd

from pyproj import Proj, transform
import warnings
warnings.filterwarnings('ignore')

#path = 'C:/Users/diieg/OneDrive/Documentos/Thenergy/sun4heat/'
path = '/home/diego/Documentos/sun4heat/'
# def ReadIndus():


#     '''
#     Esta función lee csv 'emisiones_aire_año_cart.csv' y entrega un DF.
    
#     Parameters
#     ----------
#         header
#             Encabezados del DF.
    
#     Returns
#     -------
#     indus: Data Frame
#         DF con los headers expuestos abajo.
    
#     Headers DataFrame
#     -----------------
#         'raz_social', 'nombre', 'ID', 'rubro', 'ciiu4', 'fuente_emision', 
#         'tipo_contaminante', 'ton_emision', 'anho', 'region', 'provincia', 
#         'comuna', 'huso', 'coord_norte', 'coord_este','Longitud','Latitud'.
        
#     '''
#     header = ['ano','ID', 'nombre', 'raz_social', 'ciiu4', 'ciiu6'
#               ,	'rubro', 'region', 'provincia', 'comuna', 'huso',
#               'latitud', 'longitud', 'fuente_emision', 'TIPO DE FUENTE', 'COMBUSTIBLE PRIMARIO', 'CCF8 PRIMARIO',
#               'tipo_contaminante','EMISION PRIMARIO', 'COMBUSTIBLE SECUNDARIO', 'CCF8 SECUNDARIO', 'CONTAMINANTE 2', 'EMISION SECUNDARIO', 
#               'CCF8 MATERIA PRIMA','CONTAMINANTE 3',  'EMISION MATERIA PRIMA', 'ton_emision', 'ORIGEN', 'NIVEL ACTIVIDAD EXTERNO']
    
    
    
#     # indus = pd.read_excel(path + 'datos/RETC/ruea_2020_ckan_final.xlsx', names = header)
#     indus = pd.read_csv(path + "datos/RETC/ruea_2020_ckan_final.csv", encoding="utf-8-sig", sep=';', decimal='.', names = header)
        
#     # indus.ton_emision = pd.to_numeric(indus.ton_emision, errors='coerce')
#     # indus.longitud = pd.to_numeric(indus.coord_este, errors='coerce')
#     # indus.latitud = pd.to_numeric(indus.coord_norte, errors='coerce')
#     # indus.huso = pd.to_numeric(indus.huso, errors='coerce')
       
#     # indus = indus.dropna(subset=(['ton_emision','longitud','latitud','huso']))
#     # indus = indus['coord_este'].dropna()
#     # indus = indus['coord_norte'].dropna()
#     # indus = indus['huso'].dropna()
        
    
        
    
#     return indus

####################################
##  PARA RUEA 2019
####################################

def ReadIndus():
    """
    Función que lee la base de emisiones entregada por el ministerio (variable por trimestre) y entrega un DF para manipular.
    
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
      'raz_social', 'nombre', 'ID', 'rubro', 'ciiu4', 'fuente_emision', 
      'tipo_contaminante', 'ton_emision', 'anho', 'region', 'provincia', 
      'comuna', 'huso', 'coord_norte', 'coord_este','Longitud','Latitud'.
  
    """
    # header = ['raz_social','nombre','ID','rubro','ciiu4','fuente_emision','tipo_contaminante',
    #   'ton_emision','anho','region','provincia','comuna','huso','coord_norte','coord_este','Longitud','Latitud']

    header = ['ID', 'raz_social', 'nombre','rubro','ciiu6','ciiu4','region','provincia',
              'comuna','coord_este','coord_norte', 'huso', 'fuente_emision', 'tipo_fuente','combustible_prim', 
              'EMISION PRIMARIO', 'combustible_sec','EMISION SECUNDARIO','EMISION MATERIA PRIMA','tipo_contaminante',
              'ton_emision','ORIGEN']
    
    indus = pd.read_excel(path + 'datos/RETC/2019_vfinal_v3.xlsx', names=header, skiprows=1)


    indus.ton_emision = pd.to_numeric(indus.ton_emision, errors="coerce")
    # indus = indus.dropna()  
    # indus.ccf8 = pd.to_numeric(indus.ccf8, errors="coerce")

    indus.coord_norte = pd.to_numeric(indus.coord_norte, errors="coerce")
    indus.coord_este = pd.to_numeric(indus.coord_este, errors="coerce")
    indus.huso = pd.to_numeric(indus.huso, errors="coerce")

    indus.huso = pd.to_numeric(indus.huso, errors='coerce')
    
    indus = indus.dropna(subset=(["ton_emision", "coord_este", "coord_norte",'tipo_fuente','huso']))
    
    indus.coord_este.astype(float)
    indus.coord_norte.astype(float)

    # indus = indus['longitud'].dropna()
    # indus = indus['latitud'].dropna()
    # indus = indus['huso'].dropna()



    return indus


def UTM2WGS84(indus):    
    outProj = Proj(init='epsg:4326')
    lt = []
    lg = []
    i = 1
    for coord_este, coord_norte, huso in zip(indus.coord_este, indus.coord_norte, indus.huso):
        
        if huso == 18:
            inProj = Proj(init='epsg:32718')
        elif huso == 19:
            inProj = Proj(init='epsg:32719')
        else:
            pass
    
        x2,y2 = transform(inProj,outProj,coord_este,coord_norte)
        lg.append(x2)
        lt.append(y2)
        i = i+1
        print(i)
        
    indus['Longitud'] = lg
    indus['Latitud'] = lt
    
    return indus
    
    
# ##########################################################

indus = ReadIndus()
indus = UTM2WGS84(indus)
indus.to_csv(path + 'datos/RETC/indus_ll.csv', encoding="utf-8-sig",sep=';',decimal='.', index = False)

# indus.to_excel(path + 'datos/RETC/indus_ll.xlsx', index = False)

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    