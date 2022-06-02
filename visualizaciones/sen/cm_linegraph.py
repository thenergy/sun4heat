#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 30 14:16:39 2022

@author: diego
"""

import datetime

import numpy as np
import pandas as pd

import colorcet as cc
## librerías de Bokeh
from bokeh.plotting import Figure,show

# from pyproj import Proj, transform

from bokeh.models import (
    ColumnDataSource,
    TableColumn,
    DataTable,
    TextInput,
    LinearColorMapper,
    Select,
    NumberFormatter,
    Range1d,
    HoverTool,
    TileRenderer,
    MultiChoice,
    CustomJS,
    TapTool
)

from bokeh.events import Tap

from bokeh.io import curdoc
from bokeh.layouts import column, row, Spacer
from bokeh.models.widgets import Button, PreText

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

# Libreria para descargar csv boton
from os.path import dirname, join

path = "/home/diego/Documentos/sun4heat/"

year = 2021

cmr = pd.DataFrame()


TOOLS=["pan,wheel_zoom,box_zoom,reset,save"]


#Centrales a analizar
# centrales = ['TARAPACA 220KV-BP2', 'CRUCERO 220KV-BP1', 'ATACAMA 220kV BP1','CARDONES 220KV SECCION 1',
#              'PAN DE AZUCAR 220KV SECCION 1','QUILLOTA 220KV SECCION 1','CHARRUA 220KV SECCION 1','PUERTO MONTT 220kV BP2']

# for month in np.arange(1,13):
clds = []
# head = ['b_mnemo','b_ref_mnemo','fecha','hora','us_cost','clp_cost','nombre']

temp = pd.read_csv(path + "visualizaciones/sen/costos_marginales/cmo/cmo-"+str(year)+".csv",
                   decimal=".", encoding="utf-8-sig")
temp.drop('addValue',axis=1)

#Se corrige base manualmente (horario faltante a la hora 24 del 2021-09-04)

y_rg = np.arange(1,500, 25)
y_rg = [str(x) for x in y_rg]

start = datetime.datetime(2021, 1, 1)
x= np.array([start + datetime.timedelta(hours=i) for i in range(8760)])

yrg = temp.Tarapaca

source = ColumnDataSource(data=dict(x_rg = x, y_rg = yrg))

# TOOLS=["pan,wheel_zoom,box_zoom,reset,save,tap"]


p1 = Figure(y_range=y_rg,
            x_axis_location="below", plot_width=1360, plot_height=600,
            tools=TOOLS, toolbar_location='above', x_axis_type = 'datetime')

p1.grid.grid_line_color = None
p1.axis.axis_line_color = 'black'
p1.axis.major_tick_line_color = 'black'
p1.axis.major_label_text_font_size = "10pt"
p1.axis.major_label_standoff = 0
p1.axis.axis_label_text_align = 'center'

sct =  p1.line('x_rg','y_rg',color='black',source=source, legend_label='Costo marginal USD/MWh')

p1.add_tools(HoverTool(renderers=[sct],tooltips=[("Costo Marginal Tarapaca ", "@y_rg")]))


# p1.add_tools(HoverTool(renderers=[line1_p3], tooltips=[('Fecha: ', '@Date{%F}'),
#     ('Costo histórico (US$/unidad): ', '@std_unit{0.00}'),
#     ('Costo histórico (US$/MMBtu): ', '@MMBtu{0.00}'),
#     ('Costo histórico (US$/MWh): ', '@MWh{0.00}')],mode='vline',formatters={'@Date':'datetime'}))


mapper1 = LinearColorMapper(palette=cc.rainbow, low=0, high=temp.Tarapaca.max())

p1.line(x='x_rg', y='y_rg', width=1.0,         source=source,
        # fill_color={'field': 'y_rg', 'transform': mapper1})
        line_color='black')

# cmr.to_csv(path + 'visualizaciones/sen/costos_marginales_reales/'+str(year)+'-complete.csv')













