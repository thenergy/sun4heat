#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 24 14:02:30 2021

@author: fcuevas
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

# función para aplanar lista
def flat_list(lt):
    flat_list = []
    for sublist in lt:
        for item in sublist:
            flat_list.append(item)
            
    return flat_list  

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
path = '/Users/fcuevas/Documents/Trabajo/thenergy/H2_sim'

# nombre de columnas del archivo resultante de la simulación del SAM (1 MW)
header_pv = ['date','sys_pow','ac_pow','dc_pow','mod_temp','poa','tamb','dni','diff','glob']
# leer archivo de resultados del SAM
pv = pd.read_csv(path + '/data/PV_yield.csv',names=header_pv,skiprows=1)
# crear columna índice de tiempo
pv.index = pd.date_range(start='2018-01-01 00:00', end='2018-12-31 23:00', freq='H')

# Potencia instalada sistema FV (MW)
pot_fv = 40

# calcular energía total según la potencia definida
pv['tot_pow'] = pv.sys_pow * pot_fv / 1000

# agua necesaria para producir 1 kg de H2
wat_el = 11

# eficiencia del electrolizador (%)
eff_el = 70

# energía mínima para producir 1 kg de H2 con electrólisis 
enerTeo_h2 = 39

#  energía necesaria para producir 1 kg de H2 con electrólisis
ener_h2 = enerTeo_h2 /(eff_el/100)

pot_el = 2

num_el = 10

ovload_el = 60

max_powEl = num_el * pot_el * (100 + ovload_el)/100


res_tot = pv[['sys_pow','ac_pow','dc_pow','tot_pow']]
res_tot['h2'] = res_tot['tot_pow'] / ener_h2
#res_tot['h2'] = res_tot.loc[:,'tot_pow'] / ener_h2

res_tot['agua'] = res_tot.h2 * wat_el

#res_tot['sys_powMW'] = res_tot['sys_pow']/1000

res_tot['hr_el'] = res_tot['tot_pow'].mask(res_tot.sys_pow > 0,1)




res_tot['hr_elOvLoad'] = res_tot['tot_pow'].mask(res_tot.tot_pow < max_powEl,0)

#res_tot['hr_elOvLoad'] = res_tot['hr_elOvLoad'].mask(res_tot.hr_elOvLoad > 0.999999999,0)