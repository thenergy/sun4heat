#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 20 15:53:27 2022

@author: diego
"""
import numpy as np
import pandas as pd

path = '/home/diego/Documentos/sun4heat/'


meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto',
         'Septiembre','Octubre','Noviembre','Diciembre']

dias = {'Enero':31,'Febrero':28,'Marzo':31,'Abril':30,'Mayo':31,'Junio':30,'Julio':31,'Agosto':31,
         'Septiembre':30,'Octubre':31,'Noviembre':30,'Diciembre':31}

Consumo_anual = {2025:8692, 2026:8125, 2027:7918,
                 2028:7151, 2029:5781, 2030:5204,
                 2031:4662, 2032:4271, 2033:4181,
                 2034:4281, 2035:4337, 2036:4238}

years = np.arange(2025,2037)

Consumo_mensual={'Enero':0.063, 'Febrero':0.067, 'Marzo':0.067,
                 'Abril':0.075, 'Mayo':0.103, 'Junio':0.113,
                 'Julio':0.107, 'Agosto':0.102, 'Septiembre':0.083,
                 'Octubre':0.079, 'Noviembre':0.071, 'Diciembre':0.071,}

#########################################

Tin = 73
Tout = 90
pci = 11.83 # kWh/kg
dens_f = 0.846 # kg/lt
eff_heater = 86
Cp_agua = 4.186 # kJ/(kg K)


for year in years:
    
    temp = []
    
    for mes in meses:
        
        for j in np.arange(1,dias[mes]*24+1):
            temp.append(Consumo_anual[year]*Consumo_mensual[mes])
            
    temp = pd.Series(temp)
    
    temp.to_csv(path + "visualizaciones/swh_bhp_calc/resultados/load_profile_spence/scaled_draw_"+str(year)+".csv", index=False, header=False)
    
    
    
    
    