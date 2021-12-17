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

#Libreria para descargar csv
from os.path import dirname, join
# Donde instalar. Versión local y versión en servidor
# <<<<<<< HEAD
path = "/home/ubuntu/Thenergy/diego/sun4heat/"
# path = 'C:/Users/diieg/OneDrive/Documentos/Thenergy/sun4heat/'
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

# definición de categorías según columna del archivo "emisiones_aire_2018_cart.csv"
# cats = {'Otras actividades':1,
#             'Producción de alimentos':2,
#             'Industria agropecuaria y silvicultura':3,
#             'Gestor de residuos':4,
#             'Transporte':5, 'Industria manufacturera':6, 'Extracción de minerales':7,
#            'Producción de metal':8, 'Municipio':9, 'Construcción e inmobiliarias':10,
#            'Generación de energía':11, 'Comercio':12, 'Pesca':13, 'Producción química':14,
#            'Suministro y tratamiento de aguas':15,
#            'Industria del papel y celulosa':16, 'Combustibles':17}

cats = {
    "Captación, tratamiento y distribución de agua": 1,
    "Comercio mayorista": 2,
    "Comercio minorista": 3,
    "Fundiciones de cobre": 4,
    "Gestores de residuos": 5,
    "Industria de la madera y Silvicultura": 6,
    "Industria del papel y celulosa": 7,
    "Industria química, del plástico y caucho": 8,
    "Minería": 9,
    "Otras actividades": 10,
    "Otras centrales de generación eléctrica": 11,
    "Otras industrias manufactureras": 12,
    "Pesca y Acuicultura": 13,
    "Plantas de tratamiento de aguas servidas": 14,
    "Producción agropecuaria": 15,
    "Producción de cemento, cal y yeso": 16,
    "Refinería de petróleo": 17,
    "Termoeléctricas": 18,
    "Ventas y reparaciones de vehículos automotores": 19,
}

# paleta de colores para los gráficos
clr = dict(zip(cats, Category20[20]))
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
    
    Headers DataFrame (ANTIGUO, FALTA ACTUALIZAR)
    -----------------
        'raz_social', 'nombre', 'ID', 'rubro', 'ciiu4', 'fuente_emision', 
        'tipo_contaminante', 'ton_emision', 'anho', 'region', 'provincia', 
        'comuna', 'huso', 'coord_norte', 'coord_este','Longitud','Latitud'.
        
    """
    header = ['ID', 	'raz_social',	'nombre' #establecimiento
              ,	'rubro', 'ciiu6', 'ciiu4', 'region', 'provincia', 'comuna',
              'coord_este', 'coord_norte', 'huso', 'COD_FUENTE', 'fuente_emision', 'COMBUSTIBLE PRIMARIO',
              'EMISION PRIMARIO', 'COMBUSTIBLE SECUNDARIO', 'EMISION SECUNDARIO', 'EMISION MATERIA PRIMA', 	'tipo_contaminante',
              'ton_emision', 'ORIGEN', 'Longitud', 'Latitud']

    # header = ['Razón Social','ID Establecimiento VU','Nombre Establecimiento','Rubro RETC','CIIU6',
    #           'CIIU4','Región','Provincia','Comuna','Coordenada Este','Coordenada Norte','Huso',
    #           'Fuente','Nombre Fuente','Tipo de Emisión','Combustible','Origen','Contaminante',
    #             'Emisión (Toneladas)']

    # indus = pd.read_csv(path + 'datos/RETC/ckan_ruea_2019_v1.csv', names=header, encoding="latin-1",skiprows=1,sep=';',decimal=',')
    indus = pd.read_excel(
        path + "datos/RETC/indus_ll.xlsx",
        names=header,
        encoding="utf-8-sig"
    )

    indus.ton_emision = pd.to_numeric(indus.ton_emision, errors="coerce")
    indus = indus.dropna()

    return indus


# def ReadComb():
#     '''
#     Esta función lee csv con información de combustibles, en donde se calculan las métricas de consumom anual, promedio y deviación estandar.

#     Returns
#     -------
#     cmb : DataFrame
#         DF con métricas de consumo anual, promedio y desviación estandar calculadas.


#     '''
#     cmb = pd.read_csv(path + 'datos/RETC/info_combustibles.csv', encoding="utf-8",sep=';',decimal=',')
#     cmb['f_index'] = cmb.fuente
#     cmb = cmb.set_index('f_index')
#     cmb = cmb[cmb.estado == 'Activa']
#     cmb['con_anual'] = cmb.ene + cmb.feb + cmb.mar + cmb.abr + cmb.may + cmb.jun + cmb.jul + cmb.ago + cmb.sep + cmb.oct + cmb.nov + cmb.dic
#     cmb['promedio'] = cmb.con_anual/12
#     cmb['desv_std1'] = (cmb.ene-cmb.promedio)**2 + (cmb.feb-cmb.promedio)**2 + (cmb.mar-cmb.promedio)**2 + \
#                         (cmb.abr-cmb.promedio)**2 + (cmb.may-cmb.promedio)**2 + (cmb.jun-cmb.promedio)**2 + \
#                         (cmb.jul-cmb.promedio)**2 + (cmb.ago-cmb.promedio)**2 + (cmb.sep-cmb.promedio)**2 + \
#                         (cmb.oct-cmb.promedio)**2 + (cmb.nov-cmb.promedio)**2 + (cmb.dic-cmb.promedio)**2

#     cmb['desv_std'] = np.sqrt(cmb.desv_std1/12)
#     return cmb

# extraer primeras 2 letras de la columna fuente_emision
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

    if mkt == "Caldera Calefacción (CA)":
        eqp_ft = ["CA"]

    elif mkt == "Caldera Industrial (IN)":
        eqp_ft = ["IN"]

    elif mkt == "Mercado Solar":
        eqp_ft = ["IN", "CF", "CA"]

    elif mkt == "Mercado H2":
        eqp_ft = ["IN", "CF", "CA", "PC", "PS"]

    elif mkt == "Generación eléctrica":
        eqp_ft = ["GE"]

    elif mkt == "Todo":
        eqp_ft = ["CA", "IN", "PC", "CF", "PS", "GE"]

    df = df[df.equipo.isin(eqp_ft)]

    return df


# agrupar
def IndusFilt(df, min_ton, max_ton):
    """
    Función que filtra el DF entregado (emisiones_aire_año_cart.csv) según un rango de toneladas (min_ton, max_ton). 
    También agrupa según el ID, sumando las columnas de ton_emision y n_equip, agregando columna de max_emision.
    
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
            "n_equip": "sum",
            "raz_social": "first",
            "nombre": "first",
            "rubro": "first",
            "ciiu4": "first",
            "region": "first",
            "provincia": "first",
            "comuna": "first",
            "huso": "first",
            "coord_norte": "first",
            "coord_este": "first",
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
def FiltCatg(df, catg, max_empr):
    """
    Función que filtra según las categorias presentes en 'emisiones_aire_año_cart.csv'.
    
    Categorias
    ----------
            'Otras actividades'
            'Producción de alimentos'
            'Industria agropecuaria y silvicultura'
            'Gestor de residuos'
            'Transporte'
            'Industria manufacturera'
            'Extracción de minerales'   
            'Producción de metal'
            'Municipio'
            'Construcción e inmobiliarias'
            'Generación de energía'
            'Comercio'            
            'Pesca'
            'Producción química'
            'Suministro y tratamiento de aguas'
            'Industria del papel y celulosa'
            'Combustibles'

    Parameters
    ----------
    df : DataFrame
        DF en donde se filtra la categoría correspondiente.
    catg : List
        Lista de strings que contiene las categorías a filtrar.
    max_empr : int
        Por ahora ninguna función.

    Returns
    -------
    df : DataFrame
        DF con la categoría filtrada.

    """

    df["catg"] = df.rubro.map(cats)
    df = df[df.rubro.isin(catg)]

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


# ########################################################################################
# crear dataframe (df) indus
indus = ReadIndus()

# crear lista de contaminantes
ctms = list(indus.tipo_contaminante.unique())  # saca uno de cada contaminante

# definir contaminante inicial a analizar y filtrar df indus
ctm = "Carbon dioxide"
indus = indus[indus.tipo_contaminante == ctm]

# filtrar df indus según equipo a analizar
indus = IDequipo(
    indus
)  # IDequipo: quita primeras dos letra de columna y las pone en columna "equipo"

# lista de equipos a analizar
eqp_ft = ["CA", "IN", "PC", "CF", "PS", "GE"]
indus = indus[indus.equipo.isin(eqp_ft)]  # cruzar eqp_ft con indus.equipo
mkt = "Mercado Solar"
indus_tmp = FiltEquip(indus, mkt)  # deja unicamente los equipos del mercado a analizar

# definir el mínimo de emisiones a analizar en las empresas
min_ton = 1000
max_ton = 0
indus_ft = IndusFilt(
    indus_tmp, min_ton, max_ton
)  # agrupa por ID  (suma toneladas y n° de equipos que tiene)

# definir máximo de empresas a analizar
max_empr = 1000

# definir categoría
catg = ["Minería"]
indus_ft = FiltCatg(
    indus_ft, catg, max_empr
)  # Cruza la base agrupada y con la categoría de actividad

# convertir latitud y longitud
indus_ft = wgs84_to_web_mercator(
    indus_ft, lon="Longitud", lat="Latitud"
)  # crea plano columnas (x,y) en función de lat y long

# definir tamaño y color del marcador en el mapa
pt_size = np.log(indus_ft.ton_emision)
indus_ft["pt_size"] = pt_size
indus_ft["clr"] = indus_ft.rubro.map(clr)


# Definir nuevo ID por fuente de emisión
indus["f_ind"] = indus.fuente_emision
indus = indus.set_index("f_ind")

indus = wgs84_to_web_mercator(indus, lon="Longitud", lat="Latitud")


# ##leer archivo de combustibles y juntar df indus
# cmb_indus = ReadComb()
# indus_cmb = indus.join(cmb_indus)

########################################################################################
# crear un ColumnDataSource (ds)
source_indus = ColumnDataSource(data=indus_ft)

# definir titulo de columnas de una tabla
columns = [
    TableColumn(field="nombre", title="Nombre", width=60),
    TableColumn(field="raz_social", title="Razon social", width=60),
    TableColumn(
        field="ton_emision",
        title="Emisiones (ton CO2/año)",
        width=30,
        formatter=NumberFormatter(format="0.0"),
    ),
    TableColumn(field="region", title="Región", width=50),
    TableColumn(field="rubro", title="Rubro RETC", width=60),
    TableColumn(field="ciiu4", title="CIIU4", width=200),
]

# iniciar tabla con columnas y fuente de datos ds source_indus
data_table = DataTable(
    columns=columns, source=source_indus, width=1400, height=900, editable=True
)
########################################################################################

########################################################################################
# iniciar mapa
tile_provider = get_provider(ESRI_IMAGERY)
p1 = Figure(
    plot_width=800,
    plot_height=900,
    tools=["pan,wheel_zoom,box_zoom,reset,save"],
    x_axis_type="mercator",
    y_axis_type="mercator",
    x_range=(-9000000, -6000000),
    y_range=(-6000000, -1200000),
)
p1.add_tile(tile_provider)

# graficar marcadores de industria y definir info a desplegar con "hover"
sct = p1.scatter(
    x="x",
    y="y",
    size="pt_size",
    fill_color="clr",
    fill_alpha=0.8,
    legend_field="rubro",
    source=source_indus,
)
p1.legend.click_policy = "hide"
p1.add_tools(
    HoverTool(
        renderers=[sct],
        tooltips=[
            ("Nombre: ", "@nombre"),
            ("Emisiones (ton/año): ", "@ton_emision{0.0}"),
            ("Rubro: ", "@rubro"),
        ],
    )
)
##########################################################################

# iniciar tabla específica de empresa
empr1 = indus_ft["nombre"].iloc[0]

df_empr = indus_ft[indus_ft.nombre == empr1]
source_empr = ColumnDataSource(data=df_empr)

columns_empr = [
    TableColumn(field="nombre", title="Nombre", width=25),
    TableColumn(field="fuente_emision", title="Fuente emisión", width=25),
    TableColumn(
        field="ton_emision",
        title="Emisiones (ton CO2/año)",
        width=25,
        formatter=NumberFormatter(format="0.0"),
    ),
    TableColumn(field="combustible", title="Combustible", width=25),
    # TableColumn(field="unidad_cmb", title="Unidad combustible",width=25),
    # TableColumn(field="con_anual", title="Consumo combustible anual",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="ene", title="Enero",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="feb", title="Febrero",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="mar", title="Marzo",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="abr", title="Abril",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="may", title="Mayo",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="jun", title="Junio",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="jul", title="Julio",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="ago", title="Agosto",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="sep", title="Septiembre",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="oct", title="Octubre",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="nov", title="Noviembre",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="dic", title="Diciembre",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="promedio", title="Promedio",width=25, formatter=NumberFormatter(format="0.0")),
    # TableColumn(field="desv_std", title="Desv Std",width=25, formatter=NumberFormatter(format="0.0")),
]

data_tableEmpr = DataTable(
    columns=columns_empr, source=source_empr, width=1400, height=200, editable=True
)


#####################################################################################


# crear los menus
wdt = 250

dropDownCtms = Select(value=ctm, title="Contaminante", options=ctms)

minTon = TextInput(value=str(min_ton), title="Mínimo emisiones anuales", width=wdt)
maxTon = TextInput(value=str(max_ton), title="Máximo emisiones anuales", width=wdt)
mrc = [
    "Mercado Solar",
    "Mercado H2",
    "Caldera Calefacción (CA)",
    "Caldera Industrial (IN)",
    "Generación eléctrica",
    "Todo",
]
dropdownEquip = Select(value=mkt, title="Equipo térmico", options=mrc, width=wdt)

rubro = list(indus.rubro.unique())
multi_choice = MultiChoice(value=catg, options=rubro, width=600, height=200)

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

dropDownCat = Select(value="rubro", title="Categoría", options=["rubro", "combustible"])

buttExportCSV_Excel = Button(
    label="Exportar a CSV y Excel", button_type="success", width=wdt
)

##############################################################################################
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
    indus = indus[indus.tipo_contaminante == ctm]

    indus = IDequipo(indus)
    eqp_ft = ["CA", "IN", "PC", "CF", "PS", "GE"]
    indus = indus[indus.equipo.isin(eqp_ft)]

    mkt = dropdownEquip.value
    indus_tmp = FiltEquip(indus, mkt)

    min_ton = float(minTon.value)
    max_ton = float(maxTon.value)
    indus_ft = IndusFilt(indus_tmp, min_ton, max_ton)

    max_empr = int(maxEmpr.value)
    catg = multi_choice.value
    indus_ft = FiltCatg(indus_ft, catg, max_empr)

    rn = dropdownRegion.value
    latN = float(latNorte.value)
    latS = float(latSur.value)
    indus_ft = FiltRegion(indus_ft, rn, latN, latS)

    indus_ft = wgs84_to_web_mercator(indus_ft, lon="Longitud", lat="Latitud")
    pt_size = np.log(indus_ft.ton_emision)
    indus_ft["pt_size"] = pt_size
    indus_ft["clr"] = indus_ft.rubro.map(clr)

    source_indus.data = indus_ft

    tl = get_provider(dropDownTiles.value)
    p1.renderers = [
        x for x in p1.renderers if not str(x).startswith("TileRenderer")
    ]  # ?
    tile_renderer = TileRenderer(tile_source=tl)  # ?
    p1.renderers.insert(0, tile_renderer)


buttCalcUpdate.on_click(UpdateTable)  # botón actualizar tabla

source_indus.selected.on_change("indices", function_source)

# Botón exportar empresa especifica a csv
def ExportToCSV_Excel():
    """
    Fución que utiliza todos los filtros puestos en la página, los almacena en un DF para ser llamado por un boton
    el cual entregue un CSV y un Excel.

    Returns
    -------
    None.

    """

    indus = ReadIndus()
    ctm = dropDownCtms.value
    indus = indus[indus.tipo_contaminante == ctm]

    indus = IDequipo(indus)
    eqp_ft = ["CA", "IN", "PC", "CF", "PS", "GE"]
    indus = indus[indus.equipo.isin(eqp_ft)]

    mkt = dropdownEquip.value
    indus_tmp = FiltEquip(indus, mkt)

    min_ton = float(minTon.value)
    max_ton = float(maxTon.value)
    indus_ft = IndusFilt(indus_tmp, min_ton, max_ton)

    max_empr = int(maxEmpr.value)
    catg = multi_choice.value
    indus_ft = FiltCatg(indus_ft, catg, max_empr)

    rn = dropdownRegion.value
    latN = float(latNorte.value)
    latS = float(latSur.value)
    indus_ft = FiltRegion(indus_ft, rn, latN, latS)

    indus_ft = wgs84_to_web_mercator(indus_ft, lon="Longitud", lat="Latitud")
    pt_size = np.log(indus_ft.ton_emision)
    indus_ft["pt_size"] = pt_size
    indus_ft["clr"] = indus_ft.rubro.map(clr)

    print("Antes de filtrar")

    indus_ft.to_csv(
        path + "visualizaciones/2019_mapa_emisiones/empresas_filtradas.csv",
        encoding="utf-8-sig",
        sep=".",
        decimal=",",
    )
    indus_ft.to_excel(
        path + "visualizaciones/2019_mapa_emisiones/empresas_filtradas.xlsx",
        encoding="utf-8-sig",
    )

    print("Despues de filtrar")

    ####################################
# buttondownload = Button(label="Download", button_type="success")
# buttondownload.js_on_click(CustomJS(args=dict(source=source_indus), code=open(join(dirname(
#                                     "/home/ubuntu/Thenergy/diego/sun4heat/scripts"), 'download.js')).read()))

buttExportCSV_Excel.on_click(ExportToCSV_Excel)
#############################################


#############################################


spc = 50
layout = column(
    row(dropDownCtms, minTon, maxTon, dropdownEquip),
    row(maxEmpr, multi_choice),
    row(dropdownRegion, latNorte, latSur),
    row(dropDownTiles, dropDownCat),
    row(buttCalcUpdate, buttExportCSV_Excel),
    Spacer(height=spc - 20),
    row(p1, data_table),
    Spacer(height=spc + 30),
    data_tableEmpr,
    p,
)
############################################
curdoc().add_root(layout)
