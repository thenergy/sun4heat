#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 20 08:11:42 2020

@author: fcuevas
"""
# import time

import numpy as np
import pandas as pd

from bokeh.plotting import Figure

from bokeh.models import ColumnDataSource, TableColumn, DataTable, TextInput, Select, NumberFormatter, Range1d, HoverTool, TileRenderer, MultiChoice
from bokeh.io import curdoc
from bokeh.layouts import column, row, Spacer
from bokeh.models.widgets import Button

from bokeh.palettes import Category20

from bokeh.tile_providers import get_provider, CARTODBPOSITRON, CARTODBPOSITRON_RETINA, STAMEN_TERRAIN,\
STAMEN_TERRAIN_RETINA, STAMEN_TONER, STAMEN_TONER_BACKGROUND,\
STAMEN_TONER_LABELS, OSM, WIKIMEDIA, ESRI_IMAGERY

#path = '/Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/'
path = '/home/ubuntu/Thenergy/diego/sun4heat/'
# path = '/home/ubuntu/sun4heat/'

tiles = ['CARTODBPOSITRON', 'CARTODBPOSITRON_RETINA', 'STAMEN_TERRAIN',
'STAMEN_TERRAIN_RETINA', 'STAMEN_TONER', 'STAMEN_TONER_BACKGROUND',
'STAMEN_TONER_LABELS', 'OSM', 'WIKIMEDIA', 'ESRI_IMAGERY']

cats = {'Otras actividades':1, 
            'Producción de alimentos':2,
            'Industria agropecuaria y silvicultura':3, 
            'Gestor de residuos':4,
            'Transporte':5, 'Industria manufacturera':6, 'Extracción de minerales':7,
           'Producción de metal':8, 'Municipio':9, 'Construcción e inmobiliarias':10,
           'Generación de energía':11, 'Comercio':12, 'Pesca':13, 'Producción química':14,
           'Suministro y tratamiento de aguas':15,
           'Industria del papel y celulosa':16, 'Combustibles':17}

clr = dict(zip(cats,Category20[20]))

def ReadIndus():
    header = ['raz_social','nombre','ID','rubro','ciiu4','fuente_emision','tipo_contaminante',
          'ton_emision','anho','region','provincia','comuna','huso','coord_norte','coord_este','Longitud','Latitud']

    indus = pd.read_csv(path + 'datos/RETC/emisiones_aire_2018_cart.csv', encoding="utf-8",names=header,skiprows=1,sep=',',decimal='.')
    indus.ton_emision = pd.to_numeric(indus.ton_emision, errors='coerce')
    indus = indus.dropna()
    
    return indus

def ReadComb():
    cmb = pd.read_csv(path + 'datos/RETC/info_combustibles.csv', encoding="utf-8",sep=';',decimal=',')
    cmb['f_index'] = cmb.fuente
    cmb = cmb.set_index('f_index')
    cmb = cmb[cmb.estado == 'Activa']
    cmb['con_anual'] = cmb.ene + cmb.feb + cmb.mar + cmb.abr + cmb.may + cmb.jun + cmb.jul + cmb.ago + cmb.sep + cmb.oct + cmb.nov + cmb.dic
    cmb['promedio'] = cmb.con_anual/12
    cmb['desv_std1'] = (cmb.ene-cmb.promedio)**2 + (cmb.feb-cmb.promedio)**2 + (cmb.mar-cmb.promedio)**2 + \
                       (cmb.abr-cmb.promedio)**2 + (cmb.may-cmb.promedio)**2 + (cmb.jun-cmb.promedio)**2 + \
                       (cmb.jul-cmb.promedio)**2 + (cmb.ago-cmb.promedio)**2 + (cmb.sep-cmb.promedio)**2 + \
                       (cmb.oct-cmb.promedio)**2 + (cmb.nov-cmb.promedio)**2 + (cmb.dic-cmb.promedio)**2 
   
    cmb['desv_std'] = np.sqrt(cmb.desv_std1/12)
    return cmb

def IDequipo(df):
    clds = []
    for cld in df.fuente_emision:    
        clds.append(cld[0:2])
    df['equipo'] = clds
    
    return df

def FiltEquip(df,mkt):
    
    if mkt == 'Caldera Calefacción (CA)':
        eqp_ft = ['CA']
        
    elif mkt == 'Caldera Industrial (IN)':
        eqp_ft = ['IN']
        
    elif mkt == 'Mercado Solar':
        eqp_ft = ['IN','CF','CA']
        
        
    elif mkt == 'Mercado H2':
        eqp_ft = ['IN','CF','CA','PC','PS']
    
    elif mkt == 'Generación eléctrica':
        eqp_ft = ['GE']
        
    elif mkt == 'Todo':
        eqp_ft = ['CA', 'IN', 'PC', 'CF', 'PS', 'GE']
        
    df = df[df.equipo.isin(eqp_ft)]
        
    return df

def IndusFilt(df,min_ton,max_ton):    
    df['n_equip'] = 1
    df = df.sort_values('ton_emision', ascending=False).drop_duplicates('fuente_emision')
    
    indus_gr = df.groupby(['ID']).agg({
            'ton_emision':'sum',
            'n_equip':'sum',
            'raz_social':'first',
            'nombre':'first',   
            'rubro':'first',
            'ciiu4':'first',
            'region':'first',
            'provincia':'first',
            'comuna':'first',
            'huso':'first',
            'coord_norte':'first',
            'coord_este':'first',
            'Latitud':'first',
            'Longitud':'first'})
    
    indus_max = df.groupby(['ID'])['ton_emision'].max()
    indus_gr['max_emision'] = indus_max
        
    df = indus_gr
    df['orden'] = 1
    
    if max_ton > min_ton:
        df = df[(df.ton_emision > min_ton) & (df.ton_emision < max_ton)]
        
    else:
        df = df[df.ton_emision > min_ton]
    
    return df


def FiltCatg(df,catg,max_empr):

    df['catg'] = df.rubro.map(cats)    
    df = df[df.rubro.isin(catg)]
            
    return df


def FiltRegion(df,rgn,latNor,latSur):
    if rgn == 'Todas':
        df_filt = df
    elif rgn == 'Rango latitud':
        df_filt = df[(df.Latitud < latNor) & (df.Latitud > latSur)]
    else:
        df_filt = df[df.region == rgn]
        
    return df_filt

    
def wgs84_to_web_mercator(df, lon="Longitud", lat="Latitud"):

      k = 6378137
      df["x"] = df[lon] * (k * np.pi/180.0)
      df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k

      return df
  
########################################################################################  
indus = ReadIndus()
ctms = list(indus.tipo_contaminante.unique())
ctm = 'Dióxido de carbono (CO2)'
indus = indus[indus.tipo_contaminante == ctm]
indus = IDequipo(indus)

eqp_ft = ['CA', 'IN', 'PC', 'CF', 'PS', 'GE']
indus = indus[indus.equipo.isin(eqp_ft)]

mkt = 'Mercado Solar'
indus_tmp = FiltEquip(indus,mkt)

min_ton = 500
max_ton = 0
indus_ft = IndusFilt(indus_tmp,min_ton,max_ton)

max_empr= 1000
catg = ['Industria manufacturera','Extracción de minerales', 'Producción de alimentos', 'Industria del papel y celulosa',
    'Producción química', 'Producción de metal', 'Industria agropecuaria y silvicultura', 'Pesca']
indus_ft = FiltCatg(indus_ft,catg,max_empr)
indus_ft = wgs84_to_web_mercator(indus_ft, lon="Longitud", lat="Latitud")
pt_size = np.log(indus_ft.ton_emision)
indus_ft['pt_size'] = pt_size
indus_ft['clr'] = indus_ft.rubro.map(clr)

indus['f_ind'] = indus.fuente_emision
indus = indus.set_index('f_ind')

indus = wgs84_to_web_mercator(indus, lon="Longitud", lat="Latitud")

cmb_indus = ReadComb()
indus_cmb = indus.join(cmb_indus)
########################################################################################  
source_indus = ColumnDataSource(data=indus_ft)

columns = [
        TableColumn(field="nombre", title="Nombre",width=60),
        TableColumn(field="raz_social", title="Razon social",width=60),
        TableColumn(field="ton_emision", title="Emisiones (ton CO2/año)",width=30, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="region", title="Región",width=50),
        TableColumn(field="rubro", title="Rubro RETC",width=60),
        TableColumn(field="ciiu4", title="CIIU4",width=200)]
    
data_table = DataTable(columns=columns, source=source_indus,width=1400, height=900,
                       editable=True)
########################################################################################  

tile_provider = get_provider(ESRI_IMAGERY)
p1 = Figure(plot_width=800, plot_height=900,tools=["pan,wheel_zoom,box_zoom,reset,save"],
           x_axis_type="mercator", y_axis_type="mercator",
           x_range=(-9000000,-6000000),y_range=(-6000000,-1200000))
p1.add_tile(tile_provider)

# p1.circle(x="x", y="y", size='pt_size', fill_color="blue", fill_alpha=0.8, legend_group='rubro', source=source_indus)
sct = p1.scatter(x="x", y="y", size='pt_size', fill_color="clr", fill_alpha=0.8, legend_field='rubro', source=source_indus)
p1.legend.click_policy="hide"
p1.add_tools(HoverTool(renderers=[sct], tooltips=[('Nombre: ', '@nombre'),
      ('Emisiones (ton/año): ', '@ton_emision{0.0}'),
      ('Rubro: ', '@rubro')]))
###################
empr1 = indus_ft['nombre'].iloc[0]

df_empr = indus_cmb[indus_cmb.nombre == empr1]
source_empr = ColumnDataSource(data=df_empr)

columns_empr = [
        TableColumn(field="nombre", title="Nombre",width=25),
        TableColumn(field="fuente_emision", title="Fuente emisión",width=25),
        TableColumn(field="ton_emision", title="Emisiones (ton CO2/año)",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="combustible", title="Combustible",width=25),
        TableColumn(field="unidad_cmb", title="Unidad combustible",width=25),
        TableColumn(field="con_anual", title="Consumo combustible anual",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="ene", title="Enero",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="feb", title="Febrero",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="mar", title="Marzo",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="abr", title="Abril",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="may", title="Mayo",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="jun", title="Junio",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="jul", title="Julio",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="ago", title="Agosto",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="sep", title="Septiembre",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="oct", title="Octubre",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="nov", title="Noviembre",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="dic", title="Diciembre",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="promedio", title="Promedio",width=25, formatter=NumberFormatter(format="0.0")),
        TableColumn(field="desv_std", title="Desv Std",width=25, formatter=NumberFormatter(format="0.0")),
        ]

data_tableEmpr = DataTable(columns=columns_empr, source=source_empr,width=1400, height=200,
                       editable=True)
###################
wdt = 250

dropDownCtms = Select(value=ctm,title='Contaminante',options=ctms)

minTon = TextInput(value=str(min_ton), title="Mínimo emisiones anuales",width=wdt)
maxTon = TextInput(value=str(max_ton), title="Máximo emisiones anuales",width=wdt)
mrc = ['Mercado Solar','Mercado H2','Caldera Calefacción (CA)','Caldera Industrial (IN)','Generación eléctrica','Todo']
dropdownEquip = Select(value=mkt,title='Equipo térmico',options=mrc,width=wdt)

rubro = list(indus.rubro.unique())
multi_choice = MultiChoice(value=catg, options=rubro,width=600, height=200)

region = list(indus.region.unique())
region.append('Todas')
region.append('Rango latitud')
dropdownRegion = Select(value='Rango latitud',title='Region',options=region,width=wdt)

latNorte = TextInput(value=str(-18.4), title="Latitud norte (Opción rango latitud)",width=wdt)
latSur = TextInput(value=str(-35), title="Latitud sur (Opción rango latitud)",width=wdt)

maxEmpr = TextInput(value=str(max_empr), title="Total empresas",width=wdt)
buttCalcUpdate = Button(label="Filtrar", button_type="success",width=wdt)

dropDownTiles = Select(value='ESRI_IMAGERY',title='Tipo mapa',options=tiles)

dropDownCat = Select(value='rubro',title='Categoría',options=['rubro','combustible'])
###############################################################################################
lat = df_empr.y
lon = df_empr.x

offSet = 600
ymin = lat.iloc[0] - offSet
ymax = lat.iloc[0] + offSet
yrng = Range1d()
yrng.start = ymin
yrng.end=ymax

xmin = lon.iloc[0] - offSet
xmax = lon.iloc[0] + offSet
xrng = Range1d()
xrng.start = xmin
xrng.end=xmax

tile_provider = get_provider(ESRI_IMAGERY)
p = Figure(plot_width=700, plot_height=700,tools=["pan,wheel_zoom,box_zoom,reset,save"],
           x_axis_type="mercator", y_axis_type="mercator",
           x_range=xrng,y_range=yrng)
p.add_tile(tile_provider)

source = ColumnDataSource(
    data=dict(lat=lat,
              lon=lon))

p.circle(x="lon", y="lat", size=10, fill_color="blue", fill_alpha=0.8, source=source)
###############################################################################################


###################
def function_source(attr, old, new):
    try:
        selected_index = source_indus.selected.indices[0]
        name_selected = source_indus.data['nombre'][selected_index]
        
        df_empr = indus_cmb[indus_cmb.nombre == name_selected]
        source_empr.data = df_empr
        
        lat = df_empr.y
        lon = df_empr.x
        new_data=dict(lat=lat,lon=lon)
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
    
def UpdateTable():
    
    
    
    indus = ReadIndus()
    ctm = dropDownCtms.value
    indus = indus[indus.tipo_contaminante == ctm]
    
    indus = IDequipo(indus)
    eqp_ft = ['CA', 'IN', 'PC', 'CF', 'PS', 'GE']
    indus = indus[indus.equipo.isin(eqp_ft)]
    
    mkt = dropdownEquip.value
    indus_tmp = FiltEquip(indus,mkt)


    min_ton = float(minTon.value)
    max_ton = float(maxTon.value)
    indus_ft = IndusFilt(indus_tmp,min_ton,max_ton)
    
    max_empr= int(maxEmpr.value)
    catg = multi_choice.value
    indus_ft = FiltCatg(indus_ft,catg,max_empr)
    
    rn = dropdownRegion.value
    latN = float(latNorte.value)
    latS = float(latSur.value)
    indus_ft = FiltRegion(indus_ft,rn,latN,latS)
    indus_ft = wgs84_to_web_mercator(indus_ft, lon="Longitud", lat="Latitud")
    pt_size = np.log(indus_ft.ton_emision)
    indus_ft['pt_size'] = pt_size
    indus_ft['clr'] = indus_ft.rubro.map(clr)
    
    source_indus.data = indus_ft
    
    indus_ft.to_csv(path + 'visualizaciones/mapa_emisiones/industria.csv', encoding="utf-8-sig",sep=',',decimal='.')
    
    tl = get_provider(dropDownTiles.value)
    p1.renderers = [x for x in p1.renderers if not str(x).startswith('TileRenderer')]
    tile_renderer = TileRenderer(tile_source=tl)
    p1.renderers.insert(0, tile_renderer)
    
    
    
buttCalcUpdate.on_click(UpdateTable)
source_indus.selected.on_change('indices', function_source)
##############


spc = 50
layout = column(
        row(dropDownCtms,minTon,maxTon,dropdownEquip),
        row(maxEmpr,multi_choice),
        row(dropdownRegion,latNorte,latSur),
        row(dropDownTiles,dropDownCat),
        buttCalcUpdate,        
        
        Spacer(height=spc-20),
        row(p1,data_table),
        Spacer(height=spc+30),
        data_tableEmpr,
        p)
############################################
curdoc().add_root(layout)