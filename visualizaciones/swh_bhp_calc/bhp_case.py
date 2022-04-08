#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 12:01:53 2022

@author: diego
"""

import pandas as pd
import numpy as np
import sys
sys.path



path = '/home/diego/Documentos/sun4heat/'

sys.path.append('/home/diego/Documentos/sun4heat/scripts')

from funciones_bhp_SAM import CallSWH, SetTurno, SetTMains, SetTSet, CopyRadFile
from funciones import Col_eff_val

#############################################################
#       PARAMETROS PROCESO BHP
#############################################################

years = np.arange(2024,2045)

# temperatura de entrada al proceso
Tin_p = 73
# temperatura de salida del proceso
Tout_p = 90
pci = 11.83 # kWh/kg
dens_f = 0.846 # kg/lt
eff_heater = 86
Cp_agua = 4.186 # kJ/(kg K)

################################
#############################################################
#   GENERACIÓN ARCHIVO POR UBICACIÓN
#############################################################

minas = pd.read_csv('/home/diego/Documentos/sun4heat/datos/radiacion_solar/minas_bhp.csv',sep=',')
lugar = 'Escondida'
data_lugar = minas[minas.Mina == lugar]
ghi_sg = data_lugar.GHI_SG.iloc[0]
dataSol = 'Explorador Solar'

df = CopyRadFile(lugar,dataSol) 

###############################################################
#   SETs
###############################################################
turno = "24/7"
flow_p = 757155.9535104365 #caso 1
    
SetTurno(df,turno, flow_p)
SetTMains(df,Tout_p)
SetTSet(df,Tin_p)


#############################################################
#   CÁLCULOS COLECTOR
#############################################################

# Potencia heater
# heater_pow = flow_p*dens_f*(Tin_p - Tout_p)*Cp_agua/3600

Col = 'GreenOneTec GK_SG'
#Area de colector
aCol = 1800
#Temperatura media del colector
Tmean = (Tin_p + Tout_p)/2.
# Eficiencia del colector
eff_col = Col_eff_val(Col,Tmean,25,1000)
# area de la planta solar peak
# peak_plant = heater_pow/eff_col * 1.1
#inclinación campo solar
tilt = 0
#azimuth campos solar
azim = 0
# Volumen almacenamiento
vol = 180
# Porcentaje pérdidas del almacenamiento
sto_loss=10

for year in years:

    df = CallSWH(df,tilt,azim,Col,aCol,vol,sto_loss,year)
    df.to_csv(path + 'visualizaciones/swh_bhp_calc/Datos_temp/dat_hora_sim_'+str(year)+'.csv')


# dias = [31,28,31,30,31,30,30,31,30,31,30,31]


# for year in years:
#     flujo_agua = pd.read_csv(path + 'visualizaciones/BHP_vinc/load_profile/scaled_draw_' + str(year) + '.csv', names=["flujo"])
#     f_mensuales = list(flujo_agua.flujo.unique())
    
#     for flujo in f_mensuales:
#         mes = 1
#         SetTurno(df,turno, flujo)
        
#         mes = mes+1


        
        

# enerProc, enerAux, enerSol, enerPeak, enerSto = BalanceMonth(df)







