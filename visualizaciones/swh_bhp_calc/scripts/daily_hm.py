# -*- coding: utf-8 -*-
"""
Created on Wed Jan 26 12:26:09 2022

@author: diegonaranjo
"""


import pandas as pd
import numpy as np

from math import pi
import colorcet as cc

from bokeh.plotting import Figure, show
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
path = '/home/diego/Documentos/sun4heat/'

year = 2025

def day_HMCreate(year):
# leer archivo de balance diario
bal_day = pd.read_csv(path + 'visualizaciones/swh_bhp_calc/resultados/balances_diarios_mensuales/balance_año_'+ str(year) +'.csv')

# crear columna índice de tiempo
bal_day.index = pd.date_range(start=str(year)+'-01-01', end=str(year)+'-12-31', freq='D')

#Eliminar primera columna
bal_day = bal_day.iloc[: , 1:]


bal_tot = bal_day[bal_day.columns.values.tolist()]




bal_month = bal_tot.groupby([bal_tot.index.year,bal_tot.index.month]).sum()
bal_month = bal_month.reset_index()
bal_month['Meses'] = bal_month.level_1.map(mnths)

month_max = bal_tot.groupby([bal_tot.index.year,bal_tot.index.month]).max()
month_max = month_max.reset_index()
month_max['Meses'] = month_max.level_1.map(mnths)


source_month = ColumnDataSource(data=bal_month)




# # #################################
wdt = 250

# energias = ["Energía Solar", "Bomba de calor", "Caldera eléctrica"]

# proc_butt = Select(value="Energía solar", title="Tipo de energía",options = energias, width=wdt)



# menuVar=["Ton Vapor","Consumo agua","Consumo GN"]
# dropdownVar = Select(value="Ton Vapor", title="Variable de interés",options=menuVar,width=300) 

buttFiltUpdate = Button(label="Filtrar", button_type="success",width=wdt)

bal = 'enerSol'
day_val = bal_tot[bal].groupby([bal_tot.index.year,bal_tot.index.month,bal_tot.index.day]).sum()
day_val = day_val.reset_index()

day_val['months'] = day_val.level_1.map(mnths)

dayVal = day_val.level_2
monthValue = day_val.months
val = day_val[bal].round(1)

source_day = ColumnDataSource(data=dict(day_vs = dayVal,monthValue=monthValue,val_vs=val))


# ##

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


p1.rect(x='monthValue', y='day_vs', width=1.0, height=1,
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
    
    bal_month = bal_tot.groupby([bal_tot.index.year,bal_tot.index.month]).sum()
    bal_month = bal_month.reset_index()
    bal_month['Meses'] = bal_month.level_1.map(mnths)
    
    month_max = bal_tot.groupby([bal_tot.index.year,bal_tot.index.month]).max()
    month_max = month_max.reset_index()
    month_max['Meses'] = month_max.level_1.map(mnths)
    

    new_data = dict(bal_month)
    source_month.data = new_data

       
    var = proc_butt.value
    
    if var == "Energía Solar":
            bal = 'enerSol'
            
    elif var == "Bomba de calor":
            bal = 'enerHPump_util'

    else:     
            bal = 'enerCald_util'
    
    day_val = bal_tot[bal].groupby([bal_tot.index.year,bal_tot.index.month,bal_tot.index.day]).sum()
    day_val = day_val.reset_index()
    
    
    
    day_val['months'] = day_val.level_1.map(mnths)

    
    dayVal = day_val.level_2
    monthValue = day_val.months
    val = day_val[bal].round(1) 
    

    
    mapper1.high = val.max()
    mapper1.low = val.min()
    
    new_data=dict(day_vs = dayVal,monthValue=monthValue,val_vs=val)
    
    # source_day.data = new_data
    
    return new_data




buttFiltUpdate.on_click(ChangeData)
##############
spc = 50
layout = column(Spacer(height=spc),

                # row(dropdownbal),
                row(proc_butt),
                row(buttFiltUpdate),
                row(p1),
                
                # Spacer(height=spc),
                                
                # row(p2,column(table_week))

                )
############################################
curdoc().add_root(layout)



















