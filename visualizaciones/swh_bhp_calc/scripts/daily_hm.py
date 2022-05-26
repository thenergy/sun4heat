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
    
    
    
    bal = 'enerSol'
    day_val = bal_tot[bal].groupby([bal_tot.index.year,bal_tot.index.month,bal_tot.index.day]).sum()
    day_val = day_val.reset_index()
    
    day_val['months'] = day_val.level_1.map(mnths)
    
    dayVal = day_val.level_2
    monthValue = day_val.months
    val = day_val[bal].round(1)
    
    source_day = ColumnDataSource(data=dict(day_vs = dayVal,monthValue=monthValue,val_vs=val))
    
    return val, source_day




def ChangeData(year, dis,var):
    
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
    

    new_data = dict(bal_month)
    # source_month.data = new_data

    
    if dis == "Energía Solar":
        if var == 'MWh':
            bal = 'enerSol'
           
        elif var == 'MW':
            bal = 'enerSol_MW'
        else:
            bal = 'SF'
               
            
    elif dis == "Bomba de calor":
        if var == 'MWh':
            bal = 'enerHPump_util'
           
        elif var == 'MW':
            bal = 'enerHPump_util_MW'
        else:
            bal = 'HPumpF'


    else:    
        if var == 'MWh':
            bal = 'enerCald_util'
           
        elif var == 'MW':
            bal = 'enerCald_util_MW'
        else:
            bal = 'CaldF'
    
    day_val = bal_tot[bal].groupby([bal_tot.index.year,bal_tot.index.month,bal_tot.index.day]).sum()
    day_val = day_val.reset_index()
    
    
    
    day_val['months'] = day_val.level_1.map(mnths)

    
    dayVal = day_val.level_2
    monthValue = day_val.months
    val = day_val[bal].round(1) 
    

    
    # mapper1.high = val.max()
    # mapper1.low = val.min()
    
    new_data=dict(day_vs = dayVal,monthValue=monthValue,val_vs=val)
    
    # source_day.data = new_data
    
    return val, new_data
























