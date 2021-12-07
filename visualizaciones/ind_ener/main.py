#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 10 12:00:42 2020

@author: fcuevas
"""
import sys
sys.path
#sys.path.append('/home/ubuntu/sun4heat/scripts')
#sys.path.append('/Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/scripts')
sys.path.append('/home/ubuntu/Thenergy/diego/sun4heat/scripts')

import pandas as pd
import numpy as np

#from math import pi

from bokeh.plotting import Figure
from bokeh.models.widgets import  Select, Button
from bokeh.models import  DatetimeTickFormatter
from bokeh.layouts import column, Spacer, row
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.io import curdoc

months = ['January','February','March','April','May','June','July','August','September','October','November','December']

#path = '/Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/datos/Combustibles'
path = '/home/ubuntu/Thenergy/diego/sun4heat/datos/Combustibles'

# https://www.engineeringtoolbox.com/energy-content-d_868.html
indicadores = {'Mont Belvieu'   : {'std_unit':'gal',    'PCI':91330,    'abrev':'mont'},
               'Brent'          : {'std_unit':'barrel', 'PCI':5800000,'abrev':'brent'},
               'WTI'            : {'std_unit':'barrel', 'PCI':5800000,  'abrev':'wti'},
               'Henry Hub'      : {'std_unit':'MMBtu', 'PCI':1e6,         'abrev':'hhub'},
               'enap_glp'       : {'std_unit':'ton',    'PCI':12956008,        'abrev':'glp'},
               'enap_dsl'       : {'std_unit':'m3',     'PCI':35960000,        'abrev':'dsl'}}

periodos = {'Diario':'D',
            'Semanal':'W',
            'Mensual':'M',
            'Anual':'A'}

tipos = {'USD/unidad std':'std_unit',
         'USD/MMBtu':'MMBtu',
         'Normalizado':'norm',
         'Tasa crecimiento':'perc'}

def EnerConv(df,indice,periodo):
    df_c = df.resample(periodos[periodo]).mean()
    df_c['MMBtu'] = df_c.std_unit * indicadores[indice]['PCI']/1e6
    df_c['MWh'] =df_c.MMBtu * 3.412
    
    df_c['shifted'] = df_c.std_unit.shift(periods=1)
    df_c['perc'] = 100 - df_c.std_unit / df_c.shifted*100
    df_c['norm'] = df_c.std_unit / df_c.std_unit.iloc[0]*100
    
    return df_c

def TipoGraf(df,tipo):
    var = tipos[tipo]
    df['var_graph'] = df[var]
    return df

def flat_list(lt):
    flat_list = []
    for sublist in lt:
        for item in sublist:
            flat_list.append(item)
            
    return flat_list 

################################################
mont = pd.read_excel(path + '/EER_EPLLPA_PF4_Y44MB_DPGd.xls',sheet_name='Data 1',skiprows=2)
mont.set_index('Date',inplace=True)
mont = mont.rename(columns={'Mont Belvieu, TX Propane Spot Price FOB (Dollars per Gallon)':'std_unit'})

wti = pd.read_excel(path + '/RWTCd.xls',sheet_name='Data 1',skiprows=2)
wti.set_index('Date',inplace=True)
wti = wti.rename(columns={'Cushing, OK WTI Spot Price FOB (Dollars per Barrel)':'std_unit'})

brent = pd.read_excel(path + '/RBRTEd.xls',sheet_name='Data 1',skiprows=2)
brent.set_index('Date',inplace=True)
brent = brent.rename(columns={'Europe Brent Spot Price FOB (Dollars per Barrel)':'std_unit'})

hhub = pd.read_excel(path + '/RNGWHHDd.xls',sheet_name='Data 1',skiprows=2)
hhub.set_index('Date',inplace=True)
hhub = hhub.rename(columns={'Henry Hub Natural Gas Spot Price (Dollars per Million Btu)':'std_unit'})

enp_glp = pd.read_csv(path + '/glp_enap.csv',date_parser=['fecha'])
enp_glp.set_index('Date',inplace=True)
enp_glp = enp_glp.rename(columns={'GLP_usd_ton':'std_unit'})
enp_glp.index = pd.to_datetime(enp_glp.index)

enp_dsl = pd.read_csv(path + '/dsl_enap.csv',date_parser=['fecha'])
enp_dsl.set_index('Date',inplace=True)
enp_dsl = enp_dsl.rename(columns={'Diesel_m3':'std_unit'})
enp_dsl.index = pd.to_datetime(enp_dsl.index)
################################################
# leer archivo de la EIA, con los datos históricos del indicador Mont Belvieu
#df = pd.read_excel(path + '/datos/EER_EPLLPA_PF4_Y44MB_DPGd.xls',sheet_name='Data 1',skiprows=2)
#df.set_index('Date',inplace=True)
#df = df.rename(columns={'Mont Belvieu, TX Propane Spot Price FOB (Dollars per Gallon)':'std_unit'})
indice = 'WTI'
periodo = 'Diario'
tipo = 'USD/unidad std'

df = wti
############
df_new = EnerConv(df,indice,periodo)
df_new = TipoGraf(df_new,tipo)
data_ind = ColumnDataSource(data=df_new)
############
df_month = EnerConv(df,indice,'Mensual')
monthVal = df_month.index.month
yearVal = df_month.index.year
vals = df_month.std_unit.round(3)

source1 = ColumnDataSource(data=dict(month_vs=monthVal,
                                      year_vs=yearVal,
                                      val_vs=vals))
############
from funciones_econ import RandomWalk

rnd_walk = RandomWalk(df,indice,30)
source_rnd = ColumnDataSource(data=rnd_walk)

################################################
per = Select(value=periodo, title="Períodos",options=list(periodos.keys())) 

tip = Select(value=tipo, title='Tipo gráfico',options=list(tipos.keys()))

ind = Select(value=indice, title='Indicador', options=list(indicadores.keys()))
buttCalcGraph = Button(label="Graficar", button_type="success")
buttCalcWalk = Button(label="Random", button_type="success")
################################################
TOOLS="hover,crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select,save"
plot_w = 920
plot_h = 400
#######


################################################################################################## 
# p = Figure(y_range=months,
#            x_axis_location="below", plot_width=1360, plot_height=480,
#            tools=TOOLS, toolbar_location='above')

# p.grid.grid_line_color = None
# p.axis.axis_line_color = 'black'
# p.axis.major_tick_line_color = 'black'
# p.axis.major_label_text_font_size = "10pt"
# p.axis.major_label_standoff = 0

# p.xaxis.major_label_orientation = pi / 3

# mapper = LinearColorMapper(palette=cc.rainbow, low=0, high=vals.max())
# p.rect(x='year_vs', y='month_vs', width=1.0, height=1.0,
#        source=source1,
#        fill_color={'field': 'val_vs', 'transform': mapper},
#        line_color='black')

# text_props = {"source": source1, "text_align": "center", "text_baseline": "middle"}
# r = p.text(x='year_vs', y='month_vs', text="val_vs", **text_props)
# r.glyph.text_font_style="bold"
# r.glyph.text_font_size="10pt"

# color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="8pt",
#                      ticker=BasicTicker(desired_num_ticks=6),
#                      formatter=PrintfTickFormatter(format="%d"),
#                      label_standoff=6, border_line_color=None, location=(0, 0))
# p.add_layout(color_bar, 'right')

#############################################
p1 = Figure(tools=TOOLS,title="Precio del GLP", x_axis_label="Fecha", y_axis_label= "Precio (usd/ton)", 
            plot_width=plot_w, plot_height=plot_h)

p1.line('Date','var_graph',color='black',source=data_ind, legend_label='Mont Belvieu')
p1.xaxis.formatter=DatetimeTickFormatter()


p2 = Figure(tools=TOOLS,title="Precio del GLP", x_axis_label="Fecha", y_axis_label= "Precio (usd/ton)", 
            plot_width=plot_w, plot_height=plot_h)

p2.line('Date','std_unit',color='black',source=source_rnd, legend_label='Indice')
p2.line('Date','rnd',color='blue',source=source_rnd, legend_label='Random walk')
p2.line('Date','proy',color='green',source=source_rnd, legend_label='Random walk proy')
p2.xaxis.formatter=DatetimeTickFormatter()


def Update():
    indice = ind.value
    periodo = per.value
    tipo = tip.value
    
    if indice == 'Mont Belvieu':
        df = mont
    elif indice == 'Brent':
        df = brent
    elif indice == 'WTI':
        df = wti
    elif indice == 'Henry Hub':
        df = hhub
    
    df_new = EnerConv(df,indice,periodo)
    df_new = TipoGraf(df_new,tipo)
    data_ind.data = df_new
    

def CreateWalk():
    df = pd.DataFrame()
    indice = ind.value
    if indice == 'Mont Belvieu':
        df = mont
    elif indice == 'Brent':
        df = brent
    elif indice == 'WTI':
        df = wti
    elif indice == 'Henry Hub':
        df = hhub
    
    print (df.describe())
    rnd_walk = RandomWalk(df,indice,30)
    source_rnd.data=rnd_walk

buttCalcGraph.on_click(Update)
buttCalcWalk.on_click(CreateWalk)

layout = column(row(ind,tip,per),
        buttCalcGraph,buttCalcWalk,
        p1,p2)
curdoc().add_root(layout)