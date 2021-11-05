#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 19:31:59 2021

@author: fcuevas
"""

import pandas as pd
import numpy as np
from datetime import datetime

from math import pi
import colorcet as cc

from bokeh.plotting import Figure
from bokeh.models.widgets import  Select, Button, CheckboxButtonGroup, TableColumn, NumberFormatter, DataTable
from bokeh.models import DatetimeTickFormatter, LinearColorMapper, ColorBar, BasicTicker, PrintfTickFormatter, HoverTool, Spacer, RadioButtonGroup
from bokeh.layouts import column, widgetbox, gridplot, row
from bokeh.transform import factor_cmap
from bokeh.palettes import Category20
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.io import curdoc

months = ['January','February','March','April','May','June','July','August','September','October','November','December']

mnths = {1:'January',
         2:'February',
         3:'March',
         4:'April',
         5:'May',
         6:'June',
         7:'July',
         8:'August',
         9:'September',
         10:'October',
         11:'November',
         12:'December'}

""" Función para obtener los días de un mes (creada especialmente para años bisiestos)"""
def dayxmonth(fecha):
  largo_meses=[31,28,31,30,31,30,31,31,30,31,30,31]
  return largo_meses[fecha.month-1]


def dayofyear(day):
  if (day.year%4==0) and (day.year%100!=0):
    day_of_year=(day - datetime(day.year, 1, 1)).days + 1
    if day_of_year==60:
      day_of_year=np.nan
    else:
      if day_of_year>60:
        day_of_year=day_of_year-1
  else:
    day_of_year=(day - datetime(day.year, 1, 1)).days + 1
  return day_of_year


def flat_list(lt):
    flat_list = []
    for sublist in lt:
        for item in sublist:
            flat_list.append(item)
            
    return flat_list 


def param_plot(resPlot):
    if resPlot == 'Demand':
        var = 'demanda_MWh'
    elif resPlot == 'Solar':
        var = 'solar_MWh'
    elif resPlot == 'P2H':
        var = 'elect_sell'
    elif resPlot == 'Dissipation':
        var = 'energ_diss'
    elif resPlot == 'Solar Fraction':
        var = 'sol_frac'
    elif resPlot == 'Solar direct':
        var = 'solarSF_MWh'
    elif resPlot == 'Solar storage':
        var = 'solarST_MWh'
        
        
    return var

def daily_data(df,yr,resPlot):
    year = int(yr)
    
    df_r = df[['Fecha','demanda_MWh','solarSF_MWh','solarST_MWh','P2H_MWh']]

    df_r['solar_MWh'] = df_r.solarSF_MWh + df_r.solarST_MWh
    df_r['energ_diff'] = df_r.demanda_MWh - df_r.solar_MWh
    df_r['solar_sell'] = df_r.solar_MWh.where(df_r.energ_diff > 0, df_r.demanda_MWh)
    df_r['elect_sell'] = df_r.energ_diff.where(df_r.energ_diff > 0, 0)
    df_r['energ_diss'] = df_r.energ_diff.where(df_r.energ_diff < 0, 0)
    df_r['sol_frac'] = (df_r.solar_sell/df_r.demanda_MWh)*100
    
    df_r = df_r.set_index('Fecha')

    day_filt = df_r[df_r.index.year == year]
    day_filt['months'] = day_filt.index.month.map(mnths)
    
    dayVal = day_filt.index.day
    monthValue = day_filt.months

    var = param_plot(resPlot)
    val = day_filt[var].round(1)  
    
    return dayVal, monthValue, val



"""Planta que se estudiará"""
names = ['Escondida','Spence']
name = 'Spence'
#name = 'Escondida'


"""DataFrame que contiene el consumo anual de cada planta"""
consumo_anual = pd.DataFrame.from_dict({2022 : [17577., 8371.],
                                        2023 : [18881., 8708.],
                                        2024 : [21481., 8574.],
                                        2025 : [24393., 8705.],
                                        2026 : [20805., 7938.],
                                        2027 : [18221., 8050.],
                                        2028 : [17733., 7520.],
                                        2029 : [17290., 6509.],
                                        2030 : [17334., 4354.],
                                        2031 : [16363., 3678.],
                                        2032 : [19734., 4144.],
                                        2033 : [16168., 4772.]},
                                       orient='index',
                                       columns=['Escondida', 'Spence'])

"""DataFrame que contiene la distribución del consumo mensual """
consumo_mensual = pd.DataFrame.from_dict({1 : [0.086, 0.054],
                                          2 : [0.070, 0.049],
                                          3 : [0.051, 0.052], 
                                          4 : [0.074, 0.074],
                                          5 : [0.099, 0.094],
                                          6 : [0.116, 0.108],
                                          7 : [0.111, 0.132],
                                          8 : [0.107, 0.133],
                                          9 : [0.101, 0.092],
                                          10 : [0.063, 0.071],
                                          11 : [0.045, 0.072],
                                          12 : [0.078, 0.07]},
                                         orient='index',
                                         columns=['Escondida', 'Spence'])

"""DataFrame creado para el rango desde 1 de enero de 2022 hasta 31 de dic de 2033"""
df = pd.date_range(start='1/1/2022',end='31/12/2033').to_frame()
df = df.rename_axis('Fecha').reset_index()
del df[0]

"""DataFrame que contendrá el resumen de todos los resultados""" 
resumen = df
resumen=resumen.reset_index()

"""DataFrame auxiliar para obtener el consumo anual por cada celda"""
a=consumo_anual[name][resumen['Fecha'].dt.year].to_frame().reset_index().reset_index()
del a['index']
a=a.rename(columns={'level_0':'index',name:'Consumo anual'})

"""Dataframe auxiliar para obtener la distribución del consumo para el mes de la celda"""
b = consumo_mensual[name][resumen['Fecha'].dt.month].to_frame().reset_index().reset_index()
del b['index']
b=b.rename(columns={'level_0':'index', name: 'Consumo mensual'})


"""Relleno de resultados"""
resumen = pd.merge(resumen,a,on='index')
resumen = pd.merge(resumen,b,on='index')
resumen['Dias por mes']= resumen['Fecha'].apply(dayxmonth)

"""Consumo diario = (consumo anual)*(% consumo mensual) / (dias por mes)"""
resumen['Consumo diario'] = resumen['Consumo anual']*resumen['Consumo mensual']/resumen['Dias por mes']

resumen['day']=resumen['Fecha'].apply(dayofyear)

if name == 'Escondida':
    eta_boiler = 0.81
    """Lectura de archivo de resultados"""
    df_results = pd.read_excel('dailyValuesEscondida_v2.xlsx',skiprows=range(1,2))
    df_results['day']=df_results.astype(np.float64)
    
elif name == 'Spence':
    """Lectura de archivo de resultados"""
    df_results = pd.read_excel('dailyValuesSpence_v2.xlsx',skiprows=range(1,2))
    df_results['day']=df_results.astype(np.float64)
    eta_boiler = 0.895
    
#"""Lectura de archivo de resultados"""
#df_results = pd.read_excel('dailyValuesSpence_v2.xlsx',skiprows=range(1,2))
#df_results['day']=df_results.astype(np.float64)

resumen=resumen.merge(df_results,on='day').sort_values(by='index').reset_index(drop=True)

PCI = 11.83 #kWh/kg

dens_diesel = 0.846
resumen['demanda_MWh']=resumen['Consumo diario']*dens_diesel * PCI * eta_boiler

resumen['solarSF_MWh'] = resumen['Solar Direct'] 
resumen['solarST_MWh'] = resumen['Solar Storage'] 
resumen['solar_MWh'] = resumen.solarSF_MWh + resumen.solarST_MWh
resumen['P2H_MWh'] = resumen['P2H'] 


resumen['diesel_m3'] = resumen['Consumo diario']
resumen['sol_frac'] = resumen.solar_MWh/resumen.demanda_MWh*100

res = resumen[['Fecha','demanda_MWh','solarSF_MWh','solarST_MWh','P2H_MWh','diesel_m3']]

res['solar_MWh'] = res.solarSF_MWh + res.solarST_MWh
res = res.set_index('Fecha')

res = res[(res.index.year > 2022) & (res.index.year < 2033)]


res['energ_diff'] = res.demanda_MWh - res.solar_MWh
res['solar_sell'] = res.solar_MWh.where(res.energ_diff > 0, res.demanda_MWh)
res['elect_sell'] = res.energ_diff.where(res.energ_diff > 0, 0)
res['energ_diss'] = res.energ_diff.where(res.energ_diff < 0, 0)
res['sol_frac'] = (res.solar_sell/res.demanda_MWh)*100


maxD_sf = res.sol_frac.max()
maxD_diss = res.energ_diss.max()
minD_diss = res.energ_diss.min()
maxD_dem = res.demanda_MWh.max()
maxD_P2H = res.P2H_MWh.max()


res_ann = res.groupby(res.index.year).sum()
res_ann['sol_frac'] = res_ann.solar_sell/res_ann.demanda_MWh*100
res_ann = res_ann.reset_index()
res_month = res.groupby([res.index.year,res.index.month]).sum()
res_month['sol_frac'] = res_month.solar_sell/res_month.demanda_MWh*100
##################################################################################################                                   
menuLoc=list(names)
dropdownLoc = Select(value=name, title="Location",options=menuLoc,width=300) 

res_vars = ['Demand','Solar','Solar storage','Solar direct', 'P2H','Dissipation', 'Solar Fraction']
menuRes=list(res_vars)
dropdownRes = Select(value='Solar', title="Results [MWh]",options=menuRes,width=300) 

yearButton_n = np.arange(2023,2033)
yearButton = [str(n) for n in yearButton_n]
yearButtonGroup = RadioButtonGroup(labels=yearButton, active=3,width=900)
##################################################################################################                                   
TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select,save"

plot_w = 1110
plot_h = 450

################################################################################################## 
columns = [
    TableColumn(field="Fecha", title="Year"),
    TableColumn(field="diesel_m3", title="Diesel m3", formatter=NumberFormatter(format="0.0")),
    TableColumn(field="demanda_MWh", title="Proc demand MWh", formatter=NumberFormatter(format="0.0")),
    TableColumn(field="solar_sell", title="Solar energy", formatter=NumberFormatter(format="0.0")),
    TableColumn(field="sol_frac", title="Solar fraction", formatter=NumberFormatter(format="0.0")),
    TableColumn(field="elect_sell", title="P2H", formatter=NumberFormatter(format="0.0")),
    TableColumn(field="energ_diss", title="Energy dissipated", formatter=NumberFormatter(format="0.0")),]

source_table = ColumnDataSource(data=dict(res_ann))

data_table = DataTable(columns=columns, source=source_table,width=600, height=450)
################################################################################################## 
month_val = res_month
yearVal = month_val.index.get_level_values(0)
monthVal = res_month.index.get_level_values(1)

vals = month_val.solarSF_MWh.round(1)

source1 = ColumnDataSource(data=dict(month_vs=monthVal,
                                      year_vs=yearVal,
                                      val_vs=vals))

TOOLTIPS = [
    ("Solar", "@val_vs")
]

p = Figure(y_range=months,
           x_axis_location="below", plot_width=1360, plot_height=480,
           tools=TOOLS, toolbar_location='above', tooltips=TOOLTIPS)

p.grid.grid_line_color = None
p.axis.axis_line_color = 'black'
p.axis.major_tick_line_color = 'black'
p.axis.major_label_text_font_size = "10pt"
p.axis.major_label_standoff = 0

p.xaxis.major_label_orientation = pi / 3

mapper = LinearColorMapper(palette=cc.rainbow, low=0, high=vals.max())
p.rect(x='year_vs', y='month_vs', width=1.0, height=1.0,
       source=source1,
       fill_color={'field': 'val_vs', 'transform': mapper},
       line_color='black')

text_props = {"source": source1, "text_align": "center", "text_baseline": "middle"}
r = p.text(x='year_vs', y='month_vs', text="val_vs", **text_props)
r.glyph.text_font_style="bold"
r.glyph.text_font_size="10pt"

color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="8pt",
                     ticker=BasicTicker(desired_num_ticks=6),
                     formatter=PrintfTickFormatter(format="%d"),
                     label_standoff=6, border_line_color=None, location=(0, 0))
p.add_layout(color_bar, 'right')

#p.add_tools(HoverTool(renderers=[r], tooltips=[('Fecha: ', '@Date{%F}'),
#     ('Pago fósil con SST (kUS$): ', '@fossPay{0.0}'),
#     ('Pago energía solar (kUS$): ', '@solPay{0.0}'),
#     ('Pago total con SST (kUS$): ', '@totPay{0.0}'),
#     ('Pago sin SST (kUS$): ', '@convPay{0.0}')],mode='vline',formatters={'@Date':'datetime'}))
################################################################################################## 
year = 2023

dayVal, monthValue, val = daily_data(resumen,year,'Solar')

y_rg = np.arange(1,32)
y_rg = [str(x) for x in y_rg]

source_day = ColumnDataSource(data=dict(day_vs = dayVal,monthValue=monthValue,val_vs=val))

p1 = Figure(y_range=y_rg,x_range=FactorRange(*months),
           x_axis_location="below", plot_width=1360, plot_height=750,
           tools=TOOLS, toolbar_location='above')

p1.grid.grid_line_color = None
p1.axis.axis_line_color = 'black'
p1.axis.major_tick_line_color = 'black'
p1.axis.major_label_text_font_size = "10pt"
p1.axis.major_label_standoff = 0
p1.axis.axis_label_text_align = 'center'

p1.xaxis.major_label_orientation = pi / 3

mapper1 = LinearColorMapper(palette=cc.rainbow, low=0, high=val.max())
p1.rect(x='monthValue', y='day_vs', width=1.0, height=1.0,
       source=source_day,
       fill_color={'field': 'val_vs', 'transform': mapper1},
       line_color='black')

text_props1 = {"source": source_day, "text_align": "center", "text_baseline": "middle"}
r1 = p1.text(x='monthValue', y='day_vs', text="val_vs", **text_props1)
r1.glyph.text_font_style="bold"
r1.glyph.text_font_size="10pt"

color_bar1 = ColorBar(color_mapper=mapper1, major_label_text_font_size="8pt",
                     ticker=BasicTicker(desired_num_ticks=6),
                     formatter=PrintfTickFormatter(format="%d"),
                     label_standoff=6, border_line_color=None, location=(0, 0))
p1.add_layout(color_bar1, 'right')




def ChangeData(attrname, old, new):
#    loc = dropdownLoc.value
    
    res_plot = dropdownRes.value
    yr = int(yearButtonGroup.active)
    year = yearButton_n[yr]
    
    #'Demand','Solar','Solar storage','Solar direct', 'P2H','Dissipation', 'Solar Fraction'
    if res_plot == 'Demand':
        mapper1.high = maxD_dem
        mapper.high = res_month.demanda_MWh.max()
    elif res_plot == 'Dissipation':
        mapper1.low = res.energ_diss.min()
        mapper1.high = maxD_diss
        mapper.high = res_month.energ_diss.max()
        mapper.low = res_month.energ_diss.min()
    elif res_plot == 'Solar Fraction':
        mapper.high = res_month.sol_frac.max()
        mapper1.high = maxD_sf
    elif res_plot == 'Solar':
        mapper.high = res_month.solar_MWh.max()
        mapper1.high = res.solar_MWh.max()
    
    
    dayVal, monthValue, val = daily_data(resumen,year,res_plot)
    new_data=dict(day_vs = dayVal,monthValue=monthValue,val_vs=val)
    source_day.data = new_data
#    mapper1.high = val.max()
    
    var = param_plot(res_plot)
    vals = month_val[var].round(1)
    
    
    
    new_data=dict(month_vs=monthVal,year_vs=yearVal,val_vs=vals)
    source1.data = new_data
#    mapper.high = vals.max()
    
    
dropdownRes.on_change('value', ChangeData)
dropdownLoc.on_change('value', ChangeData)
yearButtonGroup.on_change('active',ChangeData)

layout = column(data_table,
                row(dropdownRes),
                p,
                yearButtonGroup,
                p1)
curdoc().add_root(layout)