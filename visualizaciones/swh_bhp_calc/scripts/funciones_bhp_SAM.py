#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 11:53:27 2019

@author: fcuevas
"""
import numpy as np
import pandas as pd
import shutil
import os

from PySSC import PySSC


#path = '/Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/'
# path = '/home/diegonaranjo/Documentos/Thenergy/sun4heat/'
# path = '/home/ubuntu/Thenergy/diego/sun4heat/'

path = '/home/diego/Documentos/sun4heat/'



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

def CopyRadFile(lugar,data):
    '''
    Para un lugar en especifico, copia archivo de radiación formato SAM 
    a carpeta temporal, cambia nombre a TMY_lugar_SAM.CSV 

    Parameters
    ----------
    lugar : str
        Lugar en donde se copiara el archivo formato SAM.
    data : str
        DESCRIPTION.

    Returns
    -------
    df_temp : TYPE
        DESCRIPTION.

    '''
    
    if data == 'Explorador Solar':
        path_file = path + 'datos/radiacion_solar/expl_solar/TMY_' + lugar + '_SAM.csv'
        path_tmp = path + 'datos/radiacion_solar/expl_solar/tmp'
        path_SAM = path + 'datos/radiacion_solar/TMY_SAM.csv'
        path_expl = path + 'datos/radiacion_solar/expl_solar/TMY_' + lugar + '.csv'
    
        shutil.copy(path_file,path_tmp)
        os.rename(path_tmp + '/TMY_' + lugar + '_SAM.csv',path_SAM)
    
        df_temp = pd.read_csv(path_expl,skiprows=41, index_col=0)
        df_temp.index = pd.date_range(start='2018-01-01 00:00', end='2018-12-31 23:00', freq='H')
        df_temp['poa'] = df_temp.ghi
        
    elif data == 'Meteonorm':
        path_file = path + 'datos/radiacion_solar/meteonorm/TMY_' + lugar + '_SAM.csv'
        path_tmp = path + 'datos/radiacion_solar/meteonorm/tmp'
        path_SAM = path + 'datos/radiacion_solar/TMY_SAM.csv'
        path_meteo = path + 'datos/radiacion_solar/meteonorm/TMY_' + lugar + '.csv'
        
        shutil.copy(path_file,path_tmp)
        os.rename(path_tmp + '/TMY_' + lugar + '_SAM.csv',path_SAM)
                
        header = ['year','month','day','hour','hour_real','ghi','dhi','ght','dht','dni','temp']
        df_temp = pd.read_csv(path_meteo,sep=';',names=header)
        df_temp.index = pd.date_range(start='2018-01-01 00:00', end='2018-12-31 23:00', freq='H') 
        df_temp['poa'] = df_temp.ghi
    
    return df_temp


def CallSWH(df_temp,tilt,azim,Col,area,vol,sto_loss,year):
    '''
    Realiza la simulación en SAM en función de los parámetros establecidos, obteniendo
    las variables de interes.
    
    Variables de interes
    --------------------
    'flow', 'poa', 'trans', 'pump', 'Qaux', 'Qproc', 'Qdel', 'Qloss', 'Qtrans', 'Qusef'
    'Tcold', 'Thot', 'Tmains', 'Ttank', 'Tdel', 'Vcold', 'Vhot'

    Parameters
    ----------
    df_temp : DataFrame
        DF .
    tilt : int
        Inclinación campo solar.
    azim : int
        Azimuth.
    Col : str
        Tipo de colector.
    area : int
        Área del colector.
    vol : int
        Volumen almacenamiento.
    sto_loss : int
        Porcentaje pérdidas del almacenamiento.
    Returns
    -------
    df_temp : DataFrame
        DF con las variables de interes calculadas a través de simulación.

    '''
    
    FRta = cst[Col]['n0']
    FRUL = cst[Col]['a1']
     
    #flujo colector solar
    mdot = area * 260/3600
    
    ssc = PySSC()
    print ('SSC Version = ', ssc.version())
    print('year is : ' + str(year))
    print ('SSC Build Information = ', ssc.build_info().decode("utf - 8"))
    ssc.module_exec_set_print(0)
    dataSam = ssc.data_create()

    
    ssc.data_set_string( dataSam, b'solar_resource_file', path.encode() + b'datos/radiacion_solar/TMY_SAM.csv' );
    ssc.data_set_array_from_csv( dataSam, b'scaled_draw', path.encode() + b'visualizaciones/swh_bhp_calc/resultados/load_profile/scaled_draw_'+ str(year).encode('ascii')+ b'.csv')




    ssc.data_set_number( dataSam, b'system_capacity', 773.8553466796875 )
    ssc.data_set_number( dataSam, b'tilt', tilt )
    ssc.data_set_number( dataSam, b'azimuth', azim )
    ssc.data_set_number( dataSam, b'albedo', 0.20000000298023224 )
    ssc.data_set_number( dataSam, b'irrad_mode', 0 )
    ssc.data_set_number( dataSam, b'sky_model', 0 )
    ssc.data_set_number( dataSam, b'mdot', mdot )
    ssc.data_set_number( dataSam, b'ncoll', area )
    ssc.data_set_number( dataSam, b'fluid', 1 )
    ssc.data_set_number( dataSam, b'area_coll', 1 )
    ssc.data_set_number( dataSam, b'FRta', FRta )
    ssc.data_set_number( dataSam, b'FRUL', FRUL )
    ssc.data_set_number( dataSam, b'iam', 0.20000000298023224 )
    ssc.data_set_number( dataSam, b'test_fluid', 0 )
    ssc.data_set_number( dataSam, b'test_flow', 0.072200000286102295 )
    ssc.data_set_number( dataSam, b'pipe_length', 10 )
    ssc.data_set_number( dataSam, b'pipe_diam', 0.018999999389052391 )
    ssc.data_set_number( dataSam, b'pipe_k', 0.029999999329447746 )
    ssc.data_set_number( dataSam, b'pipe_insul', 0.0060000000521540642 )
    ssc.data_set_number( dataSam, b'tank_h2d_ratio', 2 )
    ssc.data_set_number( dataSam, b'U_tank', 1 )
    ssc.data_set_number( dataSam, b'V_tank', vol )
    ssc.data_set_number( dataSam, b'hx_eff', 0.75 )
    ssc.data_set_number( dataSam, b'T_room', 20 )
    ssc.data_set_number( dataSam, b'T_tank_max', 95 )
    ssc.data_set_number( dataSam, b'T_set', 70 )
    ssc.data_set_number( dataSam, b'pump_power', 45 )
    ssc.data_set_number( dataSam, b'pump_eff', 0.85000002384185791 )
    ssc.data_set_number( dataSam, b'use_custom_mains', 1 )
    ssc.data_set_array_from_csv( dataSam, b'custom_mains', path.encode() + b'visualizaciones/swh_bhp_calc/custom_mains.csv');
    
    ssc.data_set_number( dataSam, b'use_custom_set', 1 )
    ssc.data_set_array_from_csv( dataSam, b'custom_set', path.encode() + b'visualizaciones/swh_bhp_calc/custom_set.csv');

    ssc.data_set_number( dataSam, b'adjust:constant', 0 )
    module = ssc.module_create(b'swh')  
    ssc.module_exec_set_print( 0 );
    if ssc.module_exec(module, dataSam) == 0:
        print ('swh simulation error')
        idx = 1
        msg = ssc.module_log(module, 0)
        while (msg != None):
            print ('    : ' + msg.decode("utf - 8"))
            msg = ssc.module_log(module, idx)
            idx = idx + 1
        SystemExit( "Simulation Error" );
    ssc.module_free(module)
    
    flow = ssc.data_get_array(dataSam,b'draw')
    inc = ssc.data_get_array(dataSam,b'I_incident')
    trans = ssc.data_get_array(dataSam,b'I_transmitted')
    pump = ssc.data_get_array(dataSam,b'P_pump')
    Qaux = ssc.data_get_array(dataSam,b'Q_aux')
    Qproc = ssc.data_get_array(dataSam,b'Q_auxonly')
    Qdel = ssc.data_get_array(dataSam,b'Q_deliv')
    Qloss = ssc.data_get_array(dataSam,b'Q_loss')
    Qtrans = ssc.data_get_array(dataSam,b'Q_transmitted')
    Qusef = ssc.data_get_array(dataSam,b'Q_useful')
    Tcold = ssc.data_get_array(dataSam,b'T_cold')
    Tdel = ssc.data_get_array(dataSam,b'T_deliv')
    Thot = ssc.data_get_array(dataSam,b'T_hot')
    Tmains = ssc.data_get_array(dataSam,b'T_mains')
    Ttank = ssc.data_get_array(dataSam,b'T_tank')
    Vcold = ssc.data_get_array(dataSam,b'V_cold')
    Vhot = ssc.data_get_array(dataSam,b'V_hot')
    
    df_temp['flow'] = list(flow)
    df_temp['poa'] = inc 
    df_temp['trans'] = trans
    df_temp['pump'] = pump
    df_temp['Qaux'] = Qaux
    df_temp['Qproc'] = Qproc
    df_temp['Qdel'] = Qdel
    df_temp['Qloss'] = Qloss
    df_temp['Qtrans'] = Qtrans
    df_temp['Qusef'] = Qusef
    df_temp['Tcold'] = Tcold
    df_temp['Thot'] = Thot
    df_temp['Tmains'] = Tmains
    df_temp['Ttank'] = Ttank
    df_temp['Tdel'] = Tdel
    df_temp['Vcold'] = Vcold
    df_temp['Vhot'] = Vhot
    
    Qcol = []
    EffCol = []
    
    for rad,thot,tcold,qusef in zip(df_temp.poa,df_temp.Thot,df_temp.Tcold,df_temp.Qusef):
        if rad > 0:
            qcol = mdot*1000*4.18*(thot - tcold) / 3600
            Qcol.append(qcol)
            eff = qusef/rad
            EffCol.append(eff)
            
        else:
            Qcol.append(0)
            EffCol.append(0)
        
    df_temp['Qcol'] = Qcol
    df_temp['EffCol'] = EffCol
    
    Qsto = []
    Qpeak = []
    
    for qusef,qproc in zip(df_temp.Qusef,df_temp.Qproc):
        if qusef - qproc < 0:
            Qsto.append(0)
            Qpeak.append(qusef)
            
        else: 
            Qsto.append(qusef - qproc)
            Qpeak.append(qproc)
        
    df_temp['Qsto'] = Qsto
    df_temp['Qpeak'] = Qpeak
    df_temp['Qgross'] = df_temp.Qsto*(1-sto_loss/100) + df_temp.Qpeak   
    
    ssc.data_free(dataSam);
    
    return df_temp

def SetTMains(df_temp,Tmains):
    '''
    Setea la temperatura de salida del proceso como temperatura promedio a cada hora
    por un año.
    
    Exporta los datos a csv.

    Parameters
    ----------
    df_temp : DataFrame
        DF a setear la temperatura promedio.
    Tmains : int 
        Temperatura promedio (del tanque (?) == temp salida proceso).

    Returns
    -------
    None.

    '''
    df_temp = pd.DataFrame(np.arange(0,8760,1),columns=["demanda"])
    df_temp.index = pd.date_range(start='2018-01-01 00:00', end='2018-12-31 23:00', freq='H')
    df_temp['Tmains'] = Tmains
    df_temp['Tmains'].to_csv(path + "visualizaciones/swh_bhp_calc/custom_mains.csv", index=False, header=False)
    
def SetTSet(df_temp,Tset):
    '''
    Setea la temperatura de entrada del flujo al proceso.

    Parameters
    ----------
    df_temp : DataFrame
        DESCRIPTION.
    Tset : int
        Temperatura de entrada al proceso.

    Returns
    -------
    None.

    '''
    df_temp = pd.DataFrame(np.arange(0,8760,1),columns=["demanda"])
    df_temp.index = pd.date_range(start='2018-01-01 00:00', end='2018-12-31 23:00', freq='H')
    df_temp['Tset'] = Tset
    df_temp['Tset'].to_csv(path + "visualizaciones/swh_bhp_calc/custom_set.csv", index=False, header=False)


# CASO BHP 24/7, DEMANDA YA SE ESTABLECE EN SCALED DRAW ANUAL.
def SetTurno(df_temp,turno):    #,m_proc):
    '''
    Establece el nivel de demanda en función del turno.
    
    Este nivel de demanda se multiplica con el flujo de agua del proceso, obteniendo
    el flujo de demanda por turno.

    Parameters
    ----------
    df_temp : DataFrame
        DESCRIPTION.
    turno : str
        Turnos (pueden estar en función de turnos típicos o especiales por empresa).
    m_proc : int
        flujo de agua.

    Returns
    -------
    df_temp : TDataFrame
        DESCRIPTION.

    '''
    df_temp = pd.DataFrame(np.arange(0,8760,1),columns=["demanda"])
    df_temp.index = pd.date_range(start='2018-01-01 00:00', end='2018-12-31 23:00', freq='H')
    if turno == '24/7':
        df_temp['demanda'] = 1 
        
    elif turno =='17/7':
        dem_tmp = []
        for m in df_temp.index:
            if (m.hour < 6):
                tmp = 0
            else:
                tmp = 1
                
            dem_tmp.append(tmp)
        df_temp['demanda'] = dem_tmp 
        
    elif turno =='17/6':
        dem_tmp = []
        for m in df_temp.index:
            if m.dayofweek == 6:
                tmp = 0
            elif (m.hour < 6):
                tmp = 0
            else:
                tmp = 1
                
            dem_tmp.append(tmp)
        df_temp['demanda'] = dem_tmp 

    elif turno =='24/6':
        dem_tmp = []
        for m in df_temp.index:
            if m.dayofweek == 6:
                tmp = 0
            else:
                tmp = 1
                
            dem_tmp.append(tmp)
        df_temp['demanda'] = dem_tmp 

    elif turno =='14/6':
        dem_tmp = []
        for m in df_temp.index:
            if m.dayofweek == 6:
                tmp = 0
            elif (m.hour < 8 or m.hour > 22):
                tmp = 0
            else:
                tmp = 1
                
            dem_tmp.append(tmp)
        df_temp['demanda'] = dem_tmp 
        
    elif turno =='Agrosuper ACS':
        dem_tmp = []
        for m in df_temp.index:
            if m.dayofweek == 6:
                tmp = 0
            elif (m.hour == 0 and m.dayofweek == 0):
                tmp = 55
            elif (m.hour == 1 and m.dayofweek == 0):
                tmp = 70
            elif (m.hour == 2 or m.hour == 3 or m.hour == 4) and (m.dayofweek == 0):
                tmp = 61
            elif (m.hour == 5 and m.dayofweek == 0):
                tmp = 161
            elif (m.hour == 6 and m.dayofweek == 0):
                tmp = 159
            elif (m.hour == 7 and m.dayofweek == 0):
                tmp = 139
            elif (m.hour == 8 and m.dayofweek == 0):
                tmp = 106
            elif (m.hour == 9 or m.hour == 10 or m.hour == 11) and (m.dayofweek == 0):
                tmp = 111
            elif (m.hour == 12 and m.dayofweek == 0):
                tmp = 108
            elif (m.hour == 13 and m.dayofweek == 0):
                tmp = 129
            elif (m.hour == 14 and m.dayofweek == 0):
                tmp = 134
            elif (m.hour == 15 and m.dayofweek == 0):
                tmp = 137
            elif (m.hour == 16 and m.dayofweek == 0):
                tmp = 136
            elif (m.hour == 17 and m.dayofweek == 0):
                tmp = 122
            elif (m.hour == 18 and m.dayofweek == 0):
                tmp = 111
            elif (m.hour == 19 and m.dayofweek == 0):
                tmp = 109
            elif (m.hour == 20 and m.dayofweek == 0):
                tmp = 111
            elif (m.hour == 21 and m.dayofweek == 0):
                tmp = 111
            elif (m.hour == 22 and m.dayofweek == 0):
                tmp = 102
            elif (m.hour == 23 and m.dayofweek == 0):
                tmp = 95
                
            elif (m.hour == 0 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 or m.dayofweek == 5)):
                tmp = 110
            elif (m.hour == 1 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 or m.dayofweek == 5)):
                tmp = 139
            elif ((m.hour == 2 or m.hour == 3) and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 or m.dayofweek == 5)):
                tmp = 122
            elif (m.hour == 4 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 or m.dayofweek == 5)):
                tmp = 124
            elif (m.hour == 5 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 or m.dayofweek == 5)):
                tmp = 161
            elif (m.hour == 6 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 or m.dayofweek == 5)):
                tmp = 159
            elif (m.hour == 7 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 or m.dayofweek == 5)):
                tmp = 139
            elif (m.hour == 8 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 or m.dayofweek == 5)):
                tmp = 106
            elif ((m.hour == 9 or m.hour == 10 or m.hour == 11) and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 or m.dayofweek == 5)):
                tmp = 111
            elif (m.hour == 12 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 or m.dayofweek == 5)):
                tmp = 108
            elif (m.hour == 13 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 or m.dayofweek == 5)):
                tmp = 129
            elif (m.hour == 14 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 or m.dayofweek == 5)):
                tmp = 134
            elif (m.hour == 15 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 )):
                tmp = 137
            elif (m.hour == 16 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 )):
                tmp = 136
            elif (m.hour == 17 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 )):
                tmp = 122
            elif (m.hour == 18 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 )):
                tmp = 111
            elif (m.hour == 19 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 )):
                tmp = 109
            elif (m.hour == 20 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 )):
                tmp = 111
            elif (m.hour == 21 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 )):
                tmp = 111
            elif (m.hour == 22 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 )):
                tmp = 102
            elif (m.hour == 23 and (m.dayofweek == 1 or m.dayofweek == 2 or m.dayofweek == 3 or m.dayofweek == 4 )):
                tmp = 105
                
            elif (m.hour == 15 and m.dayofweek == 5):
                tmp = 92.1
            elif (m.hour == 16 and m.dayofweek == 5):
                tmp = 90.8
            elif (m.hour == 17 and m.dayofweek == 5):
                tmp = 77.2
            elif (m.hour == 18 and m.dayofweek == 5):
                tmp = 66.3
            elif (m.hour == 19 and m.dayofweek == 5):
                tmp = 66.4
            elif (m.hour == 20 and m.dayofweek == 5):
                tmp = 66.3
            elif (m.hour == 21 and m.dayofweek == 5):
                tmp = 66.1
            elif (m.hour == 22 and m.dayofweek == 5):
                tmp = 57.1
            elif (m.hour == 23 and m.dayofweek == 5):
                tmp = 50.2
                
            
            else:
                tmp = 1
                        
            dem_tmp.append(tmp)
        df_temp['demanda'] = dem_tmp 
                
    elif turno =='Agrosuper Sanit':
        dem_tmp = []
        for m in df_temp.index:
            if m.dayofweek == 6:
                tmp = 0
            elif (m.dayofweek == 5 and m.hour > 14):
                tmp = 0
            elif (m.hour < 5):
                tmp = 0
            else:
                tmp = 1
                
            dem_tmp.append(tmp)
        df_temp['demanda'] = dem_tmp 
            
    elif turno =='Watts':
        dem_tmp = []
        for m in df_temp.index:
            if m.dayofweek == 6:
                tmp = 0
            elif (m.dayofweek == 5 and m.hour > 14):
                tmp = 0
            elif (m.dayofweek == 0 and m.hour < 7):
                tmp = 0
            else:
                tmp = 1
                
            dem_tmp.append(tmp)
        df_temp['demanda'] = dem_tmp 
                
    elif turno =='Sopraval escaldado':
        dem_tmp = []
        for m in df_temp.index:
            if m.dayofweek == 6:
                tmp = 0
            elif (m.dayofweek == 5):
                tmp = 0
            elif (m.hour < 7 or m.hour > 15):
                tmp = 0
            else:
                tmp = 1
                
            dem_tmp.append(tmp)
        df_temp['demanda'] = dem_tmp 
        
    elif turno =='Sopraval producción':
        dem_tmp = []
        for m in df_temp.index: 
            if (m.dayofweek == 6 and m.hour<22):
                tmp = 0
            elif (m.dayofweek == 5 and (m.hour>7 and m.hour < 22)):
                tmp = 0.25
            elif (m.dayofweek == 5 and  m.hour > 22):
                tmp = 0
            else:
                tmp = 1
                
            dem_tmp.append(tmp)
        df_temp['demanda'] = dem_tmp 
        
    elif turno =='Ejemplo':
        dem_tmp = []
        for m in df_temp.index:
            if (m.hour > 18 or m.hour <9):
            
                tmp = 0
            elif (m.dayofweek == 5 and (m.hour<9 or m.hour > 14)):
                tmp = 0
            elif (m.dayofweek == 6):
                tmp = 0
            else:
                tmp = 1
                
            dem_tmp.append(tmp)
        df_temp['demanda'] = dem_tmp 
        
    elif turno =='14/7':
        dem_tmp = []
        for m in df_temp.index:
            
            if (m.hour < 7 or m.hour > 21):
                tmp = 0
            else:
                tmp = 1
                
            dem_tmp.append(tmp)
        df_temp['demanda'] = dem_tmp 
        
    elif turno =='Lucchetti':
        dem_tmp = []
        for m in df_temp.index:
            
            if (m.month == 2):
                tmp = 0
            else:
                tmp = 1
                
            dem_tmp.append(tmp)
        df_temp['demanda'] = dem_tmp 
    
    # df_temp['flujo'] = df_temp.demanda*m_proc*1000
    # df_temp['flujo'].to_csv(path + "visualizaciones/swh_calc/scaled_draw.csv", index=False, header=False)
    
    return df_temp
    