#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 16:26:59 2019

@author: fcuevas
"""

import numpy as np
import pandas as pd
import shutil
import os

#from funciones_econ import Vector

from funciones_SAM import SetTurno
from iapws import IAPWS97

#Propiedades del agua
# densidad (kg/m3)
dens_w = 1000

# Calor específico agua (kJ/(kg*K))
cp_w = 4.18 

meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']

years = np.arange(2024,2045)

#path = '/Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/'
# path = '/home/diegonaranjo/Documentos/Thenergy/sun4heat/'
# path = '/home/ubuntu/Thenergy/diego/sun4heat/'

path = '/home/diego/Documentos/sun4heat/'

################################### COLECTORES SOLARES ###################################
cst = {'TVP MT-Power v4':          {'n0':0.737,'a1':0.504,'a2':0.00600,'color':'red'},
       'Sunmark HT-SolarBoost':    {'n0':0.850,'a1':2.300,'a2':0.02900,'color':'green'},
       'Chromagen':                {'n0':0.722,'a1':3.390,'a2':0.01400,'color':'blue'},
       'Ecopanel':                 {'n0':0.640,'a1':3.549,'a2':0.02567,'color':'black'},
       'Shüco':                    {'n0':0.806,'a1':3.882,'a2':0.00900,'color':'orange'},
       'Termic':                   {'n0':0.725,'a1':3.359,'a2':0.01500,'color':'magenta'},
       'GreenOneTec GK_SG':        {'n0':0.857,'a1':3.083,'a2':0.01300,'color':'olive'},
       'GreenOneTec GK_DG':        {'n0':0.814,'a1':2.102,'a2':0.01600,'color':'olive'},
       'Bosch':                    {'n0':0.802,'a1':3.833,'a2':0.01500,'color':'cyan'},
       'Viessman':                 {'n0':0.819,'a1':4.342,'a2':0.03600,'color':'slategray'},
       'Piscina':                  {'n0':0.850,'a1':18.00,'a2':0.00000,'color':'slategray'},
       'Savosolar':                {'n0':0.874,'a1':3.160,'a2':0.00980,'color':'black'},
       'Sunoptimo':                {'n0':0.824,'a1':2.905,'a2':0.00300,'color':'black'}}


################################### COMBUSTIBLES ###################################
# Factor de emisiones
# http://www.declaracionemision.cl/docs/GUIA_CONAMA.pdf

# Densidad y PCI
# https://www.engineeringtoolbox.com/fuels-higher-calorific-values-d_169.html
cmb = {'Diesel':        {'PCI_kg' : 11.83, 'dens':0.846,'dens_real':99999,'f_em':3.12,'unidad':'(m3/año)'},
       'GN':            {'PCI_kg' : 13.10, 'dens':0.777,'dens_real':99999,'f_em':2.69,'unidad':'(miles m3/año)'},
       'GLP':           {'PCI_kg' : 12.64, 'dens':1.000,'dens_real':0.537,'f_em':2.82,'unidad':'(ton/año)'},
       'Kerosene':      {'PCI_kg' : 11.94, 'dens':0.821,'dens_real':99999,'f_em':3.12,'unidad':'(m3/año)'},
       'Carbón':        {'PCI_kg' :  7.89, 'dens':1.000,'dens_real':99999,'f_em':2.34,'unidad':'(ton/año)'},
       'Petróleo 5':    {'PCI_kg' : 11.28, 'dens':0.960,'dens_real':99999,'f_em':3.09,'unidad':'(m3/año)'},
       'Petróleo 6':    {'PCI_kg' : 10.83, 'dens':0.980,'dens_real':99999,'f_em':3.13,'unidad':'(m3/año)'}, 
       'Leña':          {'PCI_kg' : 4.280, 'dens':1.000,'dens_real':0.701,'f_em':1.03,'unidad':'(ton/año)'},
       'Biomasa':       {'PCI_kg' : 7.110, 'dens':1.000,'dens_real':1.000,'f_em':2.00,'unidad':'(ton/año)'}}


combs = {'Diesel':        {'PCI_kg' : 11.83, 'dens':0.846,'dens_real':99999,'f_em':3.12,'unidad':'(m3/año)','nombre':'Diesel'},
         'GN':            {'PCI_kg' : 13.10, 'dens':0.777,'dens_real':99999,'f_em':2.69,'unidad':'(miles m3/año)','nombre':'GNL'},
         'GLP':           {'PCI_kg' : 12.64, 'dens':1.000,'dens_real':0.537,'f_em':2.82,'unidad':'(ton/año)','nombre':'GLP'}}


def TableRad(df_tmp):
    '''
    Genera una tabla con la suma de la  irradiancia horizontal directa  (GHI) y
    la irradiancia directa en un panel (POA)
    Parameters
    ----------
    df_tmp : DataFrame
        DESCRIPTION.

    Returns
    -------
    table_rad : Series
        DESCRIPTION.

    ''' 
    table_rad = pd.Series()
    table_rad['GHI (kWh/m2/año): '] = "{:10.1f}".format(df_tmp.ghi.sum()/1000)
    table_rad['POA (kWh/m2/año): '] = "{:10.1f}".format(df_tmp.poa.sum()/1000)    
    table_rad['DNI (kWh/m2/año): '] = "{:10.1f}".format(df_tmp.dni.sum()/1000)    
    return table_rad

    

def Col_eff_val(Col, Tmean, Tamb, GHI):
    '''
    Calcula la eficiencia del colector bajo el modelo de regresión :
    
    Ef = Ef_o - a_1 * DeltaT/G - a_2 * DeltaT**2/G
    

    Parameters
    ----------
    Col : str
        Tipo de colector.
    Tmean : int
        Temperatura media del estanque.
    Tamb : int
        Temperatura del ambiente.
    GHI : int64.
        Radiación global horizontal.

    Returns
    -------
    eff : float
        Eficiencia del colector utilizado.

    '''
    eff = cst[Col]['n0'] - cst[Col]['a1']*(Tmean - Tamb)/GHI - cst[Col]['a2']*(Tmean - Tamb)**2/GHI
    return eff


def Vector(val,contrato,infl):
    n = contrato+1
    vct = np.zeros(n).reshape(n,1) #??
    anhos = np.arange(1,n)
    for anho in anhos:
        if anho == 1:
            vct[anho] = val
        else:
            vct[anho] = vct[anho-1]*(1+infl/100)
        
    return vct
###################################
def flat_list(lt):
    '''
    

    Parameters
    ----------
    lt : TYPE
        DESCRIPTION.

    Returns
    -------
    flat_list : TYPE
        DESCRIPTION.

    '''
    flat_list = []
    for sublist in lt:
        for item in sublist:
            flat_list.append(item)
            
    return flat_list  



def RadMonth(df_temp):
    '''
    Agrupa/suma por/la irradiancia horizontal directa  (GHI) y
    la irradiancia directa en un panel (POA)
 
    Parameters
    ----------
    df_temp : DataFrame
        DESCRIPTION.

    Returns
    -------
    rad_month : list
        Radiación mensual.
    x_month : list
        mes y proceso

    '''
    rads = ['GHI','POA']
    rad_months_ghi = df_temp['ghi'].groupby(df_temp.index.month).sum()/1000
    rad_months_poa = df_temp['poa'].groupby(df_temp.index.month).sum()/1000
    
    rad_month = [(ghi,poa) for ghi,poa in zip(rad_months_ghi,rad_months_poa)]
    rad_month = flat_list(rad_month)
    
    
    x_month = [(month,rad) for month in meses for rad in rads]
    return rad_month,x_month


def BalanceYear(df_temp):   
    '''
    Los datos obtenidos por hora los suma y convierte en datos mensuales.

    Parameters
    ----------
    df_temp : DataFrame
        DESCRIPTION.

    Returns
    -------
    enerProc : Series
        Calor utilizado en el proceso en una hora.
    enerAux : Series
        Energía extra necesitada (no cubiarta por sistema solar).
    enerSol : Series
        DESCRIPTION.
    enerPeak : Series
        DESCRIPTION.
    enerDis : TYPE
        DESCRIPTION.

    '''
    enerSol = df_temp['Qgross'].groupby(df_temp.index.year).sum()/1000
    enerSol = df_temp['Qgross'].groupby(df_temp.index.year).sum()/1000 
    
    enerProc= df_temp['Qproc'].groupby(df_temp.index.year).sum()/1000
    
    esol = []
    edis = []
    for eSol,eProc in zip(enerSol,enerProc):
        if eSol - eProc > 0:
            esol.append(eProc)
            edis.append(eSol-eProc)
        else:
            esol.append(eSol)
            edis.append(0)
                
    # enerSol = pd.Series(esol,index=np.arange(1,13))
    enerAux = enerProc - enerSol
    enerSto = df_temp['Qsto'].groupby(df_temp.index.year).sum()/1000
    enerPeak = df_temp['Qpeak'].groupby(df_temp.index.year).sum()/1000
    
    bal_year = pd.DataFrame(enerProc,index=np.arange(1,21))
    bal_year['Qsol'] = enerSol
    bal_year['SF'] = bal_year.Qsol / bal_year.Qproc * 100
    bal_year = bal_year.rename(columns={'Qproc':'enerProc','Qsol':'enerSol'})
    
    bal_year.to_csv(path + 'visualizaciones/swh_bhp_calc/balance_anual.csv')
    
    return  enerProc, enerAux, enerSol, enerPeak, enerSto #, enerDis

def BalanceMonth(df_temp):   
    '''
    Los datos obtenidos por hora los suma y convierte en datos mensuales.

    Parameters
    ----------
    df_temp : DataFrame
        DESCRIPTION.

    Returns
    -------
    enerProc : Series
        Calor utilizado en el proceso en una hora.
    enerAux : Series
        Energía extra necesitada (no cubiarta por sistema solar).
    enerSol : Series
        DESCRIPTION.
    enerPeak : Series
        DESCRIPTION.
    enerDis : TYPE
        DESCRIPTION.

    '''
    enerSol = df_temp['Qgross'].groupby(df_temp.index.month).sum()/1000
    enerSol = df_temp['Qgross'].groupby(df_temp.index.month).sum()/1000 
    
    enerProc= df_temp['Qproc'].groupby(df_temp.index.month).sum()/1000
    
    esol = []
    edis = []
    for eSol,eProc in zip(enerSol,enerProc):
        if eSol - eProc > 0:
            esol.append(eProc)
            edis.append(eSol-eProc)
        else:
            esol.append(eSol)
            edis.append(0)
                
    enerSol = pd.Series(esol,index=np.arange(1,13))
    enerAux = enerProc - enerSol
    enerSto = df_temp['Qsto'].groupby(df_temp.index.month).sum()/1000
    enerPeak = df_temp['Qpeak'].groupby(df_temp.index.month).sum()/1000
    
    bal_month = pd.DataFrame(enerProc,index=np.arange(1,13))
    bal_month['Qsol'] = enerSol
    bal_month['SF'] = bal_month.Qsol / bal_month.Qproc * 100
    bal_month = bal_month.rename(columns={'Qproc':'enerProc','Qsol':'enerSol'})
    
    bal_month.to_csv(path + 'visualizaciones/swh_calc/balance_mensual.csv')
    
    return  enerProc, enerAux, enerSol, enerPeak, enerSto #, enerDis
 
def SystemYear(df_temp):
    ener = ['Proceso','Caldera','Solar']
#    proc = df_temp['Qproc'].groupby(df_temp.index.month).sum()/1000
#    aux = df_temp['Qaux'].groupby(df_temp.index.month).sum()/1000
#    col = df_temp['Qdel'].groupby(df_temp.index.month).sum()/1000
    
    yearProc, yearAux, yearSol, yearPeak, yearSto = BalanceYear(df_temp)
    
    ener_year = [(total,heater,solar) for total,heater,solar in zip(yearProc,yearAux,yearSol)]
    ener_year = flat_list(ener_year)
    
    x_year = [(year,enr) for year in years for enr in ener]
    return ener_year, x_year 

  
def SystemMonth(df_temp):
    ener = ['Proceso','Caldera','Solar']
#    proc = df_temp['Qproc'].groupby(df_temp.index.month).sum()/1000
#    aux = df_temp['Qaux'].groupby(df_temp.index.month).sum()/1000
#    col = df_temp['Qdel'].groupby(df_temp.index.month).sum()/1000
    
    monthProc, monthAux, monthSol, monthPeak, monthSto = BalanceMonth(df_temp)
    
    ener_month = [(total,heater,solar) for total,heater,solar in zip(monthProc,monthAux,monthSol)]
    ener_month = flat_list(ener_month)
    
    x_month = [(month,enr) for month in meses for enr in ener]
    return ener_month, x_month


def TableEner(df_temp,flow_p, Tout_h, Tin_h,eff_heater,Col):
    '''
    Genera una tabla (Pandas Serie) que contiene información respecto
    a la caldera, sistema solar y balance de energía 

    Parameters
    ----------
    df_temp : TYPE
        DESCRIPTION.
    flow_p : TYPE
        DESCRIPTION.
    Tout_h : TYPE
        DESCRIPTION.
    Tin_h : TYPE
        DESCRIPTION.
    eff_heater : TYPE
        DESCRIPTION.
    Col : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    
    heater_pow = flow_p*dens_w*(Tout_h - Tin_h)*cp_w/3600
    #Temperatura media del colector
    Tmean = (Tin_h + Tout_h)/2.
    # Eficiencia del colector
    eff_col = Col_eff_val(Col,Tmean,25,1000)
    # area de la planta solar peak
    peak_plant = heater_pow/eff_col * 1.1
    
    monthProc, monthAux, monthSol, monthPeak, monthSto = BalanceMonth(df_temp)
    
    procAnnual = monthProc.sum()
    auxAnnual = monthAux.sum()
    colAnnual = monthSol.sum()
#    disAnnual = monthDis.sum()
    
    table_ener = pd.Series()
    table_ener['Caldera'] = ''
    table_ener['Potencia caldera (kW)'] = "{:10.1f}".format(heater_pow)
    table_ener['Potencia caldera (kcal/hr)'] = "{:10.1f}".format(heater_pow*3600/4.184)
    table_ener['Potencia caldera (BHP)'] = "{:10.1f}".format(heater_pow*0.101942)
    table_ener['---------'] = '---------'
    
    table_ener['Sistema solar']  = ''
    table_ener['Colector solar'] = Col
    table_ener['Eficiencia óptica'] = cst[Col]['n0']
    table_ener['Eficiencia térmica u1'] = cst[Col]['a1']
    table_ener["Tamaño planta peak (m2)"] =    "{:10.1f}".format(peak_plant)
    table_ener['Fracción solar: (%)'] = "{:10.1f}".format(colAnnual / procAnnual * 100)
    table_ener['----------'] = '----------'
    
    table_ener['Balance energía']  = ''
    table_ener['Demanda energía proceso (MWh/año): '] = "{:10.1f}".format(procAnnual)
    table_ener['Demanda energía convencional(MWh/año): '] = "{:10.1f}".format(procAnnual/(eff_heater/100))
    table_ener['Generación caldera (MWh/año): '] = "{:10.1f}".format(auxAnnual/(eff_heater/100))
    table_ener['Generación solar (MWh/año): '] = "{:10.1f}".format(colAnnual)
    table_ener['Reemplazo solar equivalente (MWh/año): '] = "{:10.1f}".format(colAnnual/(eff_heater/100))
#    table_ener['Energía solar disipada (MWh/año): '] = "{:10.1f}".format(disAnnual)
    
    return table_ener


def TableFuel(df_temp,fuel,eff_heater):
    
    table_fuel = pd.Series()
    
    monthProc, monthAux, monthSol, monthPeak, monthSto = BalanceMonth(df_temp)
    
    procAnnual = monthProc.sum()
    auxAnnual = monthAux.sum()
    colAnnual = monthSol.sum()
    
    f_em = cmb[fuel]['f_em']
    PCI_kg = cmb[fuel]['PCI_kg']
    dens = cmb[fuel]['dens']
    
    dem_fuel = procAnnual/(eff_heater/100)/(PCI_kg*dens)
    cons_fuel = auxAnnual/(eff_heater/100)/(PCI_kg*dens)
    ahor_fuel = colAnnual/(eff_heater/100)/(PCI_kg*dens)
    
    table_fuel[fuel] = ''
    table_fuel['PCI (kWh/kg)'] = PCI_kg
    table_fuel['Demanda ' + fuel + ' ' + cmb[fuel]['unidad']] = "{:10.1f}".format(dem_fuel)
    table_fuel['Consumo ' + fuel + ' ' + cmb[fuel]['unidad']] = "{:10.1f}".format(cons_fuel)
    table_fuel['Ahorro ' + fuel + ' ' + cmb[fuel]['unidad']] = "{:10.1f}".format(ahor_fuel)
    table_fuel['---------'] = '---------'
    table_fuel['Emisiones'] = ''
    table_fuel['Factor de emisión (kg CO2/kg ' + fuel + ')'] = f_em
    table_fuel['Total emisiones (ton/año)'] = "{:10.1f}".format(dem_fuel*dens * f_em)
    table_fuel['Emisiones emitidas (ton/año)'] = "{:10.1f}".format(cons_fuel*dens * f_em)
    table_fuel['Emisiones desplazadas (ton/año)'] = "{:10.1f}".format(ahor_fuel*dens * f_em)
        
    return table_fuel



def TableFuel_LCOH(fuel,CFuel,eff_heater,annSol,solFrac):
    
    table_fuel = pd.Series()
    
    colAnnual = annSol
    procAnnual = colAnnual/(solFrac/100)
    auxAnnual = procAnnual/(eff_heater/100)
        
    f_em = combs[fuel]['f_em']
    PCI_kg = combs[fuel]['PCI_kg']
    dens = combs[fuel]['dens']
    
    cons_fuel = auxAnnual/(PCI_kg*dens)
    ahor_fuel = colAnnual/(eff_heater/100)/(PCI_kg*dens)
    dem_fuel = cons_fuel - ahor_fuel
    
    lcoh_conv = CFuel/(eff_heater/100)/(PCI_kg*dens)*1000
    
    table_fuel[combs[fuel]['nombre']] = ''
    table_fuel['PCI (kWh/kg)'] = PCI_kg
    table_fuel['LCOH conv (US$/MWh)'] = "{:10.1f}".format(lcoh_conv)
    table_fuel['--------'] = '--------'
    table_fuel['Demanda proceso (MWh/año)'] = "{:10.1f}".format(procAnnual)
#    table_fuel['Demanda proceso' + fuel + ' ' + cmb[fuel]['unidad']] = "{:10.1f}".format(dem_fuel)
    table_fuel['Energía convencional (MWh/año)'] = "{:10.1f}".format(auxAnnual)
    table_fuel['Consumo sin SST de ' + combs[fuel]['nombre'] + ' ' + combs[fuel]['unidad']] = "{:10.1f}".format(cons_fuel)
    table_fuel['Ahorro ' + combs[fuel]['nombre'] + ' ' + combs[fuel]['unidad']] = "{:10.1f}".format(ahor_fuel)
    table_fuel['---------'] = '---------'
    table_fuel['Emisiones'] = ''
    table_fuel['Factor de emisión (kg CO2/kg ' + combs[fuel]['nombre'] + ')'] = f_em
    table_fuel['Total emisiones (ton/año)'] = "{:10.1f}".format(cons_fuel * dens * f_em)
    table_fuel['Emisiones emitidas con SST (ton/año)'] = "{:10.1f}".format(dem_fuel*dens * f_em)
    table_fuel['Emisiones desplazadas (ton/año)'] = "{:10.1f}".format(ahor_fuel * dens * f_em)
        
    return table_fuel


def TableProy(lcoh,solFrac,annSol,indSol,fuel,CFuel,indFuel,eff_heater,anho_contr,anho_proy):
    colAnnual = annSol
    procAnnual = colAnnual/(solFrac/100)
    auxAnnual = procAnnual/(eff_heater/100)
        
    f_em = combs[fuel]['f_em']
    PCI_kg = combs[fuel]['PCI_kg']
    dens = combs[fuel]['dens']
    
    dem_fuel = procAnnual/(eff_heater/100)/(PCI_kg*dens)
    cons_fuel = auxAnnual/(PCI_kg*dens)
    ahor_fuel = colAnnual/(eff_heater/100)/(PCI_kg*dens)
    
    lcoh_conv = CFuel/(eff_heater/100)/(PCI_kg*dens)*1000
    
    ingSolar_1 = lcoh * colAnnual/1000
    ingSolar = Vector(ingSolar_1,anho_contr,indSol)
    
    costFuel_1 = cons_fuel*(100-solFrac)/100 * CFuel 
    costFoss_1 = cons_fuel  * CFuel
    
    costFuel = Vector(costFuel_1,anho_proy,indFuel)
    costFoss = Vector(costFoss_1,anho_proy,indFuel)   
    
    cSolar = pd.DataFrame(ingSolar,columns=['csol'])
    cFuel = pd.DataFrame(costFuel,columns=['cfuel'])
    cFoss = pd.DataFrame(costFoss,columns=['cfoss'])
    
    cProy = pd.concat([cSolar,cFuel,cFoss], axis=1)
    cProy = cProy.fillna(0)
    cProy['SST'] = cProy.csol + cProy.cfuel
    cProy.SST = cProy.SST.fillna(0)
    
    
    table_proy = pd.Series()
    table_proy['Pago sin SST (kUS$): '] = "{:10.1f}".format(cProy.cfoss.sum())
    table_proy['Pago con SST (kUS$): '] = "{:10.1f}".format(cProy.SST.sum())
    table_proy['Pago solar (kUS$): '] = "{:10.1f}".format(cProy.csol.sum())
    table_proy['Ahorro (kUS$): '] = "{:10.1f}".format(cProy.cfoss.sum() - cProy.SST.sum())
    
    
    return cProy, table_proy


def TableSteam(df_temp,turno,flow_p, Tout_h, Tin_h,eff_heater,rec_cond,T_cond,p_vapor,fuel):
    # Energía requerida kW
    q_proc = flow_p*1000*(Tout_h - Tin_h)*cp_w/3600
    dem = SetTurno(df_temp,turno,flow_p)
    df_temp['flujo'] = dem.flujo
    df_temp['demanda'] = dem.demanda
    df_temp['q_proc'] = df_temp.flujo *(Tout_h - Tin_h)*cp_w/3600
        
    #presion en bar (gauge) y condiciones del vapor
    presion_proc = p_vapor
    # entalpía vapor saturado (kJ/kg)
    sat_steam=IAPWS97(P=(presion_proc/10 + 1.033/10),x=1)
    # entalpía vapor humedo (kJ/kg)
    wet_steam=IAPWS97(P=(presion_proc/10 + 1.033/10),x=0)
    # calor latente de evaporación kJ/kg
    lat_heat = sat_steam.h - wet_steam.h
    
    # flujo de vapor en segundos. Multiplicado por 3600 para tener kg/hr
    steam = q_proc/lat_heat*3600
    #steam = 15000
    df_temp['steam'] = df_temp.demanda * df_temp.q_proc/lat_heat*3600
    
    # porcentaje recuperación condensado. Temperatura y flujo másico
    cond_rec = rec_cond
#    T_cond = wet_steam.T - 273.5
    m_cond = steam*cond_rec/100
    
    # Temperatura de red
    T_red = 20
    # temperatura make-up
    T_makeup = (T_red*(steam-m_cond) + T_cond*m_cond)/steam
    
    # flujo makeup (m3/hr)
    m_makeup = (steam-m_cond)/1000
    
    # condiciones del agua
    sat_water_inic=IAPWS97(T=T_makeup+273.5,x=0)
    sat_water_final=IAPWS97(P=(presion_proc/10 + 1.033/10),x=0)
    
    # energía para calentar agua y producir vapor (kWh)
    df_temp['ener_water'] = df_temp.demanda * m_makeup*1000 * (sat_water_final.h - sat_water_inic.h) / (3600)
    df_temp['ener_vapor'] = df_temp.demanda * m_makeup*1000 * (sat_steam.h - sat_water_final.h) / (3600)
    
    # total de energía demandada por el proceso
    df_temp['tot_ener'] = (df_temp.ener_water + df_temp.ener_vapor)
    
    # energía necesaria del combustible (kWh)
    df_temp['ener_fuel'] = df_temp.tot_ener/(eff_heater/100)
    
    # fracción solar
    enerSol = df_temp['Qgross'].groupby(df_temp.index.month).sum()/1000
    enerProc= df_temp['Qproc'].groupby(df_temp.index.month).sum()/1000
    FS = enerSol.sum() / enerProc.sum()
    
    enerFuel = df_temp.ener_fuel.sum()/1000
    enerHeater = df_temp.ener_fuel.sum()/1000 * (1-FS)
    enerSolar = df_temp.ener_fuel.sum()/1000 * FS
    
    table_steam = pd.Series()
    table_steam['Temperatura vapor (ºC)'] = "{:10.1f}".format(T_cond)
    table_steam['Calor latente evaporación (kJ/kg)'] = "{:10.1f}".format(lat_heat)
    table_steam['Flujo vapor (kg/hr)'] = "{:10.1f}".format(steam)
    table_steam['Flujo vapor (ton/año)'] = "{:10.1f}".format(df_temp.steam.sum()/1000)
    table_steam['-----------'] = '-----------'
    table_steam['Demanda energía convencional (MWh/año)'] = "{:10.1f}".format(enerFuel)
    table_steam['Generación caldera (MWh/año)'] = "{:10.1f}".format(enerHeater)
    table_steam['Reemplazo solar (MWh/año)'] = "{:10.1f}".format(enerSolar)
    table_steam['----------'] = '----------'
    
    f_em = cmb[fuel]['f_em']
    PCI_kg = cmb[fuel]['PCI_kg']
    dens = cmb[fuel]['dens']
    
    table_steam['Demanda ' + fuel + ' ' + cmb[fuel]['unidad']] = "{:10.1f}".format(enerFuel/(PCI_kg*dens))
    table_steam['Consumo ' + fuel + ' ' + cmb[fuel]['unidad']] = "{:10.1f}".format(enerHeater/(PCI_kg*dens))
    table_steam['Ahorro ' + fuel + ' ' + cmb[fuel]['unidad']] = "{:10.1f}".format(enerSolar/(PCI_kg*dens))
    
    table_steam['---------'] = '---------'
    table_steam['Emisiones'] = ''
    table_steam['Factor de emisión (kg CO2/kg ' + fuel + ')'] = f_em
    table_steam['Total emisiones (ton/año)'] = "{:10.1f}".format(enerFuel/PCI_kg * f_em)
    table_steam['Emisiones emitidas (ton/año)'] = "{:10.1f}".format(enerHeater/PCI_kg * f_em)
    table_steam['Emisiones desplazadas (ton/año)'] = "{:10.1f}".format(enerSolar/PCI_kg * f_em)
        
    df_temp['fuel_water'] = df_temp.q_proc/(eff_heater/100) / PCI_kg
    df_temp['fuel_steam'] = df_temp.ener_fuel / PCI_kg
    
    return table_steam
    

def TestSteam(df_temp,turno,steam,eff_heater,cond_rec,T_cond,p_vapor,fuel,fuelCost):
    dem = SetTurno(df_temp,turno,steam)
    df_temp['flujo'] = dem.flujo
    df_temp['demanda'] = dem.demanda

    #presion en bar (gauge) y condiciones del vapor
    presion_proc = p_vapor
    # entalpía vapor saturado (kJ/kg)
    sat_steam=IAPWS97(P=(presion_proc/10 + 1.033/10),x=1)
    # entalpía vapor humedo (kJ/kg)
    wet_steam=IAPWS97(P=(presion_proc/10 + 1.033/10),x=0)
    # calor latente de evaporación kJ/kg
    lat_heat = sat_steam.h - wet_steam.h
    
    # flujo de vapor en segundos. Multiplicado por 3600 para tener kg/hr
#    steam = flow_steam
    df_temp['steam'] = steam * df_temp.demanda
    
    T_vapor = sat_steam.T - 273
    
    # porcentaje recuperación condensado. Temperatura y flujo másico
#    cond_rec = rec_cond
    m_cond = steam*cond_rec/100
    
    # Temperatura de red
    T_red = 20
    # temperatura make-up
    T_makeup = (T_red*(steam-m_cond) + T_cond*m_cond)/steam
    
    # flujo makeup (m3/hr)
    m_makeup = (steam-m_cond)/1000
    
    # condiciones del agua
    sat_water_inic=IAPWS97(T=T_makeup+273.5,x=0)
    sat_water_final=IAPWS97(P=(presion_proc/10 + 1.033/10),x=0)
    
    # energía para calentar agua y producir vapor (kWh)
    df_temp['ener_water'] = df_temp.demanda * steam * (sat_water_final.h - sat_water_inic.h) / (3600)
    df_temp['ener_vapor'] = df_temp.demanda * steam * (sat_steam.h - sat_water_final.h) / (3600)
    # total de energía demandada por el proceso
    df_temp['tot_ener'] = (df_temp.ener_water + df_temp.ener_vapor)
    
    # energía necesaria del combustible (kWh)
    df_temp['ener_fuel'] = df_temp.tot_ener/(eff_heater/100)
    
    ener_sens = steam * (sat_water_final.h - sat_water_inic.h) / (3600)/(eff_heater/100)
    ener_lat =  steam * (sat_steam.h - sat_water_final.h) / (3600)/(eff_heater/100)
    ener = ener_sens + ener_lat
    
    ener_sensTon = 1000 * (sat_water_final.h - sat_water_inic.h) / (3600)/(eff_heater/100)
    ener_latTon =  1000 * (sat_steam.h - sat_water_final.h) / (3600)/(eff_heater/100)
    enerTon = ener_sensTon + ener_latTon
        
    enerProc = df_temp.tot_ener.sum()/1000
    enerHeater = df_temp.ener_fuel.sum()/1000 
    
    f_em = cmb[fuel]['f_em']
    PCI_kg = cmb[fuel]['PCI_kg']
    dens = cmb[fuel]['dens']
    
    table_steam = pd.Series()
    table_steam['Temperatura vapor (ºC)'] = "{:10.1f}".format(T_vapor)
    table_steam['Calor latente evaporación (kJ/kg)'] = "{:10.1f}".format(lat_heat)
    table_steam['Flujo vapor (kg/hr)'] = "{:10.1f}".format(steam)
    table_steam['Consumo hora de ' + fuel + ' ' + '(' + cmb[fuel]['unidad'] + '/hr)'] = "{:10.1f}".format(ener/(PCI_kg*dens))
    table_steam['Flujo vapor (ton/año)'] = "{:10.1f}".format(df_temp.steam.sum()/1000)
    table_steam['-----------'] = '------------'
    table_steam['Demanda energía proceso (MWh/año)'] = "{:10.1f}".format(enerProc)
    table_steam['Generación caldera (MWh/año)'] = "{:10.1f}".format(enerHeater)
    table_steam['-----------'] = '-----------'
    table_steam['Temperatura make-up (ºC)'] = "{:10.1f}".format(T_makeup)
    table_steam['Calor sensible (kWh/flujo vapor)'] = "{:10.1f}".format(ener_sens)
    table_steam['Calor latente (kWh/flujo vapor)'] = "{:10.1f}".format(ener_lat)
    table_steam['Energía (kWh/flujo vapor)'] = "{:10.1f}".format(ener)
    table_steam['----------'] = '----------'
    table_steam['Calor sensible caldera (kWh/ton vapor)'] = "{:10.1f}".format(ener_sensTon)
    table_steam['Calor latente caldera (kWh/ton vapor)'] = "{:10.1f}".format(ener_latTon)
    table_steam['Energía caldera (kWh/ton vapor)'] = "{:10.1f}".format(enerTon)
    table_steam['Consumo ' + fuel + ' (ton/hr vapor)'] = "{:10.1f}".format(enerTon/(PCI_kg*dens))
    table_steam['Costo vapor (US$/ton vapor)'] = "{:10.1f}".format(enerTon/(PCI_kg*dens) * fuelCost)
    table_steam['Costo energía (US$/MWh)'] = "{:10.1f}".format(enerHeater/(PCI_kg*dens) * fuelCost / enerProc * 1000)
    table_steam['Calor sensible (kWh/ton vapor)'] = "{:10.1f}".format(ener_sensTon*eff_heater/100)
    table_steam['Calor latente (kWh/ton vapor)'] = "{:10.1f}".format(ener_latTon*eff_heater/100)
    table_steam['Energía (kWh/ton vapor)'] = "{:10.1f}".format(enerTon*eff_heater/100)
    table_steam['----------'] = '---------'
        
    table_steam['Consumo ' + fuel + ' ' + cmb[fuel]['unidad']] = "{:10.1f}".format(enerHeater/(PCI_kg*dens))
    
    table_steam['---------'] = '---------'
    table_steam['Emisiones'] = ''
    table_steam['Factor de emisión (kg CO2/kg ' + fuel + ')'] = f_em
    table_steam['Emisiones (ton/año)'] = "{:10.1f}".format(enerHeater/PCI_kg * f_em)
    table_steam['Horas al año'] = "{:10.1f}".format(df_temp.demanda.sum())
        
#    df_temp['fuel_water'] = df_temp.q_proc/(eff_heater/100) / PCI_kg
    df_temp['fuel_steam'] = df_temp.ener_fuel / PCI_kg
        
    return table_steam

def PowerHeater(steam_flow,steam_press,Tin):
    
    #presion en bar (gauge) y condiciones del vapor
    presion_proc = steam_press
    # entalpía vapor saturado (kJ/kg)
    sat_steam=IAPWS97(P=(presion_proc/10 + 1.033/10),x=1)
    
    # condiciones del agua
    sat_water_inic=IAPWS97(T=Tin+273.5,x=0)
    sat_water_final=IAPWS97(P=(presion_proc/10 + 1.033/10),x=0)
    
    ener_sens = steam_flow * (sat_water_final.h - sat_water_inic.h) / (3600)
    ener_lat =  steam_flow * (sat_steam.h - sat_water_final.h) / (3600)
    ener = ener_sens + ener_lat
        
    return ener

def nLoopsFresnel(dni,power,eff,sm,areaMod):
    area = power*1e6 / ( dni * eff)
    areaSM = area * sm
    nLoop = np.ceil(areaSM/(areaMod*16))
    areaFinal = nLoop*areaMod*16
    
    return nLoop

def TableFresnel(dni,power,eff,sm,areaMod):
    area = power*1e6 / ( dni * eff)
    areaSM = power * 1e6 /( dni * eff) * sm
    nLoop = np.ceil(areaSM/(areaMod*16))
    areaFinal = nLoop*areaMod*16
    
    table_fresnel = pd.Series()
    table_fresnel['Potencia proceso: '] = power
    table_fresnel['Área SM=1'] = area
    table_fresnel['Área SM usuario'] = areaSM
    table_fresnel['Área final: '] = areaFinal
    
    return table_fresnel