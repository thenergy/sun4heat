# -*- coding: utf-8 -*-
"""
Created on Fri Nov 19 16:28:00 2021

@author: diieg
"""

path = '/home/diegonaranjo/Documentos/Thenergy/sun4heat/'

import pandas as pd

from pyproj import Proj, transform
import warnings
warnings.filterwarnings('ignore')

#path = 'C:/Users/diieg/OneDrive/Documentos/Thenergy/sun4heat/'

def ReadIndus():


    '''
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
        'raz_social', 'nombre', 'ID', 'rubro', 'ciiu4', 'fuente_emision', 
        'tipo_contaminante', 'ton_emision', 'anho', 'region', 'provincia', 
        'comuna', 'huso', 'coord_norte', 'coord_este','Longitud','Latitud'.
        
    '''
    header = ['raz_social','ID','nombre','rubro','ciiu6','ciiu4','region','provincia','comuna','coord_este','coord_norte',
              'huso','fuente_emision','nombre_fuente','tipo_emision','combustible','origen','tipo_contaminante','ton_emision']

    # header = ['Razón Social','ID Establecimiento VU','Nombre Establecimiento','Rubro RETC','CIIU6',
    #           'CIIU4','Región','Provincia','Comuna','Coordenada Este','Coordenada Norte','Huso',
    #           'Fuente','Nombre Fuente','Tipo de Emisión','Combustible','Origen','Contaminante',
    #             'Emisión (Toneladas)']
    
    indus = pd.read_csv(path + 'datos/RETC/ckan_ruea_2019_v1.csv', names=header, encoding="latin-1",skiprows=1,sep=';',decimal=',')
    
    
    indus.ton_emision = pd.to_numeric(indus.ton_emision, errors='coerce')
    indus = indus.dropna()
    
    return indus

def UTM2WGS84(indus):    
    outProj = Proj(init='epsg:4326')
    lt = []
    lg = []
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
        
    indus['Longitud'] = lg
    indus['Latitud'] = lt
    
    return indus
    
    
##########################################################

indus = ReadIndus()
indus = UTM2WGS84(indus)
indus.to_csv(path + 'datos/RETC/indus_ll.csv', encoding="utf-8-sig",sep=';',decimal=',')
#indus_ft.to_excel(path + 'visualizaciones/mapa_emisiones/empresas_filtradas.xlsx', encoding="utf-8-sig")   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    