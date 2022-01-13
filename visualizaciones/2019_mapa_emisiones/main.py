# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 13:41:53 2021

@author: diieg
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 20 08:11:42 2020

@author: fcuevas
"""
# import time

import numpy as np
import pandas as pd




## librerías de Bokeh
from bokeh.plotting import Figure

# from pyproj import Proj, transform

from bokeh.models import (
    ColumnDataSource,
    TableColumn,
    DataTable,
    TextInput,
    Select,
    NumberFormatter,
    Range1d,
    HoverTool,
    TileRenderer,
    MultiChoice,
    CustomJS,
)
from bokeh.io import curdoc
from bokeh.layouts import column, row, Spacer
from bokeh.models.widgets import Button

from bokeh.palettes import Category20

# mapas disponibles en Bokeh
from bokeh.tile_providers import (
    get_provider,
    CARTODBPOSITRON,
    CARTODBPOSITRON_RETINA,
    STAMEN_TERRAIN,
    STAMEN_TERRAIN_RETINA,
    STAMEN_TONER,
    STAMEN_TONER_BACKGROUND,
    STAMEN_TONER_LABELS,
    OSM,
    WIKIMEDIA,
    ESRI_IMAGERY,
)

#Libreria para descargar csv boton
from os.path import dirname, join
# Donde instalar. Versión local y versión en servidor
# <<<<<<< HEAD
path = "/home/ubuntu/Thenergy/diego/sun4heat/"
# path = '/home/diegonaranjo/Documentos/Thenergy/sun4heat/'
# =======
# <<<<<<< HEAD
# path = '/mnt/c/Users/diieg/OneDrive/Documentos/Thenergy/prueba/'
# path = 'C:/Users/diieg/OneDrive/Documentos/Thenergy/prueba/'
# =======
# path = '/mnt/c/Users/diieg/OneDrive/Documentos/Thenergy/sun4heat/'
# path = '/home/diegonaranjo/Documentos/Thenergy/sun4heat/'
# >>>>>>> 350a39b9ca7a3f4b215e4f8551be09387d69b24d
# >>>>>>> main
# path = '/home/ubuntu/sun4heat/'
# path = '/Users/fcuevas/Documents/Trabajo/thenergy/test_repo/sun4heat/'

# Lista con nombre de los "tiles"
tiles = [
    "CARTODBPOSITRON",
    "CARTODBPOSITRON_RETINA",
    "STAMEN_TERRAIN",
    "STAMEN_TERRAIN_RETINA",
    "STAMEN_TONER",
    "STAMEN_TONER_BACKGROUND",
    "STAMEN_TONER_LABELS",
    "OSM",
    "WIKIMEDIA",
    "ESRI_IMAGERY",
]


cats = {
    'Otras actividades':1,
     'Comercio minorista':2,
     'Captación, tratamiento y distribución de agua':3,
     'Otras industrias manufactureras':4,
     'Pesca y acuicultura':5,
     'Plantas de tratamiento de aguas servidas':6,
     'Comercio mayorista':7,
     'Producción agropecuaria':8,
     'Ventas y mantención de vehículos automotores':9,
     'Construcción':10,
     'Minería':11,
     'Termoeléctricas':12,
     'Otras centrales de generación eléctrica':13,
     'Industria del papel y celulosa':14,
     'Industria química, de plástico y caucho':15,
     'Industria de la madera y silvicultura':16,
     'Refinería de petróleo':17,
     'Gestores de residuos':18,
     'Producción de cemento, cal y yeso':19,        
}


combs_1 = {
    'Carbón Bituminoso Pulverizado':1,
     'Gas Natural':2,
     'Gas de Coque':3,
     'Carbón Sub Bituminoso':4,
     'Licor Negro':5,
     'Gas de Coque Diluido':6,
     'Gas Licuado de Petróleo':7,
     'Gas de Alto Horno':8,
     'Carbón Coke':9,
     'Coke de Petróleo (Petcoke)':10,
     'Biomasa Combustible':11,
     'Petróleo N 6':12,
     'Carbón Bituminoso':13,
     'Gas de Refinería':14,
     'Aserrín':15,
     'Viruta, Despuntes':16,
     'Petróleo N 2 (Diesel)':17,
     'Leña':18,
     'Gas de Cañería':19,
     'Petróleo N 5':20
     }

combs_2 = {
     'Kerosene':1,
     'Metanol':2,
     'Propano':3,
     'Aceite Usado':4,
     'Carbón de Leña':5,
     'Bencina':6,
     'Biogas':7
    }


# paleta de colores para los gráficos
clr = dict(zip(cats, Category20[20]))

# paleta de colores para los combustibles
# clr_combs = {}
# clr_combs1 = dict(zip(combs_1, Category20[20]))
# clr_combs2 = dict(zip(combs_2,Category20[7]))

# clr_combs.update(clr_combs1)
# clr_combs.update(clr_combs2)


# leer archivo "ckan_ruea_2019_v1"
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
            'Latitud', 'Longitud', 'fuente_emision', 'tipo_fuente, 'combustible_prim', 'CCF8 PRIMARIO',
            'tipo_contaminante','EMISION PRIMARIO', 'combustible_sec', 'CCF8 SECUNDARIO', 'CONTAMINANTE 2', 'EMISION SECUNDARIO', 
            'CCF8 MATERIA PRIMA','CONTAMINANTE 3',  'EMISION MATERIA PRIMA', 'ton_emision', 'ORIGEN', 'NIVEL ACTIVIDAD EXTERNO'
        
    """
    header = ['ano','ID', 'nombre', 'raz_social', 'ciiu4', 'ciiu6'
              ,	'rubro', 'region', 'provincia', 'comuna', 'huso',
              'Latitud', 'Longitud', 'fuente_emision', 'tipo_fuente', 'combustible_prim', 'CCF8 PRIMARIO',
              'tipo_contaminante','EMISION PRIMARIO', 'combustible_sec', 'CCF8 SECUNDARIO', 'CONTAMINANTE 2', 'EMISION SECUNDARIO', 
              'CCF8 MATERIA PRIMA','CONTAMINANTE 3',  'EMISION MATERIA PRIMA', 'ton_emision', 'ORIGEN', 'NIVEL ACTIVIDAD EXTERNO']
    
    

    indus = pd.read_csv(path + "datos/RETC/ruea_2020_ckan_final.csv", sep =';', decimal=',', thousands= '.', encoding = 'utf-8-sig', names = header)

      
    indus = indus.drop(0, axis=0)
    

    
    indus = indus.drop(['ano','CCF8 PRIMARIO', 'CCF8 SECUNDARIO', 'CONTAMINANTE 2', 'EMISION SECUNDARIO', 
    'CCF8 MATERIA PRIMA','CONTAMINANTE 3', 'ORIGEN', 'NIVEL ACTIVIDAD EXTERNO' ], axis = 1)
    
    
    #Se necesita reemplazar los puntos por nada, y las comas por puntos (ya que los decimales en python son con puntos.)
    indus['ton_emision'] = indus['ton_emision'].str.replace(".", '')
    indus['ton_emision'] = indus['ton_emision'].str.replace(",", '.')
    
    indus['Latitud'] = indus['Latitud'].str.replace(",", '.')
    indus['Longitud'] = indus['Longitud'].str.replace(",", '.')



    indus.ton_emision = pd.to_numeric(indus.ton_emision, errors='coerce')
    indus.Longitud = pd.to_numeric(indus.Longitud, errors='coerce')
    indus.Latitud = pd.to_numeric(indus.Latitud, errors='coerce')

    indus = indus.dropna(subset=(['ton_emision','Longitud','Latitud']))
    # indus = indus['longitud'].dropna()
    # indus = indus['latitud'].dropna()
    # indus = indus['huso'].dropna()


    # indus.huso = pd.to_numeric(indus.huso, errors='coerce')
       

        
    return indus


def IDequipo(df):
    """
    Esta función extrae las dos primeras letras de la columna fuente_emisión del 
    DF proveniente del CSV emisiones_aire_año (función ReadIndus).

    Parameters
    ----------
    df : Data Frame
        Se entrega el DataFrame del CSV emisiones_aire_año.

    Returns
    -------
    df : Mismo DF del parámetro pero con nueva columna el cual 
        representa el equipo utilizado (primeras dos letras de la fuente).

    """
    clds = []
    for cld in df.fuente_emision:
        clds.append(cld[0:2])
    df["equipo"] = clds

    return df


# filtrar según el equipo o mercado a analizar
def FiltEquip(df, mkt):
    """
    Función que filtra los equipos del mercado según la DF entregada (emisiones_aire_año_cart.csv).
    
    Equipos / Mercado
    -----------------
    ACTUALIZAR EQUIPOS!!!
        Caldera Calefacción ('CA')
        Caldera Industrial ('IN')
        Mercado Solar ('IN', 'CF', 'CA')
        Mercado H2 ('IN','CF','CA','PC','PS')
        Generación Eléctrica ('GE')
        Todo ('CA', 'IN', 'PC', 'CF', 'PS', 'GE')
        


    Parameters
    ----------
    df : DataFrame
        Corresponde al DF de emisiones.
    mkt : String
        Corresponde al equipo o mercado a analizar.

    Returns
    -------
    df : Data Frame
        DF con los filtros aplicados.

    """

    if mkt == "Antorcha":
        eqp_ft = ["AN"]
        
    elif mkt == "Caldera de Fluido Térmico":
        eqp_ft = ["CF"]
        
    elif mkt == "Caldera de Generación Eléctrica":
        eqp_ft = ["CG"]
        
    elif mkt == "Calentador":
        eqp_ft = ["CL"]
        
    elif mkt == "Caldera Recuperadora":
        eqp_ft = ["CR"]      

    elif mkt == "Convertidor Teniente (CT)":
        eqp_ft = ["CV"]   
        
    elif mkt == "Convertidor Pierce Smith (CPS)":
        eqp_ft = ["CV"]

    elif mkt == "Caldera Calefacción (CA)":
        eqp_ft = ["CA"]
        
    elif mkt == "Grupo Electrógeno":
        eqp_ft = ["EL"]
         
    elif mkt == "Horno de Panadería":
        eqp_ft = ["HR"]
        
    elif mkt == "Incinerador":
        eqp_ft = ["IC", "MO"]
        
    elif mkt == "Molino de Rodillo":
        eqp_ft = ["MC"]

    elif mkt == "Marmita de Calcinación":
        eqp_ft = ["MC", "MO"]

    elif mkt == "Caldera Industrial (IN)":
        eqp_ft = ["IN"]
        
    elif mkt == "Motor Generación Eléctrica":
        eqp_ft = ["MG"]
        
    elif mkt == "Turbina de Gas":
        eqp_ft = ["TG"]
        
    elif mkt == "Regenerador Cracking Catalítico (FCCU)":
        eqp_ft = ["RG"]
        
    elif mkt == "Secadores":
        eqp_ft = ["SC"]

    elif mkt == "Mercado Solar":
        eqp_ft = ["IN", "CF", "CA"]

    elif mkt == "Mercado H2":
        eqp_ft = ["IN", "CF", "CA", "PC", "PS"]

    elif mkt == "Todo":
        eqp_ft = ['CG',
         'EL',
         'AN',
         'IN',
         'PS',
         'TG',
         'HR',
         'CA',
         'RG',
         'CF',
         'MG',
         'MC',
         'SC',
         'CV',
         'IC',
         'MO',
         'CL',
         'CR']

    df = df[df.equipo.isin(eqp_ft)]

    return df


# agrupar
def IndusFilt(df, min_ton, max_ton):
    """
    Función que filtra el DF entregado (emisiones_aire_año_cart.csv) según un rango de toneladas (min_ton, max_ton). 
    También agrupa según el ID, sumando las columnas de ton_emision y n_equip, agregando columna de max_emision (conjunto de empresas).
    
    Parameters
    ----------
    df : DataFrame
        DF de industrias.
    min_ton : Float
        Cantidad mínima de toneladas de emisiones a filtrar.
    max_ton : Float
        Cantidad máxima de toneladas de emisiones a filtrar.

    Returns
    -------
    df : DataFrame
        Nueva agrupación de datos por ID y sumando ton_emision y n_equip
        

    """
    df["n_equip"] = 1
    df = df.sort_values("ton_emision", ascending=False).drop_duplicates(
        "fuente_emision"
    )

    indus_gr = df.groupby(["ID"]).agg(
        {
            "ton_emision": "sum",
            "ener_cons_Co2":"sum",
            "n_equip": "sum",
            "raz_social": "first",
            "nombre": "first",
            "rubro": "first",
            "ciiu4": "first",
            "region": "first",
            "provincia": "first",
            "comuna": "first",
            "combustible_prim": "first",
            "combustible_sec":"first",
            "fuente_emision":"first",   
            "tipo_contaminante":"first",
            "huso": "first",
            "Latitud": "first",
            "Longitud": "first",
        }
    )

    indus_max = df.groupby(["ID"])["ton_emision"].max()
    indus_gr["max_emision"] = indus_max

    df = indus_gr
    df["orden"] = 1

    if max_ton > min_ton:
        df = df[(df.ton_emision > min_ton) & (df.ton_emision < max_ton)]

    else:
        df = df[df.ton_emision > min_ton]

    return df


# filtrar por categorias
def Filtrbr(df, rbr, max_empr):
    """
    Función que filtra según las categorias presentes en 'emisiones_aire_año_cart.csv'.
    
    Categorias
    ----------
            'Otras actividades',
             'Comercio minorista',
             'Captación, tratamiento y distribución de agua',
             'Otras industrias manufactureras',
             'Pesca y acuicultura',
             'Plantas de tratamiento de aguas servidas',
             'Comercio mayorista',
             'Producción agropecuaria',
             'Ventas y mantención de vehículos automotores',
             'Construcción',
             'Minería',
             'Termoeléctricas',
             'Otras centrales de generación eléctrica',
             'Industria del papel y celulosa',
             'Industria química, de plástico y caucho',
             'Industria de la madera y silvicultura',
             'Refinería de petróleo',
             'Gestores de residuos',
             'Producción de cemento, cal y yeso'

    Parameters
    ----------
    df : DataFrame
        DF en donde se filtra la categoría correspondiente.
    rbr : List
        Lista de strings que contiene las categorías a filtrar.
    max_empr : int
        Por ahora ninguna función.

    Returns
    -------
    df : DataFrame
        DF con la categoría filtrada.

    """
    
    # if catg == "rubro":
    if rbr == ["Todo"]:
        rbr = list(indus.rubro.unique())

    else:
        pass
    
    df["rbr"] = df.rubro.map(cats)
    df = df[df.rubro.isin(rbr)]
            
    # else :
    #     if rbr == ["Todo"]:
    #         rbr = list(indus.combustible_prim.unique())
    #         rbr.remove("Null")
    #         rbr.remove(rbr[8])
    #         df["rbr"] = df.combustible_prim.map(clr_combs)
    #         df = df[df.combustible_prim.isin(rbr)]
    #     else:
    #         df["rbr"] = df.rubro.map(cats)
    #         df = df[df.rubro.isin(rbr)]
    #         df["rbr"] = df.rubro.map(clr_combs)
    #         df = df[df.rubro.isin(rbr)]

   
    return df
    


# filtrar por region
def FiltRegion(df, rgn, latNor, latSur):
    """
    Función que filtra por región o según rango de latitud.

    Parameters
    ----------
    df : DataFrame
        Base de datos 'emisiones_aire_año_cart.csv'.
    rgn : string
        Region a filtrar.
    latNor : float
        Latitud norte.
    latSur : float
        Latitud sur.

    Returns
    -------
    df_filt : DataFrame.
        DF con el filtro de región/latitud realizados.       
    """

    if rgn == "Todas":
        df_filt = df
    elif rgn == "Rango latitud":
        df_filt = df[(df.Latitud < latNor) & (df.Latitud > latSur)]
    else:
        df_filt = df[df.region == rgn]

    return df_filt


# # Convertir UTM a wgs84
# def convert_UTM_to_WGS84(coord_este, coord_norte, huso):
#     outProj = Proj(init='epsg:4326')
#     lt = []
#     lg = []
#     for coord_este, coord_norte, huso in zip(indus.coord_este, indus.coord_norte, indus.huso):
#         if huso == 18:
#             inProj = Proj(init='epsg:32718')
#         elif huso == 19:
#             inProj = Proj(init='epsg:32719')
#         elif huso == 12:
#             inProj = Proj(init='epsg:32712')

#         x2,y2 = transform(inProj,outProj,coord_este,coord_norte)
#         lg.append(x2)
#         lt.append(y2)

#     indus['Longitud'] = lg
#     indus['Latitud'] = lt

# conversion de escala de latitud y longitud
def wgs84_to_web_mercator(df, lon="Longitud", lat="Latitud"):
    """
    Función que convierte las escalas de longitud en una variable 'x' y latitud
    en una variable 'y', generando nuevas columnas 'x' 'y' en el DF entregado.

    Parameters
    ----------
    df : DataFrame
        DF en el que se generará las variables 'x', 'y' ('emisiones_aire_año_cart.csv').
    lon : Column
        Pertenece a la columna "Longitud" del DF.
    lat : Column
        Pertenece a la columna "Latitud" del DF.

    Returns
    -------
    df : DataFrame
        DF con las nuevas columnas 'x', 'y' generadas.

    """
    k = 6378137
    df["x"] = df[lon] * (k * np.pi / 180.0)
    df["y"] = np.log(np.tan((90 + df[lat]) * np.pi / 360.0)) * k

    return df

def emission_to_energy(df):
    
    fc_CO2_GE_GN = 56.10 #ton/TJ
    fc_CO2_GE_DS = 74.10
    
    df.loc[(df.equipo == 'EL') & (df.combustible_prim == 'Gas Natural'), 'ener_cons_Co2'] = df.ton_emision/(fc_CO2_GE_GN*3600*4*365)*10**9
    df.loc[(df.equipo == 'EL') & (df.combustible_prim == 'Petróleo N 2 (Diesel)'), 'ener_cons_Co2'] = df.ton_emision/(fc_CO2_GE_DS*3600*4*365)*10**9

    df.loc[df.equipo != 'EL', 'ener_cons_Co2'] = np.nan
    
    return df


# ########################################################################################
# crear dataframe (df) indus
indus = ReadIndus()

# crear lista de combustibles
comb_list = list(indus.combustible_prim.unique())
comb_list.remove("Null")
comb_list.remove(comb_list[8])
comb_list.sort()
comb_list= ["Todo"] + comb_list


# crear lista de contaminantes
ctms = list(indus.tipo_contaminante.unique())  # saca uno de cada contaminante
ctms.sort()
ctms_opt = ["Todo"] + ctms

ctm = "Carbon dioxide"
indus = indus[indus.tipo_contaminante == ctm]

#definición factor emisión/energía para grupo electrogenos


# definir contaminante inicial a analizar y filtrar df indus
comb = ['Todo']

if comb == ['Todo']:
    pass
else:
   indus = indus[indus.combustible_prim.isin(comb)]

# filtrar df indus según equipo a analizar
indus = IDequipo(indus) # IDequipo: quita primeras dos letra de columna y las pone en columna "equipo"

#convierte emisiones a factor energético
indus = emission_to_energy(indus)


# lista de equipos a analizar
# eqp_ft = ["CA", "IN", "PC", "CF", "PS", "GE"]
# indus = indus[indus.equipo.isin(eqp_ft)]  # cruzar eqp_ft con indus.equipo

mkt = "Todo"
indus_tmp = FiltEquip(indus, mkt)  # deja unicamente los equipos del mercado a analizar

# definir el mínimo de emisiones a analizar en las empresas
min_ton = 1000
max_ton = 0
indus_ft = IndusFilt(indus_tmp, min_ton, max_ton)  # agrupa por ID  (suma toneladas y n° de equipos que tiene)

# definir máximo de empresas a analizar
max_empr = 1000

# definir categoría
rbr = ["Todo"]
catg = ["rubro"]
indus_ft = Filtrbr(indus_ft, rbr, max_empr)  # Cruza la base agrupada con la categoría de actividad

# convertir latitud y longitud
indus_ft = wgs84_to_web_mercator(indus_ft, lon="Longitud", lat="Latitud")  # crea plano columnas (x,y) en función de lat y long

# definir tamaño y color del marcador en el mapa
pt_size = np.log(indus_ft.ton_emision)
indus_ft["pt_size"] = pt_size
indus_ft["clr"] = indus_ft.rubro.map(clr)
# indus_ft["clr_combus"]  = indus_ft.combustible_prim.map(clr_combs)


# Definir nuevo ID por fuente de emisión
indus["f_ind"] = indus.fuente_emision
indus= indus.set_index("f_ind")

indus= wgs84_to_web_mercator(indus, lon="Longitud", lat="Latitud")


# # ##leer archivo de combustibles y juntar df indus
# # cmb_indus = ReadComb()
# # indus_cmb = indus.join(cmb_indus)

########################################################################################
# crear un ColumnDataSource (ds)
source_indus = ColumnDataSource(data=indus_ft)

# definir titulo de columnas de una tabla
columns = [
    TableColumn(field="nombre", title="Nombre", width=60),
    TableColumn(field="raz_social", title="Razon social", width=60),
    TableColumn(field="ton_emision", title="Emisiones (ton CO2/año)", width=30, formatter=NumberFormatter(format="0.0"),),
    TableColumn(field="ener_cons_Co2", title="Energía consumida promedio hora pic electrogenos (kW)", width=30, formatter=NumberFormatter(format="0.0"),),
    TableColumn(field="region", title="Región", width=50),
    TableColumn(field= "combustible_prim", title = "Combustible Primario", width = 50),
    TableColumn(field="rubro", title="Rubro RETC", width=60),
    TableColumn(field="ciiu4", title="CIIU4", width=200),
]

# iniciar tabla con columnas y fuente de datos ds source_indus
data_table = DataTable(
    columns=columns, source=source_indus, width=1400, height=900, editable=True
)
# ########################################################################################

#######################################################################################
# iniciar mapa
tile_provider = get_provider(ESRI_IMAGERY)
p1 = Figure(plot_width=800, plot_height=900,tools=["pan,wheel_zoom,box_zoom,reset,save"],
            x_axis_type="mercator", y_axis_type="mercator",
            x_range=(-9000000,-6000000),y_range=(-6000000,-1200000))
p1.add_tile(tile_provider)


# graficar marcadores de industria y definir info a desplegar con "hover"
sct = p1.scatter(x="x", y="y", size="pt_size" , fill_color='clr', fill_alpha=0.8, legend_field="rubro",
                  source=source_indus)

p1.legend.click_policy = "hide"

p1.add_tools(HoverTool(renderers=[sct],tooltips=[("Nombre: ", "@nombre"), ("Emisiones (ton/año): ", "@ton_emision"),
            ("Rubro: ", "@rubro"), ("Combustible Primario: ", "@combustible_prim")]))
########################################################################

# iniciar tabla específica de empresa
empr1 = indus_ft["nombre"].iloc[0]

df_empr = indus_ft[indus_ft.nombre == empr1]
source_empr = ColumnDataSource(data=df_empr)

columns_empr = [
    TableColumn(field="nombre", title="Nombre", width=25),
    TableColumn(field="fuente_emision", title="Fuente emisión", width=25),
    TableColumn(field="ton_emision", title="Emisiones (ton CO2/año)", width=25, formatter=NumberFormatter(format="0.0")),
    TableColumn(field="ener_cons_Co2", title="Energía consumida promedio hora pic electrogenos (kW)", width=25, formatter=NumberFormatter(format="0.0")),
    TableColumn(field="tipo_contaminante", title="Contaminante", width=25),
    TableColumn(field="combustible_prim", title="Combustible Primario", width=25),
    TableColumn(field="combustible_sec", title="Secundario", width=25) ]

data_tableEmpr = DataTable(
    columns=columns_empr, source=source_empr, width=1400, height=200, editable=True
)
 

#####################################################################################


# crear los menus
wdt = 250

dropDownCtms = Select(value=ctm, title="Contaminante", options=ctms_opt)

minTon = TextInput(value=str(min_ton), title="Mínimo emisiones anuales", width=wdt)
maxTon = TextInput(value=str(max_ton), title="Máximo emisiones anuales", width=wdt)
mrc = ["Antorcha",
    "Caldera de Fluido Térmico",       
    "Caldera de Generación Eléctrica",       
    "Calentador",       
    "Caldera Recuperadora",
    "Convertidor Teniente (CT)",
    "Convertidor Pierce Smith (CPS)",
    "Caldera Calefacción (CA)",    
    "Grupo Electrógeno",       
    "Horno de Panadería",       
    "Incinerador",       
    "Molino de Rodillo",      
    "Marmita de Calcinación",    
    "Caldera Industrial (IN)",       
    "Motor Generación Eléctrica",  
    "Turbina de Gas",   
    "Regenerador Cracking Catalítico (FCCU)",
    "Secadores",
    "Mercado Solar",
    "Mercado H2",
    "Generación eléctrica"
]

mrc.sort()
mrc = ["Todo"] + mrc
dropdownEquip = Select(value=mkt, title="Equipo térmico", options=mrc, width=wdt)

rubro = list(indus.rubro.unique())
rubro.sort()
rubro =["Todo"] + rubro
rbr_multi_choice = MultiChoice(title = "Rubro", value=rbr, options=rubro, width=600, height=200)





region = list(indus.region.unique())
region.append("Todas")
region.append("Rango latitud")
dropdownRegion = Select(value="Todas", title="Region", options=region, width=wdt)

latNorte = TextInput(
    value=str(-18.4), title="Latitud norte (Opción rango latitud)", width=wdt
)
latSur = TextInput(
    value=str(-35), title="Latitud sur (Opción rango latitud)", width=wdt
)

maxEmpr = TextInput(value=str(max_empr), title="Total empresas", width=wdt)
buttCalcUpdate = Button(label="Filtrar", button_type="success", width=wdt)

dropDownTiles = Select(value="ESRI_IMAGERY", title="Tipo mapa", options=tiles)

dropDownComb = MultiChoice(value=["Todo"], title="Combustible Primario", options=comb_list)




#############################################################################################
# definir coordenadas del mapa específico de una empresa
lat = df_empr.y
lon = df_empr.x

offSet = 600
ymin = lat.iloc[0] - offSet
ymax = lat.iloc[0] + offSet
yrng = Range1d()  # ?
yrng.start = ymin
yrng.end = ymax

xmin = lon.iloc[0] - offSet
xmax = lon.iloc[0] + offSet
xrng = Range1d()  # ?
xrng.start = xmin
xrng.end = xmax

# iniciar mapa
tile_provider = get_provider(ESRI_IMAGERY)
p = Figure(
    plot_width=700,
    plot_height=700,
    tools=["pan,wheel_zoom,box_zoom,reset,save"],
    x_axis_type="mercator",
    y_axis_type="mercator",
    x_range=xrng,
    y_range=yrng,
)
p.add_tile(tile_provider)

source = ColumnDataSource(data=dict(lat=lat, lon=lon))

p.circle(x="lon", y="lat", size=10, fill_color="blue", fill_alpha=0.8, source=source)
###############################################################################################


###################
# crear funcion para cambiar mapa de empresa específica (cambio al clickear empresa en tabla superior)
def function_source(attr, old, new):
    """
    Función que permite cambiar el mapa de la empresa específica (la cual cambia al clickear empresa en la tabla superior)

    Parameters
    ----------
    attr : TYPE
        DESCRIPTION.
    old : TYPE
        DESCRIPTION.
    new : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    try:
        selected_index = source_indus.selected.indices[0]
        name_selected = source_indus.data["nombre"][selected_index]

        df_empr = indus[indus.nombre == name_selected]
        source_empr.data = df_empr

        lat = df_empr.y
        lon = df_empr.x
        new_data = dict(lat=lat, lon=lon)
        source.data = new_data

        ymin = lat.iloc[0] - offSet
        ymax = lat.iloc[0] + offSet

        xmin = lon.iloc[0] - offSet
        xmax = lon.iloc[0] + offSet
        xrng.update(start=xmin, end=xmax)
        yrng.update(start=ymin, end=ymax)
        ##############

    except IndexError:
        pass


# crear funcion para cambiar mapa y tabla general

source_indus.selected.on_change("indices", function_source)



def UpdateTable():
    """
    Función creada para un boton. Permite leer y procesar el archivo de 'emisiones_aire_año_cart.csv', 
    aplicando todos los filtros colocados.

    Returns
    -------
    None.

    """

    indus = ReadIndus()
    ctm = dropDownCtms.value
    
    if ctm == "Todo":
        indus = indus[indus.tipo_contaminante.isin(ctms)]
    else:
        indus = indus[indus.tipo_contaminante == ctm]       
        
    comb = dropDownComb.value

    if comb == ["Todo"]:
        pass
    else:
        indus = indus[indus.combustible_prim.isin(comb)]


    indus = IDequipo(indus)
    
    indus = emission_to_energy(indus)

    # eqp_ft = ["CA", "IN", "PC", "CF", "PS", "GE"]
    # indus = indus[indus.equipo.isin(eqp_ft)]

    mkt = dropdownEquip.value
    indus_tmp = FiltEquip(indus, mkt)

    min_ton = float(minTon.value)
    max_ton = float(maxTon.value)
    indus_ft = IndusFilt(indus_tmp, min_ton, max_ton)

    max_empr = int(maxEmpr.value)
    
            
    rbr = rbr_multi_choice.value
    indus_ft = Filtrbr(indus_ft, rbr, max_empr)
    
    rn = dropdownRegion.value
    latN = float(latNorte.value)
    latS = float(latSur.value)
    indus_ft = FiltRegion(indus_ft, rn, latN, latS)
    
    source_empr.data = indus_ft
    
    indus_ft = wgs84_to_web_mercator(indus_ft, lon="Longitud", lat="Latitud")
    pt_size = np.log(indus_ft.ton_emision)
    indus_ft["pt_size"] = pt_size
    indus_ft["clr"] = indus_ft.rubro.map(clr)
    # indus_ft["clr_combus"]  = indus_ft.combustible_prim.map(clr_combs)
        
    source_indus.data = indus_ft
    source_empr.data = indus_ft
    
        
    tl = get_provider(dropDownTiles.value)
    p1.renderers = [
        x for x in p1.renderers if not str(x).startswith("TileRenderer")
    ]  # ?
    tile_renderer = TileRenderer(tile_source=tl)  # ?
    p1.renderers.insert(0, tile_renderer)

    source_empr.data = indus_ft
    # source_indus.data = indus_ft
  

def DownloadButton():
   
    indus_D = ReadIndus()
    ctm = dropDownCtms.value
     
    indus_D = indus_D[indus_D.tipo_contaminante == ctm]


    comb = dropDownComb.value

    if comb == ["Todo"]:
        pass
    else:
        indus_D = indus_D[indus_D.combustible_prim.isin(comb)]
    
    indus_D = IDequipo(indus_D)
    
    indus_D = emission_to_energy(indus_D)


    mkt = dropdownEquip.value
    indus_tmp = FiltEquip(indus_D, mkt)

    min_ton = float(minTon.value)
    max_ton = float(maxTon.value)
    indus_ft2 = IndusFilt(indus_tmp, min_ton, max_ton)

    max_empr = int(maxEmpr.value)
    # catg = dropDownCat.value

    
    rbr = rbr_multi_choice.value
    indus_ft2 = Filtrbr(indus_ft, rbr, max_empr)

 
    indus_ft2 = indus_ft2.drop(['clr','Latitud','Longitud','rbr', 'comuna'
                          ,'huso','n_equip','orden','max_emision', 'pt_size'
                          ,'x','y'
                            ], axis = 1)
    
    indus_ft2 = indus_ft2[['nombre','raz_social','rubro',
                            'ciiu4','region','provincia','fuente_emision',
                            'combustible_prim','combustible_sec','tipo_contaminante',
                            'ton_emision']]
    
    nw = ColumnDataSource(data = indus_ft2)
    # nw = source_indus
    
    nw.data = indus_ft2
    
    # source_indus = ColumnDataSource(data = indus_ft)
    
    button = Button(label="Download", button_type="success")
    button.js_on_click(CustomJS(args=dict(source=source_indus),
                                code=open(join(dirname(__file__), "download.js")).read()))
    
    return nw

    

# nw = DownloadButton()

#############################################
buttCalcUpdate.on_click(UpdateTable)
# buttCatgUpdate.on_click(UpdateCatg)
# buttCalcUpdate.on_click(DownloadButton)
# indus_temp = UpdateTable()
# nw = DownloadButton()





button = Button(label="Download", button_type="success")


button.on_click(DownloadButton)
button.on_click(DownloadButton)
nw = DownloadButton()
button.js_on_click(CustomJS(args=dict(source=nw),
                        code=open(join(dirname(__file__), "download.js")).read()))
#############################################


#############################################


spc = 50
layout = column(
    row(dropDownCtms, minTon, maxTon, dropdownEquip),
    row(maxEmpr, dropDownComb),# buttCatgUpdate),
    row(rbr_multi_choice),
    Spacer(height=spc),
    row(dropdownRegion, latNorte, latSur),
    row(dropDownTiles),
    row(buttCalcUpdate, button),
    Spacer(height=spc - 20),
    row(p1, data_table),
    Spacer(height=spc + 30),
    data_tableEmpr,
    p,
)
############################################
curdoc().add_root(layout)
