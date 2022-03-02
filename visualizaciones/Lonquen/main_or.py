#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 12:26:09 2022

@author: diegonaranjo
"""


import pandas as pd
import numpy as np

from math import pi
import colorcet as cc

from bokeh.plotting import Figure
from bokeh.models.widgets import  Select, Button, TextInput
from bokeh.models import  DatetimeTickFormatter
from bokeh.layouts import column, Spacer, row
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, LinearColorMapper, ColorBar, BasicTicker, \
PrintfTickFormatter, TableColumn, DataTable, NumberFormatter, PreText
from bokeh.io import curdoc

# meses del año
months = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
mnths = {1:'Enero',
         2:'Febrero',
         3:'Marzo',
         4:'Abril',
         5:'Mayo',
         6:'Junio',
         7:'Julio',
         8:'Agosto',
         9:'Septiembre',
         10:'Octubre',
         11:'Noviembre',
         12:'Diciembre'}

# ruta de la ubicación de la visualizacion
#path = '/Users/fcuevas/Documents/Trabajo/thenergy/H2_sim'
path = '/home/diegonaranjo/Documentos/Thenergy/Lonquen'

# nombre de columnas del archivo
header_lq = ['tv_loos','tv_salcor','tv_visa','tv_desgas','ca_loos','ca_salcor','ca_visa','cg_loos','cg_salcor','cg_visa']
# leer archivo de consumo Lonquen
lq = pd.read_csv(path + '/calderas_lonquen.csv',names=header_lq ,skiprows=2)
# crear columna índice de tiempo
lq.index = pd.date_range(start='2021-01-01', end='2021-12-31', freq='D')

lq["cg_loos"] = lq["cg_loos"].str.replace(",", "")
lq["cg_salcor"] = lq["cg_salcor"].str.replace(",", "")
lq["cg_visa"] = lq["cg_visa"].str.replace(",", "")

lq.cg_loos = pd.to_numeric(lq.cg_loos, errors="coerce")
lq.cg_salcor = pd.to_numeric(lq.cg_salcor, errors="coerce")
lq.cg_visa = pd.to_numeric(lq.cg_visa, errors="coerce")


res_tot = lq[['tv_loos','tv_salcor','tv_visa','tv_desgas','ca_loos','ca_salcor','ca_visa','cg_loos','cg_salcor','cg_visa']]

res_month = res_tot.groupby([res_tot.index.year,res_tot.index.month]).sum()
res_month = res_month.reset_index()
res_month['Meses'] = res_month.level_1.map(mnths)

month_max = res_tot.groupby([res_tot.index.year,res_tot.index.month]).max()
month_max = month_max.reset_index()
month_max['Meses'] = month_max.level_1.map(mnths)


source_month = ColumnDataSource(data=res_month)

cols_month = [
        TableColumn(field="Meses", title="Mes",width=60),     
        TableColumn(field="tv_loos", title="Ton vapor loos",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="tv_salcor", title="Ton vapor salcor",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="tv_visa", title="Ton vapor visa",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="tv_desgas", title="Ton vapor desgasificador",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="ca_loos", title="Consumo agua loos",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="ca_salcor", title="Consumo agua salcor",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="ca_visa", title="Consumo agua visa",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="cg_loos", title="Consumo GN loos",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="cg_salcor", title="Consumo GN salcor",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="cg_visa", title="Consumo GN visa",width=150, formatter=NumberFormatter(format="0"))]

    


table_month = DataTable(columns=cols_month, source=source_month,width=600, height=450,
                        editable=True)



# #################################
wdt = 250

eqp_opt = ["Caldera Loos", "Caldera Salcor", "Caldera Visa", "Desgasificador (solo Ton Vapor)"]
equip_butt = Select(value="Caldera Loos", title="Potencia FV (MW)", options =eqp_opt, width=wdt)
proc_butt = Select(value="Ton vapor", title="Tipo de proceso",options = ["Ton vapor, consumo agua, consumo GN"], width=wdt)

eqp_opt = ["Caldera Loos", "Caldera Salcor", "Caldera Visa", "Desgasificador (solo Ton Vapor)"]
dropdownRes = Select(value="Caldera Loos", title="Equipo Térmico",options=eqp_opt,width=300) 

menuVar=["Ton Vapor","Consumo agua","Consumo GN"]
dropdownVar = Select(value="Ton Vapor", title="Variable de interés",options=menuVar,width=300) 

buttFiltUpdate = Button(label="Filtrar", button_type="success",width=wdt)

res = 'tv_loos'
day_val = res_tot[res].groupby([res_tot.index.year,res_tot.index.month,res_tot.index.day]).sum()
day_val = day_val.reset_index()

day_val['months'] = day_val.level_1.map(mnths)

dayVal = day_val.level_2
monthValue = day_val.months
val = day_val[res].round(1) 

source_day = ColumnDataSource(data=dict(day_vs = dayVal,monthValue=monthValue,val_vs=val))

y_rg = np.arange(1,32)
y_rg = [str(x) for x in y_rg]




# ################################################################################################## 
TOOLS="hover,crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select"
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





def ChangeData():
    
    res_month = res_tot.groupby([res_tot.index.year,res_tot.index.month]).sum()
    res_month = res_month.reset_index()
    res_month['Meses'] = res_month.level_1.map(mnths)
    
    month_max = res_tot.groupby([res_tot.index.year,res_tot.index.month]).max()
    month_max = month_max.reset_index()
    month_max['Meses'] = month_max.level_1.map(mnths)
    

    new_data = dict(res_month)
    source_month.data = new_data

    
    men = dropdownRes.value
    
    var = dropdownVar.value
    
    if var == "Ton Vapor":
        if men == "Caldera Loos":
            res = 'tv_loos'
            
        elif men == "Caldera Salcor":
            res = 'tv_salcor'
            
        elif men == "Caldera Visa":
            res = 'tv_visa'
        
        elif men == "Desgasificador (solo Ton Vapor)":
            res = 'tv_desgas'   
            
    elif var == "Consumo agua":
        if men == "Caldera Loos":
            res = 'ca_loos'
            
        elif men == "Caldera Salcor":
            res = 'ca_salcor'
            
        elif men == "Caldera Visa":
            res = 'ca_visa'
    elif var == "Consumo GN":
        if men == "Caldera Loos":
            res = 'cg_loos'
            
        elif men == "Caldera Salcor":
            res = 'cg_salcor'
            
        elif men == "Caldera Visa":
            res = 'cg_visa'
    
    
    day_val = res_tot[res].groupby([res_tot.index.year,res_tot.index.month,res_tot.index.day]).sum()
    day_val = day_val.reset_index()
    
    day_val['months'] = day_val.level_1.map(mnths)
    
    dayVal = day_val.level_2
    monthValue = day_val.months
    val = day_val[res].round(1) 
    
    new_data=dict(day_vs = dayVal,monthValue=monthValue,val_vs=val)
    source_day.data = new_data









buttFiltUpdate.on_click(ChangeData)
##############
spc = 50
layout = column(Spacer(height=spc),

                row(dropdownRes),
                row(dropdownVar),
                row(buttFiltUpdate),
                row(p1,column(table_month))
                )
############################################
curdoc().add_root(layout)