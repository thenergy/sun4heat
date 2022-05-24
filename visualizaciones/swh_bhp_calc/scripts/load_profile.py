#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 23 12:56:31 2022

@author: diego
"""

import pandas as pd
import numpy as np

path = '/home/diego/Documentos/sun4heat/'


# meses del año
months = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

mnths_spence = {1:{'nombre':'Enero',      'perc':0.063,    'dias':31},
         2:{'nombre':'Febrero',    'perc':0.067,    'dias':28},
         3:{'nombre':'Marzo',      'perc':0.067,    'dias':31},
         4:{'nombre':'Abril',      'perc':0.075,    'dias':30},
         5:{'nombre':'Mayo',       'perc':0.103,    'dias':31},
         6:{'nombre':'Junio',      'perc':0.113,    'dias':30},
         7:{'nombre':'Julio',      'perc':0.107,   'dias':31},
         8:{'nombre':'Agosto',     'perc':0.102,    'dias':31},
         9:{'nombre':'Septiembre', 'perc':0.083,    'dias':30},
         10:{'nombre':'Octubre',   'perc':0.079,      'dias':31},
         11:{'nombre':'Noviembre', 'perc':0.071,    'dias':30},
         12:{'nombre':'Diciembre', 'perc':0.071,    'dias':31}}


years_spence = np.arange(2025,2037)

dem_spence = {2025:8692, 2026:8125, 2027:7918,
                 2028:7151, 2029:5781, 2030:5204,
                 2031:4662, 2032:4271, 2033:4181,
                 2034:4281, 2035:4337, 2036:4238}

mnths_escondida = {1:{'nombre':'Enero',      'perc':6.9,    'dias':31},
         2:{'nombre':'Febrero',    'perc':6.3,    'dias':28},
         3:{'nombre':'Marzo',      'perc':7.5,    'dias':31},
         4:{'nombre':'Abril',      'perc':8.8,    'dias':30},
         5:{'nombre':'Mayo',       'perc':9.7,    'dias':31},
         6:{'nombre':'Junio',      'perc':9.6,    'dias':30},
         7:{'nombre':'Julio',      'perc':10.5,   'dias':31},
         8:{'nombre':'Agosto',     'perc':9.9,    'dias':31},
         9:{'nombre':'Septiembre', 'perc':9.1,    'dias':30},
         10:{'nombre':'Octubre',   'perc':8,      'dias':31},
         11:{'nombre':'Noviembre', 'perc':6.6,    'dias':30},
         12:{'nombre':'Diciembre', 'perc':7.1,    'dias':31}}

years_escondida = np.arange(2024,2045)

dem_escondida = {2024: 18750,
       2025: 17667,
       2026: 19436,
       2027: 19915,
       2028: 17031,
       2029: 14892,
       2030: 16848,
       2031: 17693,
       2032: 16335,
       2033: 16527,
       2034: 16033,
       2035: 13503,
       2036: 11724,
       2037: 11660,
       2038: 11526,
       2039: 11409,
       2040: 11276,
       2041: 10874,
       2042: 9424,
       2043: 7835,
       2044: 7063}

Tin = 73
Tout = 90
pci = 11.83 # kWh/kg
dens_f = 0.846 # kg/lt
eff_heater = 86
Cp_agua = 4.186 # kJ/(kg K)

def lp_Spence(Tout,Tin):
    for year in years_spence:
        # print ('###########################')
        # print(dem_spence[year])
        # print ('###########################')
        if year in (2024,2028,2032,2036,2040,2044):
            ds = np.arange(1,8785)
        else:
            ds = np.arange(1,8761)
        ds = pd.DataFrame(ds)
        ds.index = pd.date_range(start=str(year) + '-01-01 00:00', end=str(year) + '-12-31 23:00', freq='H')
    #    ds.index = pd.date_range(start='2022-01-01 00:00', end='2022-12-31 23:00', freq='H')
        
        # Calcular la cantidad de combustible por hora (m3/hr)
        a = []
        for mth in np.arange(1,13):
            fuel = dem_spence[year] * mnths_spence[mth]['perc'] / (mnths_spence[mth]['dias'] *24)
            # print (str(fuel) + " m3/h")
            a.append(fuel)
            
        fl = pd.Series(a)
        fl.index = np.arange(1,13)    
        ds['fuel_hr'] = ds.index.month.map(fl)
        ds['ener_proc'] = ds.fuel_hr * eff_heater/100 * 1000 * dens_f * pci / 1000
        ds['flujo'] = ds.ener_proc / (Cp_agua * (Tout-Tin)/3600/1000)
        print ("load_profile año: " + str(year) +" para Spence creado")
        ds['flujo'][:8760].to_csv(path + "visualizaciones/swh_bhp_calc/resultados/load_profile_spence/scaled_draw_" + str(year) + ".csv", index=False, header=False)
        

def lp_Escondida(Tout,Tin):
    for year in years_escondida:
        # print ('###########################')
        # print(dem_escondida[year])
        # print ('###########################')
        if year in (2024,2028,2032,2036,2040,2044):
            ds = np.arange(1,8785)
        else:
            ds = np.arange(1,8761)
        ds = pd.DataFrame(ds)
        ds.index = pd.date_range(start=str(year) + '-01-01 00:00', end=str(year) + '-12-31 23:00', freq='H')
    #    ds.index = pd.date_range(start='2022-01-01 00:00', end='2022-12-31 23:00', freq='H')
        
        # Calcular la cantidad de combustible por hora (m3/hr)
        a = []
        for mth in np.arange(1,13):
            fuel = dem_escondida[year] * mnths_escondida[mth]['perc'] / 100 / (mnths_escondida[mth]['dias'] *24)
            # print (str(fuel) + " m3/h")
            a.append(fuel)
            
        fl = pd.Series(a)
        fl.index = np.arange(1,13)    
        ds['fuel_hr'] = ds.index.month.map(fl)
        ds['ener_proc'] = ds.fuel_hr * eff_heater/100 * 1000 * dens_f * pci / 1000
        ds['flujo'] = ds.ener_proc / (Cp_agua * (Tout-Tin)/3600/1000)
        print ("load_profile año: " + str(year) +" para Escondida creado")

        ds['flujo'][:8760].to_csv(path + "visualizaciones/swh_bhp_calc/resultados/load_profile/scaled_draw_" + str(year) + ".csv", index=False, header=False)
        




