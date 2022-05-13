#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 15:33:06 2019     

@author: fcuevas
"""
import sys
sys.path
#sys.path.append('/Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/visualizaciones/swh_bhp_calc/scripts')
sys.path.append('/home/diego/Documentos/sun4heat/visualizaciones/swh_bhp_calc/scripts')
# sys.path.append('/home/ubuntu/Thenergy/diego/sun4heat/scripts')

import numpy as np
import pandas as pd

from funciones_bhp import TableRad,  Col_eff_val, RadMonth,  SystemMonth, SystemYear, TableEner, TableFuel,  TableFuel_LCOH, BalanceYear, BalanceMonth, TableProy, TableEnerYear# ,TableSteam
from funciones_bhp_SAM import CallSWH, SetTurno, SetTMains, SetTSet, CopyRadFile
from funciones_econ_bhp import Pago, PagoPrinInt, Vector, Vector_20, TableRes, Depr, Perdidas, BaseImpuesto, FlujoAcum,Van,Tir,Payback,TableCapex,TableCapexU, TableOpex, TableOpexY, TableEval, LCOH_calc, LCOH_calc_upt

from bokeh.plotting import Figure
from bokeh.layouts import column, Spacer, row
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, DatetimeTickFormatter, TableColumn, DataTable, NumberFormatter, CustomJS, RadioButtonGroup
from bokeh.io import curdoc
from bokeh.transform import factor_cmap
from bokeh.models.widgets import Select, TextInput, Button, PreText

meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
#path = '/Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/'
# path = '/home/ubuntu/Thenergy/diego/sun4heat/'
path = '/home/diego/Documentos/sun4heat/'

years = np.arange(2024,2045)
years = list(years)
years_list = list(map(str, years))

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




##################################
#           RADIACION
###################################

# ciudades = pd.read_csv('/home/diegonaranjo/Documentos/Thenergy/sun4heat/datos/radiacion_solar/ciudades.csv',sep=',')
minas = pd.read_csv('/home/diego/Documentos/sun4heat/datos/radiacion_solar/minas_bhp.csv',sep=',')

# ciudades = pd.read_csv('/home/ubuntu/Thenergy/diego/sun4heat/datos/radiacion_solar/ciudades.csv',sep=',')

lugar = 'Spence'
data_lugar = minas[minas.Mina == lugar]
ghi_sg = data_lugar.GHI_SG.iloc[0]
dataSol = 'Explorador Solar'

df = CopyRadFile(lugar,dataSol)
table_rad = TableRad(df)
table_rad['GHI Solargis (kWh/m2/año)'] = ghi_sg
rad_month, x_month = RadMonth(df)

source_rad = ColumnDataSource(data=dict(x=x_month, rad=rad_month))


###################################
#       APORTE SISTEMA SOLAR
###################################

#Propiedades del agua
#densidad 
dens_w = 1000  # (kg/m3)

# Calor específico agua 
cp_w = 4.18     #(kJ/(kg*K))


##################################

# temperatura de entrada al proceso
Tin_p  = 70

# temperatura de salida del proceso
Tout_p = 50     # ºC

# flujo de agua, proceso
flow_p = 30     # m3/hr


###################################

# caldera, temperatura de salida
Tout_h = Tin_p + 5      # ºC

# caldera, temperatura de entrada
Tin_h  = Tout_h - (Tin_p - Tout_p)      # ºC

# flujo de agua
flow_h = flow_p     # m3/hr

# Potenica caldera
potHeater = 150

# Eficiencia caldera
effHeater = 75

# Potencia bomba de calor
potHPump = 150

# Eficiencia bomba de calor
effHPump = 98

# % recuperación condensado
cond = 30

# temperatura de condensado
T_cond = 90

# presion de vapor
p_steam = 5

# Potencia heater
# heater_pow = flow_p*dens_w*(Tout_h - Tin_h)*cp_w/3600

# Combustible
fuel = 'Diesel'

# Costo del combustible
costFuel = 0.32

# Indexación del combustible
indFuel = 2.4

#Turno
turno = '24/7'

#year
year= '2024'

##############################################
#           BOTON AÑO
##############################################

years_button_group = RadioButtonGroup(labels=years_list, active=0,button_type="success")
years_button_group.on_change('active', lambda attr, old, new: CalcSystemMonth)




###########################
#    COLECTOR SOLAR
###########################

#Colector
Col = 'GreenOneTec GK_SG'

#Area de colector
aCol = 1800

# Volumen almacenamiento
vol = 180

#########################

# Producción específica colector
yield_m2 = 1.4

# Largo del piping interconexión (m)
Lpipe = 2000

# número de intercambiadores de calor
nHEX = 5

#########################

#Temperatura media del colector
Tmean = (Tin_h + Tout_h)/2.

# Eficiencia del colector
eff_col = Col_eff_val(Col,Tmean,25,1000)

# area de la planta solar peak
# peak_plant = heater_pow/eff_col * 1.1

#inclinación campo solar
tilt = 0

#azimuth campos solar
azim = 0


# Porcentaje pérdidas del almacenamiento
sto_loss=10


############################
#   ECON COLECTOR SOLAR
############################

# Indexacion del precio solar
indSol = 2

# costo colector (US$/m2)
costCol_m2 = 369.4

# costo instalación colector (US$/m2)
cost_instCol_m2 = 100

# costo balance de planta (US$/m2)
costBOP = 100

# costo instalación balance de planta (US$/m2)
cost_instBOP = 100

# costo storage (US$/m3)
costSto = 100

# costo instalación storage (US$)
cost_instSto = 100

# costo caldera eléctrica (US$)
costCald = 100

# costo instalación caldera eléctrica (US$)
cost_instCald = 100

# costo piping (US$/m)
costPiping = 100

# costo instalación piping (US$/m)
cost_instPiping = 100

# costo HEX (US$)
costHEX = 100

# costo instalación HEX (US$)
cost_instHEX = 100

# costo preparación terreno (US$/m2)
cost_prepTerr = 30

# costo ingeniería (US$)
CostIng = 200000

# costo desarrollo (US$)
CostDev = 200000

# costo energía (US$/kW)
Ecost = 70

# Freight, Insurance and Transport
FIT_m2 = 0
FIT = FIT_m2 * aCol

#Costos independientes capex equipos capex
CEQ_1 = (aCol * costCol_m2)
CEQ_2 = (aCol * costBOP)
CEQ_3 = costSto
CEQ_4 = costCald
CEQ_5 = (costPiping * Lpipe)
CEQ_6 =(costHEX * nHEX)

# CAPEX de equipos
CAPEX_eq = CEQ_1 + CEQ_2 + CEQ_3 + CEQ_4 + CEQ_5 + CEQ_6

# CAPEX PIPHEX
COST_PIPHEX = CEQ_5+CEQ_6
 
#Costos independientes instalación capex
CIN_1 = (aCol * cost_instCol_m2)
CIN_2 = cost_instBOP
CIN_3 = cost_instSto
CIN_4 = cost_instCald
CIN_5 = (Lpipe * cost_instPiping)
CIN_6 = (nHEX * cost_instHEX)
CIN_7 = (aCol * cost_prepTerr)


# CAPEX instalación
CAPEX_inst =  CIN_1 + CIN_2 + CIN_3 + CIN_4 + CIN_5 + CIN_6 + CIN_7

#Costos independientes 
CDE_1 = CostIng
CDE_2 = CostDev

# CAPEX desarrollo (US$)
CAPEX_dev = CDE_1 + CDE_2

# Contingencias (% CAPEX)
Cont = 10
Cont_tot = (CAPEX_eq + CAPEX_inst + CAPEX_dev) * Cont/100

# Utilidades (% CAPEX)
Util = 10
Util_tot = (CAPEX_eq + CAPEX_inst + CAPEX_dev) * Util/100

CAPEX = CAPEX_eq + CAPEX_inst + CAPEX_dev + Cont_tot + Util_tot + FIT
#############
# CPX = aCol * costCol_m2 

# perc_fee = 0
# fee = (CAPEX+FIT)*perc_fee/100
# CAPEX = CPX+ FIT + fee 

#####################################
#   OPEX
#####################################

#trabajadores
Workers = 10

#costo trabajador mensual US$/mes
WorkersCost = 1000


percOpex = 1.5


OPEX = CAPEX * percOpex/100

###################################
#   TABLA CAPEX
###################################

SCAPEX_eq = pd.Series([CAPEX_eq])
SCAPEX_inst = pd.Series([CAPEX_inst])
SCAPEX_dev = pd.Series([CAPEX_dev])
SCAPEX = pd.Series([CAPEX])
source_capex = ColumnDataSource(data=dict(capex_eq = SCAPEX_eq, capex_inst = SCAPEX_inst,
                                          capex_dev = SCAPEX_dev, capex_tot = SCAPEX))




columns_capex = [
    TableColumn(field="capex_eq", title="CAPEX Equipo",formatter=NumberFormatter(format="0.00")),
    TableColumn(field="capex_inst", title="CAPEX Instalación", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="capex_dev", title="CAPEX Desarrollo", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="capex_tot", title="CAPEX TOTAL", formatter=NumberFormatter(format="0.00"))
]

table_CAPEX = DataTable(columns=columns_capex, source=source_capex,width=600, height=450,
                      editable=True)

###################################
#   Condiciones para Calculadora
###################################

# SetTurno(df,turno, flow_p)
SetTMains(df,Tout_p)
SetTSet(df,Tin_p)

df = CallSWH(df,tilt,azim,Col,aCol,vol,sto_loss,year)


#########################################
#           BALANCE ANUAL (por 20 años)
#########################################


enerProcYear,enerAux_pump, enerAux_cald, enerPeakYear, enerStoYear = BalanceYear(df,tilt,azim,Col,aCol,vol,sto_loss,potHeater,effHeater,potHPump,effHPump,year)
# BalanceYear(df,tilt,azim,Col,aCol,vol,sto_loss,year)

potHeater_year = potHeater*24*30.5*12
potHPump_year = potHPump*24*30.5*12


balance_year = pd.read_csv(path + 'visualizaciones/swh_bhp_calc/resultados/balance_anual.csv')
# balance_year['enerHeater'] = (balance_year.enerProc-balance_year.enerSol)/(effHeater/100)
balance_year['enerHeater'] = potHeater_year*effHeater
balance_year['enerHeatPump'] = potHPump_year*effHPump
balance_year['Años'] = years_list
# balance_year.loc['Total TWh/año'] = balance_year.sum(numeric_only=True, axis = 0)*10**(-6)
# balance_year.Total.astype(str)
# balance_year.Total = balance_year.Total + 'TW'

# balance_year['Total',:1] = 20
# balance.drop(['Unnamed: 0'], axis = 1)

source_bal_year = ColumnDataSource(data=balance_year)
    
# df = CallSWH(df,tilt,azim,Col,aCol,vol,sto_loss,year)

# table_ener_year = TableEnerYear(df, Tout_h, Tin_h,effHeater,Col,year)
table_fuel = TableFuel(df,fuel,tilt,azim,Col,aCol,vol,sto_loss,potHeater,effHeater,year)
# table_steam = TableSteam(df,turno,flow_p, Tout_h, Tin_h,effHeater,cond,T_cond,p_steam,fuel)
    
enerSolYear = balance_year.enerSol


totSol_year = enerSolYear
totProc_year = enerProcYear
# totHeater_year = enerAuxYear
solFrac_year = totSol_year/totProc_year

    
# totSol_year = enerSolYear.sum()
# totProc_year = enerProcYear.sum()
# totHeater_year = enerAuxYear.sum()
# solFrac_year = totSol_year/totProc_year



#########################################
#           BALANCE MENSUAL
#########################################
# df = CallSWH(df,tilt,azim,Col,aCol,vol,sto_loss,year)

potHeater_month = potHeater*24*30.5
potHPump_month = potHPump*24*30.5

enerProc, enerAux_pump, enerAux_cald, enerSol, enerPeak, enerSto = BalanceMonth(df,tilt,azim,Col,aCol,vol,sto_loss,potHeater,effHeater,potHPump,effHPump,year)
balance = pd.read_csv(path + 'visualizaciones/swh_bhp_calc/resultados/balances_mensuales_año/balance_mensual_'+ str(year) +'.csv')
balance['enerHeater'] = (balance.enerProc-balance.enerSol)/(effHeater/100)
balance_year['enerHeater'] = potHeater_month*effHeater
balance_year['enerHeatPump'] = potHPump_month*effHPump
balance['Meses'] = meses
balance.loc['Total'] = balance.sum(numeric_only=True, axis = 0)

source_bal_month = ColumnDataSource(data=balance)
    
EnerHeaterOp = balance.enerHeater.sum()

table_ener = TableEner(df, Tout_h, Tin_h,potHeater,effHeater,potHPump,effHPump,Col,year)
table_fuel = TableFuel(df,fuel,tilt,azim,Col,aCol,vol,sto_loss,potHPump,effHeater, year)
table_capexu = TableCapexU(CEQ_1, CEQ_2, CEQ_3, CEQ_4, CEQ_5, CEQ_6,
                CIN_1, CIN_2, CIN_3, CIN_4, CIN_5, CIN_6, CIN_7,
                CDE_1, CDE_2,FIT)
    


# table_steam = TableSteam(df,turno,flow_p, Tout_h, Tin_h,effHeater,cond,T_cond,p_steam,fuel)

# totSol = enerSol #enerSol.sum()
# totProc = enerProc.sum()
# totHeater = enerAux.sum()
# solFrac = totSol/totProc



###############################
# INFORMACION EVALUACION ECONOMICA
#################################

# años del contrato
anho_contr = 20
# años evaluación proyecto
anho_proy = 25
# años a depreciar el equipo
anho_depr = 8
# valor depreciable
val_depr = CAPEX/anho_depr
# porcentaje deuda
perc_deuda = 0
# monto de la deuda
deuda = perc_deuda/100 * CAPEX
# porcentaje equity
perc_equi = 100 - perc_deuda
# tasa anual de la deuda
tasa_deuda = 2
# años para pagar la deuda
pago_deuda = 8
# tasa anual equity
tasa_equi = 8
# impuesto primera categoría
impuesto = 27   
# inflacion USA
infl_usa = 2
# inflación Chile
infl_cl = 2
# diferencial inflacionario
dif_infl = (1+infl_usa/100) / (1+infl_cl/100) 

#Volumen agua (indicar proceso) (m3)
vol_agua = 100

#Costo agua m3 (US$/m3)
agua_cost = 30

# # Trabajadores ( # Personas)
Workers = 50

# Costo mensual trabajador (US$/trabajador)
CostW = 1000

#Porcentaje Opex SST (%)
perc_SST = 10

#Porcentaje Opex Cald (%)
perc_Cald = 10

#Porcentaje Opex Almac (%)
perc_Almac = 10

#Porcentaje Opex PipHEX (%)
perc_PipHEX = 10



table_eval,annual_res, annual_proy = LCOH_calc(CAPEX,OPEX,tasa_deuda, pago_deuda,perc_deuda,impuesto,tasa_equi,dif_infl,infl_cl,
                                  anho_contr,anho_proy,val_depr,anho_depr,totSol_year,indSol,indFuel,costFuel)

table_opex = TableOpexY(Ecost,EnerHeaterOp,vol_agua,agua_cost,Workers,CostW,CEQ_1,CEQ_4,CEQ_2,
               COST_PIPHEX,perc_SST,perc_Cald,perc_Almac,perc_PipHEX)

table_res_anho = TableRes(anho_contr,anho_proy)

annual_res.costSol[0] = np.nan
an=pd.date_range('2021-01',freq='A',periods=len(annual_res))
annual_res.index = an

lcoh_f = float(table_fuel[2])

cfuel = Vector(lcoh_f,anho_proy,indFuel)
an=pd.date_range('2021-01',freq='A',periods=len(cfuel))
cfuel = pd.DataFrame(cfuel,index=an)
cfuel = cfuel.rename(columns={0:'costFuel'})
cfuel = cfuel.rename_axis(None, axis=1).rename_axis('date', axis=0)

csol=annual_res.costSol
ener_cst = pd.concat([cfuel,csol], axis=1)


lcoh = float(table_eval['LCOH (US$/MWh)'])
source_flujo = ColumnDataSource(data=dict(x1=annual_res.index.year,ingEner=annual_res.ing_ener,
                                          opex=annual_res.opex,utils=annual_res.utilidades,
                                          perd=annual_res.perdidas,base_imp=annual_res.base_imp,
                                          imp_pc=annual_res.imp_PC,util_imp=annual_res.util_imp,
                                          fljNeto=annual_res.flujo_neto,fljAcum=annual_res.flujo_acum,
                                          van_vect=annual_res.vect_VAN)) 

source_cost = ColumnDataSource(data=ener_cst)
    
columns = [
    TableColumn(field="x1", title="Año",width=25),
    TableColumn(field="ingEner", title="Ingreso Energía (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="opex", title="OPEX (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="utils", title="Utilidades (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="base_imp", title="Base impuesto (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="util_imp", title="Utilidades despues impuesto (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="fljNeto", title="Flujo neto (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="fljAcum", title="Flujo acumulado (kUS$)", formatter=NumberFormatter(format="0.00"))
]

data_table = DataTable(columns=columns, source=source_flujo,width=700, height=480)


#################################
cProy,table_proy = TableProy(lcoh,solFrac_year,totSol_year,indSol,fuel,costFuel,indFuel,effHeater,anho_contr,anho_proy)
anhoProyect = np.arange(0,anho_proy+1,1)
an=pd.date_range('2021-01',freq='A',periods=len(cProy))
cProy.index = an
source_proy = ColumnDataSource(data=dict(x1=cProy.index,CSol=cProy.csol,CFuel=cProy.cfuel,CFoss=cProy.cfoss,CSST=cProy.SST))

###############################################################################################                    
TOOLS="hover,crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select,save"

fill=0.2
plot_w = 1000
plot_h = 450
#################################

#################################
mina_nombre=list(minas.Mina)
dropdownData = Select(value=lugar, title="Lugar",options=mina_nombre) 

solData=['Meteonorm','Explorador Solar']
dropdownSolData = Select(value='Explorador Solar', title="Dato radiación",options=solData) 
incl = TextInput(value=str(tilt), title="Inclinación:")
orie = TextInput(value=str(azim), title="Orientación:")
buttCalcRad = Button(label="Calcular", button_type="success",width=100)


dropdownYearData = Select(value = '2024', title = 'Año a analizar', options = years_list)

########################
# INFO GRAF RADIACIÓN
########################
rads = ['GHI','POA']
palette = ["green", "blue"]
p_rad = Figure(tools=TOOLS, plot_width=plot_w, plot_height=plot_h, title="Recurso solar en " + lugar,
            y_axis_label= "Radiación (kWh/m2/mes)", x_range=FactorRange(*x_month))
p_rad.vbar(x='x', top='rad', source = source_rad, width=0.45,
      fill_color=factor_cmap('x', palette=palette, factors=rads, start=1, end=2),
      line_color=factor_cmap('x', palette=palette, factors=rads, start=1, end=2))
p_rad.xaxis.major_label_orientation = 1
p_rad.select_one(HoverTool).tooltips = [
    ('Radiación (kWh/mes): ', '@rad{0.0}')]
p_rad.select_one(HoverTool).mode='vline'
infoRad = PreText(text=str(table_rad), width=600)




#################################
#INFO VARIABLES e AL GRAFICO BALANCE DE ENERGÍA
##################################
Tin_proc = TextInput(value=str(Tin_p), title="Tin proceso:")
Tout_proc = TextInput(value=str(Tout_p), title="Tout proceso:")        
# flow_proc = TextInput(value=str(flow_p), title="Flujo proceso (m3/hr):")
# Turnos = ['24/7','24/6','17/6','14/6', 'Agrosuper ACS','Agrosuper Sanit','Watts','Sopraval escaldado','Sopraval producción','Lucchetti']
# selectTurno = Select(value="Agrosuper Sanit", title="Turno de trabajo",options=Turnos)

eff_heater= TextInput(value=str(effHeater), title="Eficiencia caldera eléctrica (%):")
pot_heater= TextInput(value=str(potHeater), title="Potencia caldera eléctrica (kWh):")

eff_hpump= TextInput(value=str(effHPump), title="Eficiencia bomba de calor (%):")
pot_hpump= TextInput(value=str(potHPump), title="Potencia bomba de calor (kWh):")

fuels = ['Diesel','GN','GLP','Kerosene','Petróleo 5','Petróleo 6','Carbón','Leña','Biomasa']
dropdownFuel = Select(value='Diesel',title='Combustible',options=fuels)
#fluids = ['Agua','Vapor']
#dropdownFluid = Select(value='Vapor', title='Fluido caldera',options=fluids)

perc_cond = TextInput(value=str(cond),title = '% condensado (solo vapor)')
presion_vapor = TextInput(value=str(p_steam),title = 'Presión de vapor (barg, solo vapor)')
temp_cond = TextInput(value=str(T_cond),title = 'Temperatura condensado')


cols = list(cst.keys())
selectCol = Select(value=Col, title="Colector solar",options=cols)
areaCol = TextInput(value=str(aCol), title="Área colectores:")
vol_sto = TextInput(value=str(vol), title="Volumen acumulación (m3):")
loss_sto= TextInput(value=str(sto_loss), title="Pérdidas almacenamiento (%):")

buttCalcEnergyYear = Button(label="Calcular balance anual", button_type="success",width=100)

buttCalcEnergyMonth = Button(label="Calcular balance mensual", button_type="success",width=100)

####################################
#GRAFICO BALANCE DE ENERGÍA ANUAL
####################################
ener = ['Proceso','Ener Total','Caldera eléctrica','Bomba de calor','Ener Solar']
ener_year, x_year = SystemYear(df,tilt,azim,Col,aCol,vol,sto_loss,effHeater,year) ####################
source_ener_year = ColumnDataSource(data=dict(x=x_year, ener=ener_year))
palette = ["red", "yellow", "black","blue","orange"]
    
p_year = Figure(tools=TOOLS, x_range=FactorRange(*x_year),plot_width=plot_w, plot_height=plot_h, title="Balance de energía anual",
            y_axis_label="Energía (MWh/año)")
p_year.vbar(x='x', top='ener', width=1.0, source=source_ener_year, 
      fill_color=factor_cmap('x', palette=palette, factors=ener, start=1, end=2),
      line_color='white')
p_year.xaxis.major_label_orientation = 1

p_year.select_one(HoverTool).tooltips = [
    ('Energía (MWh/año)', '@ener{0.0}')]
p_year.select_one(HoverTool).mode='vline'


cols_balance_year = [
        TableColumn(field="Años", title="Año",width=60),
        TableColumn(field="enerProc", title="E proceso (MWh/año)",width=150, formatter=NumberFormatter(format="0.00")),
        TableColumn(field="enerCald", title="E caldera eléctrica (MWh/año)",width=150, formatter=NumberFormatter(format="0.00")),
        TableColumn(field="enerHPump", title="E bomba de calor (MWh/año)",width=150, formatter=NumberFormatter(format="0.00")),
        TableColumn(field="enerSol", title="E solar (MWh/año)",width=150, formatter=NumberFormatter(format="0.00")),
        TableColumn(field="SF", title="Fracción solar (%)",width=150, formatter=NumberFormatter(format="0.0"))]

table_bal_year = DataTable(columns=cols_balance_year, source=source_bal_year,width=600, height=450,
                      editable=True)




####################################
#GRAFICO BALANCE DE ENERGÍA MENSUAL
####################################
ener = ['Proceso','Ener Total','Caldera eléctrica','Bomba de calor','Ener Solar']
ener_month, x_month = SystemMonth(df,tilt,azim,Col,aCol,vol,sto_loss,effHeater,year)
source_ener_month = ColumnDataSource(data=dict(x=x_month, ener=ener_month))
palette = ["red", "yellow", "black","blue","orange"]
    
p_month = Figure(tools=TOOLS, x_range=FactorRange(*x_month),plot_width=plot_w, plot_height=plot_h, title="Balance de energía mensual",
            y_axis_label="Energía (MWh/mes)")
p_month.vbar(x='x', top='ener', width=1.0, source=source_ener_month, 
      fill_color=factor_cmap('x', palette=palette, factors=ener, start=1, end=2),
      line_color='white')
p_month.xaxis.major_label_orientation = 1

p_month.select_one(HoverTool).tooltips = [
    ('Energía (MWh/mes)', '@ener{0.0}')]
p_month.select_one(HoverTool).mode='vline'


cols_balance_month = [
        TableColumn(field="Meses", title="Mes",width=60),
        TableColumn(field="enerProc", title="E proceso (MWh/año)",width=150, formatter=NumberFormatter(format="0.00")),
        TableColumn(field="enerCald", title="E caldera eléctrica (MWh/año)",width=150, formatter=NumberFormatter(format="0.00")),
        TableColumn(field="enerHPump", title="E bomba de calor (MWh/año)",width=150, formatter=NumberFormatter(format="0.00")),
        TableColumn(field="enerSol", title="E solar (MWh/año)",width=150, formatter=NumberFormatter(format="0.00")),
        TableColumn(field="SF", title="Fracción solar (%)",width=150, formatter=NumberFormatter(format="0.0"))]

table_bal_month = DataTable(columns=cols_balance_month, source=source_bal_month,width=600, height=450,
                      editable=True)
###################################################
#fs_mes = enerSol/enerProc*100
#source_fs = ColumnDataSource(data=dict(x=meses,y=fs_mes))
#p3 = Figure(tools=TOOLS,plot_width=plot_w, plot_height=plot_h, title="Fracción solar mensual",
#            y_axis_label="% aporte solar", x_range=FactorRange(*meses))
#p3.vbar(x='x', top='y', width=0.4, source=source_fs, 
#       fill_color='orange', line_color='white')
#p3.xaxis.major_label_orientation = 1
#######
infoEner = PreText(text=str(table_ener), width=550)
infoFuel = PreText(text=str(table_fuel), width=480)
infoCapexu = PreText(text=str(table_capexu), width=550)
infoOpex = PreText(text=str(table_opex), width=550)
infoResAnho = PreText(text=str(table_res_anho), width=550)

# infoSteam = PreText(text=str(table_steam), width=480)
######################
# DATOS TABLA ECONÓMICA
######################
wdt = 250

CCol = TextInput(value=str(costCol_m2), title="Costo SST (US$/m2):",width=wdt)

CCol_inst = TextInput(value=str(cost_instCol_m2), title="Costo instalación SST (US$/m2):",width=wdt)

# CBOP = TextInput(value=str(costBOP), title="Costo instalación colector (US$/m2):",width=wdt)

C_instBOP = TextInput(value=str(cost_instBOP), title="Costo instalación balance de planta (US$/m2):",width=wdt)

CSto = TextInput(value=str(costSto), title="Costo almacenamiento (US$/m3):",width=wdt)

Cinst_Sto = TextInput(value=str(cost_instSto), title="Costo instalación almacenador (US$):",width=wdt)

CCald = TextInput(value=str(costCald), title="Costo caldera eléctrica (US$):",width=wdt)

C_instCald = TextInput(value=str(cost_instCald), title="Costo instalación caldera eléctrica (US$):",width=wdt)

CPiping = TextInput(value=str(costPiping), title="Costo piping (US$/m):",width=wdt)

C_instPiping = TextInput(value=str(cost_instPiping), title="Costo instalación piping (US$/m):",width=wdt)

CHEX = TextInput(value=str(costHEX), title="Costo HEX (US$):",width=wdt)

C_instHEX = TextInput(value=str(cost_instHEX), title="Costo instalación HEX (US$):",width=wdt)

C_prepTerr = TextInput(value=str(cost_prepTerr), title="Costo preparación terreno (US$/m2):",width=wdt)

CIng = TextInput(value=str(CostIng), title="Costo ingeniería (US$):",width=wdt)

CDev = TextInput(value=str(CostDev), title="Costo desarrollo (US$):",width=wdt)

fitm2 = TextInput(value=str(FIT_m2), title="Envío, seguro e impuesto (US$/m2):",width=wdt)

# percFee = TextInput(value=str(perc_fee), title="Fee desarrollador (% CAPEX)",width=wdt)



# POPEX = TextInput(value=str(percOpex), title="OPEX (% CAPEX):",width=wdt)

indexSolar = TextInput(value=str(indSol), title="Indexación solar (%):",width=wdt)

CFuel = TextInput(value=str(costFuel), title="Precio combustible (US$/unidad):",width=wdt)

indexFuel = TextInput(value=str(indFuel), title="Indexación combustible (%):",width=wdt)

anhoContr = TextInput(value=str(anho_contr), title="Años de contrato ESCO:",width=wdt)

anhoProy = TextInput(value=str(anho_proy), title="Años evaluación escenario:",width=wdt)

anhoDepr = TextInput(value=str(anho_depr), title="Años depreciación:",width=wdt)

percDeuda = TextInput(value=str(perc_deuda), title="Porcentaje deuda:",width=wdt)

tasaDeuda = TextInput(value=str(tasa_deuda), title="Tasa deuda (%):",width=wdt)

pagoDeuda = TextInput(value=str(pago_deuda), title="Años pago deuda:",width=wdt)

tasaEqui = TextInput(value=str(tasa_equi), title="Tasa capital propio (%):",width=wdt)

inflChile = TextInput(value=str(infl_cl), title="Inflación Chile (%):",width=wdt)

CostE = TextInput(value=str(Ecost), title="Costo energía eléctrica (US$/kW):",width=wdt)

########################
#   SEC OPEX
########################


########################
#   SEC OPEX
########################

VolAgua = TextInput(value=str(vol_agua), title="Vólumen agua m³:",width=wdt)
CostAg = TextInput(value=str(agua_cost), title="Costo m³ agua (US$/m³):",width=wdt)
Wkers = TextInput(value=str(Workers), title="Trabajadores (# Personas):",width=wdt)
WCost = TextInput(value=str(CostW), title="Costo mensual trabajador (US$/persona):",width=wdt)
PercSST = TextInput(value=str(perc_SST), title="OPEX SST (% CAPEX SST):",width=wdt)
PercCald = TextInput(value=str(perc_Cald), title="OPEX Caldera (% CAPEX Caldera):",width=wdt)
PercAlmac = TextInput(value=str(perc_Almac), title="OPEX Almacenamiento (% CAPEX Almacenamiento):",width=wdt+20)
PercPipHEX = TextInput(value=str(perc_PipHEX), title="OPEX Piping & HEX (% CAPEX Piping & HEX):",width=wdt)



#####################
buttCalcEcon = Button(label="Calcular", button_type="success",width=wdt)
infoEval = PreText(text=str(table_eval), width=320)

# infoProy = PreText(text=str(table_proy), width=320)
################################################
TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select,save"
plot_w = 700
plot_h = 360

# ###############################################
# #GRÁFICO COSTO DE ENERGÍA (NO FUNCIONA)
# ###############################################
# p1 = Figure(tools=TOOLS,title="Costo de energía", x_axis_label="Fecha", y_axis_label= "Costo (US$/MWh)", 
#             plot_width=plot_w, plot_height=plot_h)

# line1_p1 = p1.line(x='date',y='costFuel',source=source_cost,color='red',legend_label='Costo MWh combustible')
# line2_p1 = p1.line(x='date',y='costSol',source=source_cost,color='green',legend_label='Costo MWh solar')

# p1.xaxis.formatter=DatetimeTickFormatter(hours = ['%d/%m %H:00'],days = ['%F'])
# p1.legend.click_policy="hide"
# p1.add_tools(HoverTool(renderers=[line1_p1], tooltips=[('Fecha: ', '@date{%F}'),
#     ('Costo combustible (US$/MWh): ', '@costFuel{0.0}'),
#     ('Costo solar (US$/MWh): ', '@costSol{0.0}')],mode='vline',formatters={'@date':'datetime'}))
# ###########################
# #GRÁFICO COSTO DE PROYECTOS
# ###########################
# p2 = Figure(tools=TOOLS,title="Costo proyectos", x_axis_label="Fecha", y_axis_label= "Pago (kUS$/año)", 
#             plot_width=plot_w, plot_height=plot_h, x_range=p1.x_range)

# line1_p2 = p2.line(x='x1',y='CFuel',source=source_proy,color='red',line_width=1.2, legend_label='Pago fósil con SST')
# line2_p2 = p2.line(x='x1',y='CSol',source=source_proy,color='green',line_width=1.2,legend_label='Pago energía solar')
# line3_p2 = p2.line(x='x1',y='CSST',source=source_proy,color='blue',line_width=2.4,legend_label='Pago total con SST')
# line4_p2 = p2.line(x='x1',y='CFoss',source=source_proy,color='black',line_width=2.4,legend_label='Pago sin SST')

# p2.xaxis.formatter=DatetimeTickFormatter(hours = ['%d/%m %H:00'],days = ['%F'])
# p2.legend.click_policy="hide"
# p2.add_tools(HoverTool(renderers=[line1_p2], tooltips=[('Fecha: ', '@x1{%F}'),
#     ('Pago fósil con SST (kUS$): ', '@CFuel{0.0}'),
#     ('Pago energía solar (kUS$): ', '@CSol{0.0}'),
#     ('Pago total con SST (kUS$): ', '@CSST{0.0}'),
#     ('Pago sin SST (kUS$): ', '@CFoss{0.0}')],mode='vline',formatters={'@x1':'datetime'}))
# ###############################################
# ###############################################

# ###############################################
# ###############################################
# from funciones_econ import RandomWalk, EnerConvProy, ProyMonth, MonteCarloParallel, cdf

# # https://www.engineeringtoolbox.com/energy-content-d_868.html
# indicadores = {'Mont Belvieu'   : {'std_unit':'gal',    'PCI':91330,    'abrev':'mont'},
#               'Brent'          : {'std_unit':'barrel', 'PCI':5800000,'abrev':'brent'},
#               'WTI'            : {'std_unit':'barrel', 'PCI':5800000,  'abrev':'wti'},
#               'Henry Hub'      : {'std_unit':'MMBtu', 'PCI':1e6,         'abrev':'hhub'},
#               'GLP ENAP'       : {'std_unit':'ton',    'PCI':12956008,        'abrev':'glp'},
#               'DSL ENAP'       : {'std_unit':'m3',     'PCI':35960000,        'abrev':'dsl'}}

# # GLP   264.17*0.537*91330
# #path = '/Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/datos/Combustibles/indicadores'
# ################################################
# # Lista histórica de precios de combustibles, según la EIA

# #https://www.eia.gov/dnav/pet/hist_xls/EER_EPLLPA_PF4_Y44MB_DPGd.xls
# mont = pd.read_excel(path + '/datos/Combustibles/EER_EPLLPA_PF4_Y44MB_DPGd.xls',sheet_name='Data 1',skiprows=2)
# mont.set_index('Date',inplace=True)
# mont = mont.rename(columns={'Mont Belvieu, TX Propane Spot Price FOB (Dollars per Gallon)':'std_unit'})

# wti = pd.read_excel(path + '/datos/Combustibles/RWTCd.xls',sheet_name='Data 1',skiprows=2)
# wti.set_index('Date',inplace=True)
# wti = wti.rename(columns={'Cushing, OK WTI Spot Price FOB (Dollars per Barrel)':'std_unit'})

# brent = pd.read_excel(path + '/datos/Combustibles/RBRTEd.xls',sheet_name='Data 1',skiprows=2)
# brent.set_index('Date',inplace=True)
# brent = brent.rename(columns={'Europe Brent Spot Price FOB (Dollars per Barrel)':'std_unit'})

# hhub = pd.read_excel(path + '/datos/Combustibles/RNGWHHDd.xls',sheet_name='Data 1',skiprows=2)
# hhub.set_index('Date',inplace=True)
# hhub = hhub.rename(columns={'Henry Hub Natural Gas Spot Price (Dollars per Million Btu)':'std_unit'})

# # Lista histórica de precios de combustibles, según ENAP
# enp_glp = pd.read_csv(path + '/datos/Combustibles/glp_enap.csv',date_parser=['Date'])
# enp_glp.set_index('Date',inplace=True)
# enp_glp = enp_glp.rename(columns={'GLP_usd_ton':'std_unit'})
# enp_glp.index = pd.to_datetime(enp_glp.index)

# enp_dsl = pd.read_csv(path + '/datos/Combustibles/dsl_enap.csv',date_parser=['Date'])
# enp_dsl.set_index('Date',inplace=True)
# enp_dsl = enp_dsl.rename(columns={'Diesel_m3':'std_unit'})
# enp_dsl.index = pd.to_datetime(enp_dsl.index)


# ########################################################
# # Botón para correr el random walk del índice a analizar
# ########################################################
# indice = 'Mont Belvieu'
# buttCalcWalk = Button(label="Random", button_type="success")
# ind = Select(value=indice, title='Indicador', options=list(indicadores.keys()))

# # Factor a sumar en caso de Chile
# factInd = 0
# fctInd = TextInput(value=str(factInd), title="Valor a agregar Chile (+)",width=wdt)

# ############
# # Definir el índice a analizar
# df = mont
# # Llamar a función RandomWalk, definida en funciones_econ
# # toma el df de los valores de EIA o ENAP, según el índicador definido y lo proyecta 30 años
# rnd_walk = RandomWalk(df,indice,30)
# # Conversión energética desde la unidad estandar a MWh y MMBtu
# rnd_walk = EnerConvProy(rnd_walk,indice,'Semanal','proy')
# source_rnd = ColumnDataSource(data=rnd_walk)
# ####################
# #GRÁFICO RANDOMWALK
# ####################
# p3 = Figure(tools=TOOLS,title="", x_axis_label="Fecha", y_axis_label= "Precio (USD/unidad standar)", 
#             plot_width=plot_w+450, plot_height=plot_h+100)
# line1_p3 = p3.line('Date','std_unit',color='black',source=source_rnd, legend_label='Indice')
# line2_p3 = p3.line('Date','proy',color='green',source=source_rnd, legend_label='Random walk proy')
# p3.xaxis.formatter=DatetimeTickFormatter()

# p3.add_tools(HoverTool(renderers=[line1_p3], tooltips=[('Fecha: ', '@Date{%F}'),
#     ('Costo histórico (US$/unidad): ', '@std_unit{0.00}'),
#     ('Costo histórico (US$/MMBtu): ', '@MMBtu{0.00}'),
#     ('Costo histórico (US$/MWh): ', '@MWh{0.00}')],mode='vline',formatters={'@Date':'datetime'}))
# p3.add_tools(HoverTool(renderers=[line2_p3], tooltips=[('Fecha: ', '@Date{%F}'),
#     ('Costo proyectado (US$/unidad): ', '@proy{0.00}'),
#     ('Costo proyectado (US$/MMBtu): ', '@MMBtu_proy{0.00}'),
#     ('Costo proyectado (US$/MWh): ', '@MWh_proy{0.00}')],mode='vline',formatters={'@Date':'datetime'}))
# #####################################################################

# df_month, table_proy2 = ProyMonth(rnd_walk,'gen',indice,lcoh,indSol,anho_contr,anho_proy,effHeater,factInd,inicSolar = 2022)

# sourceMonth = ColumnDataSource(data=df_month)

# ######################################################################
# #GÁFRICO COMPARACIÓN PRECIO ENERGÍA POR COSTO DE COMBUSTIBLES VS SOLAR
# ######################################################################
# p4 = Figure(tools=TOOLS,title="Precio energía", x_axis_label="Fecha", y_axis_label= "Precio (USD/MWh)", 
#             plot_width=plot_w, plot_height=plot_h)
# line1_p4 = p4.line('Date','MWh_cl',color='black',source=sourceMonth, legend_label='Fósil')
# line2_p4 = p4.line('Date','precioSol',color='green',source=sourceMonth, legend_label='Solar')
# p4.xaxis.formatter=DatetimeTickFormatter()
# p4.legend.click_policy="hide"
# p4.add_tools(HoverTool(renderers=[line1_p4], tooltips=[('Fecha: ', '@Date{%F}'),
#     ('Costo combustible (US$/MWh): ', '@MWh_cl{0.0}'),
#     ('Costo solar (US$/MWh): ', '@precioSol{0.0}')],mode='vline',formatters={'@Date':'datetime'}))
# #############################################
# #GRÁFICO COMPARACIÓN COSTOS PROYECTOS Y PAGOS
# #############################################
# p5 = Figure(tools=TOOLS,title="Costo proyectos", x_axis_label="Fecha", y_axis_label= "Pago (kUS$/año)", 
#             plot_width=plot_w, plot_height=plot_h)

# line1_p5 = p5.line(x='Date',y='fossPay',source=sourceMonth,color='red',line_width=1.2, legend_label='Pago fósil con SST')
# line2_p5 = p5.line(x='Date',y='solPay',source=sourceMonth,color='green',line_width=1.2,legend_label='Pago energía solar')
# line3_p5 = p5.line(x='Date',y='totPay',source=sourceMonth,color='blue',line_width=2.4,legend_label='Pago total con SST')
# line4_p5 = p5.line(x='Date',y='convPay',source=sourceMonth,color='black',line_width=2.4,legend_label='Pago sin SST')
# p5.xaxis.formatter=DatetimeTickFormatter()
# p5.legend.click_policy="hide"
# p5.add_tools(HoverTool(renderers=[line1_p5], tooltips=[('Fecha: ', '@Date{%F}'),
#     ('Pago fósil con SST (kUS$): ', '@fossPay{0.0}'),
#     ('Pago energía solar (kUS$): ', '@solPay{0.0}'),
#     ('Pago total con SST (kUS$): ', '@totPay{0.0}'),
#     ('Pago sin SST (kUS$): ', '@convPay{0.0}')],mode='vline',formatters={'@Date':'datetime'}))
# ###############################################    

# infoProy2 = PreText(text=str(table_proy2), width=320)

# N_iter = 500

# ahr1 = MonteCarloParallel(df,0,indice,lcoh,indSol,anho_contr,anho_proy,effHeater,factInd,N_iter = N_iter, inicSolar = 2022)
# ahr = np.array(ahr1)
# hist, edges = np.histogram(ahr, density=True, bins=20)
# hist_df = pd.DataFrame({'column': hist,
#                         "left": edges[:-1],
#                         "right": edges[1:]})
# hist_df["interval"] = ["%d to %d" % (left, right) for left, 
#                         right in zip(hist_df["left"], hist_df["right"])]

# src_hist = ColumnDataSource(hist_df)

# ################################
# #HISTOGRAMA INDICADOR POR ÍNDICE
# ################################

# p6 = Figure(title='Histograma, ' + str(N_iter) + ', indicador ' + indice,
#             tools=TOOLS,plot_width=plot_w, plot_height=plot_h+200) #, background_fill_color="#fafafa"
# p6.quad(top='column', bottom=0, left='left', right='right',
#           fill_color="navy", line_color="white", alpha=0.5, source=src_hist)


# x_data, y_data = cdf(ahr1)
# src_cdf = ColumnDataSource(data=dict(x=x_data,y=y_data))
# ##############
# #HISTOGRAMA???
# ##############
# p7 = Figure(tools=TOOLS,title = 'Histograma, ' + str(N_iter) + ', indicador ' + indice,
#             plot_width=plot_w, plot_height=plot_h+200) #, background_fill_color="#fafafa"
# p7.line('x','y',source=src_cdf)         
  

# buttCalcMC = Button(label="Monte Carlo", button_type="success")
# n_esc = TextInput(value=str(N_iter), title="Número de escenarios",width=wdt)

#################################
#################################

def CalcRad():
    '''
    Actualiza la simulación de radiación según los filtros de lugar,
    datos solares, inclinación y orientación establecidos.
    
    Variables a definir
    --------------------
    lugar: Lugar a evaluar.
    dataSol: De donde se obtienen los datos solares (ej: explorador solar).
    tilt: Inclinación campo solar.
    azim: Azimuth.
    
    Returns
    -------
    df : DataFrame
        DF con los filtros aplicados.

    '''
    ######################
    lugar = dropdownData.value
    dataSol = dropdownSolData.value
    tilt = float(incl.value)
    azim = float(orie.value)
        
    df = CopyRadFile(lugar,dataSol)
    df = CallSWH(df,tilt,azim,Col,aCol,vol,sto_loss,year)
    
    dropdownYearData
    rad_month, x_month = RadMonth(df)
    new_data=dict(x=x_month, rad=rad_month)
    source_rad.data = new_data

    table_rad = TableRad(df)
    data_lugar = minas[minas.Mina == lugar]
    ghi_sg = data_lugar.GHI_SG.iloc[0]
    table_rad['GHI Solargis (kWh/m2/año)'] = ghi_sg
    
    infoRad.text = str(table_rad)
   
    return df

# def CalcRad_Year():
#     '''
#     Actualiza la simulación de radiación según los filtros de lugar,
#     datos solares, inclinación y orientación establecidos.
    
#     Variables a definir
#     --------------------
#     lugar: Lugar a evaluar.
#     dataSol: De donde se obtienen los datos solares (ej: explorador solar).
#     tilt: Inclinación campo solar.
#     azim: Azimuth.
    
#     Returns
#     -------
#     df : DataFrame
#         DF con los filtros aplicados.

#     '''
#     ######################
#     lugar = dropdownData.value
#     dataSol = dropdownSolData.value

#     tilt = float(incl.value)
#     azim = float(orie.value)
        
#     df = CopyRadFile(lugar,dataSol)
#     df = CallSWH(df,tilt,azim,Col,aCol,vol,sto_loss,year)
    
    
#     rad_month, x_month = RadMonth(df)
#     new_data=dict(x=x_month, rad=rad_month)
#     source_rad.data = new_data

#     table_rad = TableRad(df)
#     data_lugar = minas[minas.Mina == lugar]
#     ghi_sg = data_lugar.GHI_SG.iloc[0]
#     table_rad['GHI Solargis (kWh/m2/año)'] = ghi_sg
    
#     infoRad.text = str(table_rad)
   
#     return df

def CalcSystemMonth(temp):
    '''
    A través de la simulación en SAM hecha por CallSWH calcula la 
    energía en función del sistema y variables seleccionadas.
    
    Variables a definir.
    ----------------------
    tilt:Inclinación campo solar.
    azim: Azimuth.
    
    Tin_p: Temperatura de entrada al proceso.
    Tout_p: Temperatura de salida del proceso.
    
    flow_p: Flujo de agua en el proceso.
    p_steam: Presión de vapor.
    
    T_cond: Temperatura de condensado.
    cond: % de condensación del vapor.
    
    Col: Colector.
    aCol: Área de colector.
    
    Vol: Volumen de almacenamiento.    
    sto_loss: % Pérdida de almacenamiento.    
    
    turno: Turno de trabajo de la empresa.
    
    effHeater: Eficiencia Caldera.
    fuel: Combustible.
    
    
    Returns
    -------
    None.

    '''
    df   = CalcRad()
    tilt = float(incl.value)
    azim = float(orie.value)
    
    Tin_p  = float(Tin_proc.value)
    Tout_p = float(Tout_proc.value)
    # flow_p = float(flow_proc.value)
    # turno = str(selectTurno.value)
    
    effHeater = float(eff_heater.value)
    # fuel   = str(dropdownFuel.value)
    
    year = int(years_button_group.active)
    year = years[year]
    

    # p_steam = float(presion_vapor.value)
    # cond = float(perc_cond.value)
    # T_cond = float(temp_cond.value)
    
    Col = selectCol.value
    aCol = float(areaCol.value)
    vol  = float(vol_sto.value)
    sto_loss = float(loss_sto.value)
    # year = 
    
    # SetTurno(df,turno)
    SetTMains(df,Tout_p)
    SetTSet(df,Tin_p)
    
    # df = CallSWH(df,tilt,azim,Col,aCol,vol,sto_loss,year)
   
    enerProc, enerAux_pump, enerAux_cald, enerPeak, enerSto = BalanceMonth(df,tilt,azim,Col,aCol,vol,sto_loss,potHeater,effHeater,potHPump,effHPump,year)
    balance_month = pd.read_csv(path + 'visualizaciones/swh_bhp_calc/resultados/balances_mensuales_año/balance_mensual_'+ str(year)+'.csv')
    balance_month['enerHeater'] = (balance_month.enerProc-balance_month.enerSol)/(effHeater/100)
    balance_month['Meses'] = meses
    source_bal_month.data = balance_month
    
    ener_month, x_month = SystemMonth(df,tilt,azim,Col,aCol,vol,sto_loss,effHeater,year)
    new_data_month=dict(x=x_month, ener=ener_month)
    source_ener_month.data = new_data_month
    
    
def CalcSystemYear():
    '''
    A través de la simulación en SAM hecha por CallSWH calcula la 
    energía en función del sistema y variables seleccionadas.
    
    Variables a definir.
    ----------------------
    tilt:Inclinación campo solar.
    azim: Azimuth.
    
    Tin_p: Temperatura de entrada al proceso.
    Tout_p: Temperatura de salida del proceso.
    
    flow_p: Flujo de agua en el proceso.
    p_steam: Presión de vapor.
    
    T_cond: Temperatura de condensado.
    cond: % de condensación del vapor.
    
    Col: Colector.
    aCol: Área de colector.
    
    Vol: Volumen de almacenamiento.    
    sto_loss: % Pérdida de almacenamiento.    
    
    turno: Turno de trabajo de la empresa.
    
    effHeater: Eficiencia Caldera.
    fuel: Combustible.
    
    
    Returns
    -------
    None.

    '''
    df   = CalcRad()
    tilt = float(incl.value)
    azim = float(orie.value)
    
    Tin_p  = float(Tin_proc.value)
    Tout_p = float(Tout_proc.value)
    # flow_p = float(flow_proc.value)
    # turno = str(selectTurno.value)
    
    effHeater = float(eff_heater.value)
    potHeater = float(pot_heater.value)
    effHPump = float(eff_hpump.value)
    potHPump = float(pot_hpump.value)
    # fuel   = str(dropdownFuel.value)
    
    year = int(years_button_group.active)
    year = years[year]
    

    # p_steam = float(presion_vapor.value)
    # cond = float(perc_cond.value)
    # T_cond = float(temp_cond.value)
    
    Col = selectCol.value
    aCol = float(areaCol.value)
    vol  = float(vol_sto.value)
    sto_loss = float(loss_sto.value)
       
    # SetTurno(df,turno)
    SetTMains(df,Tout_p)
    SetTSet(df,Tin_p)
    
    df = CallSWH(df,tilt,azim,Col,aCol,vol,sto_loss,year)
    
    enerProc, enerAux_pump, enerAux_cald, enerPeak, enerSto = BalanceYear(df,tilt,azim,Col,aCol,vol,sto_loss,potHeater,effHeater,potHPump,effHPump,year)
    
    balance_year = pd.read_csv(path + 'visualizaciones/swh_bhp_calc/resultados/balance_anual.csv')
    # balance_year['enerHeater'] = (balance_year.enerProc-balance_year.enerSol)/(effHeater/100)
    balance_year['Años'] = years_list
    # balance_year.loc['Total TWh/año'] = balance_year.sum(numeric_only=True, axis = 0)*10**(-6)
    # balance_year.iloc[21:22,4:5] = "TWh/año"
    source_bal_year.data = balance_year
    
    ener_year, x_year = SystemYear(df,tilt,azim,Col,aCol,vol,sto_loss,effHeater,year)
    new_data_year=dict(x=x_year, ener=ener_year)
    source_ener_year.data = new_data_year
    # df = CallSWH(df,tilt,azim,Col,aCol,vol,sto_loss,year)
    
    enerProc,  enerCald, enerHPump, enerPeak, enerSto = BalanceMonth(df,tilt,azim,Col,aCol,vol,sto_loss,potHeater,effHeater,potHPump,effHPump,year)
    balance_month = pd.read_csv(path + 'visualizaciones/swh_bhp_calc/resultados/balances_mensuales_año/balance_mensual_'+ str(year)+'.csv')
    # balance_month['enerHeater'] = (balance_month.enerProc-balance_month.enerSol)/(effHeater/100)
    # balance_month['Meses'] = meses
    balance_month.loc['Total TW/año'] = balance_month.sum(numeric_only=True, axis = 0)*10**(-6)
    # balance_year.iloc[21:22,4:5] = "TWh/año"
    source_bal_month.data = balance_month
    
    ener_month, x_month = SystemMonth(df,tilt,azim,Col,aCol,vol,sto_loss,effHeater,year)
    new_data_month=dict(x=x_month, ener=ener_month)
    source_ener_month.data = new_data_month
    
    table_ener = TableEner(df, Tin_p, Tout_p,potHeater,effHeater,potHPump,effHPump,Col,year)
    infoEner.text = str(table_ener)
    
    table_fuel = TableFuel(df,fuel,tilt,azim,Col,aCol,vol,sto_loss,effHeater,year)
    infoFuel.text = str(table_fuel)
    
    # table_steam = TableSteam(df,turno,flow_p, Tin_p, Tout_p,effHeater,cond,T_cond,p_steam,fuel)
    # infoSteam.text = str(table_steam)
        
#    fs_mes = enerSol/enerProc*100
#    new_data=dict(x=meses,y=fs_mes)
#    source_fs.data = new_data
    
    # new_data=dict(x=df.index,y=df.demanda)
#    source_dem.data = new_data

    #############################
def CalcEcon():
    '''
    

    Returns
    -------
    None.

    '''
    #####
    costCol_m2 =    float(CCol.value)
    cost_instCol_m2 =    float(CCol_inst.value)
    # costBOP=    float(CBOP.value)
    cost_instBOP=    float(C_instBOP.value)
    costSto=       float(CSto.value)
    cost_instSto=float(Cinst_Sto.value)
    costCald=    float(CCald.value)
    cost_instCald=    float(C_instCald.value)
    costPiping=    float(CPiping.value)
    cost_instPiping=    float(C_instPiping.value)
    costHEX=    float(CHEX.value)
    cost_instHEX=    float(C_instHEX.value)
    cost_prepTerr =  float(C_prepTerr.value)
    CostIng =    float(CIng.value)
    CostDev =    float(CDev.value)
    FIT_m2 =     float(fitm2.value)
    # perc_fee =float(percFee.value)
    
    
    # percOpex =float(POPEX.value)
    indSol =float(indexSolar.value)
    costFuel = float(CFuel.value)
    indFuel = float(indexFuel.value)
    anho_contr = int(anhoContr.value)
    # anho_contr = 20
    anho_proy = int(anhoProy.value)
    anho_depr = int(anhoDepr.value)
    perc_deuda = float(percDeuda.value)
    tasa_deuda = float(tasaDeuda.value)
    pago_deuda = int(pagoDeuda.value)
    tasa_equi = float(tasaEqui.value)
    infl_cl = float(inflChile.value)
    effHeater = float(eff_heater.value)
    potHeater= float(pot_heater.value)
    effHPump = float(eff_hpump.value)
    potHPump = float(pot_hpump.value)    
    aCol = float(areaCol.value)
    Ecost = float(CostE.value)
    
    vol_agua = float(VolAgua.value)
    agua_cost = float(CostAg.value)
    Workers = float(Wkers.value)
    CostW = float(WCost.value)
    perc_SST = float(PercSST.value)
    perc_Cald = float(PercCald.value)
    perc_Almac = float(PercAlmac.value)
    perc_PipHEX = float(PercPipHEX.value)
    

    
    #####
    

    fuel = dropdownFuel.value

    
#    pry = dropdownProy.value

    
    balance = pd.read_csv(path + 'visualizaciones/swh_bhp_calc/resultados/balances_mensuales_año/balance_mensual_'+str(year)+'.csv')
    # balance['enerHeater'] = (balance.enerProc-balance.enerSol)/(effHeater/100)
    # balance['enerCald'] = 
    balance['Meses'] = meses
    enerCol = balance.enerSol.sum()
    solFrac = enerCol / balance.enerProc.sum() * 100
#    enerCol = sum(prys[pry]['enerSol'])
#    solFrac = sum(prys[pry]['enerSol'])/sum(prys[pry]['enerProc']) *100
    
    FIT = FIT_m2 * aCol
    # CPX = areaCol * costCol_m2 
    
    
    
    #Costos independientes capex equipos capex
    CEQ_1 = (aCol * costCol_m2)
    # CEQ_2 = (aCol * costBOP)
    CEQ_3 = costSto
    CEQ_4 = costCald
    CEQ_5 = (costPiping * Lpipe)
    CEQ_6 =(costHEX * nHEX)
    
    #CAPEX PIPHEX
    COST_PIPHEX = CEQ_5+CEQ_6

    
    # CAPEX de equipos
    CAPEX_eq = CEQ_1  + CEQ_3 + CEQ_4 + CEQ_5 + CEQ_6 #+ CEQ_2
     
    #Costos independientes instalación capex
    CIN_1 = (aCol * cost_instCol_m2)
    CIN_2 = cost_instBOP
    CIN_3 = cost_instSto
    CIN_4 = cost_instCald
    CIN_5 = (Lpipe * cost_instPiping)
    CIN_6 = (nHEX * cost_instHEX)
    CIN_7 = (aCol * cost_prepTerr)
    
    # CAPEX_SST = CEQ_1 #+ CIN_1
    # CAPEX_Cald = CEQ_4 #+ CIN_4
    # CAPEX_Almac = CEQ_3 #+ CIN_3
    # CAPEX_PipHEX = CEQ_5 + CEQ_6 #+ CIN_5 +CIN_6
    
    
    # CAPEX instalación
    CAPEX_inst =  CIN_1 + CIN_2 + CIN_3 + CIN_4 + CIN_5 + CIN_6 + CIN_7

    #Costos independientes 
    CDE_1 = CostIng
    CDE_2 = CostDev
    
    # CAPEX desarrollo (US$)
    CAPEX_dev = CDE_1 + CDE_2
    
    table_capexu = TableCapexU(CEQ_1, CEQ_2, CEQ_3, CEQ_4, CEQ_5, CEQ_6,
                    CIN_1, CIN_2, CIN_3, CIN_4, CIN_5, CIN_6, CIN_7,
                    CDE_1, CDE_2,FIT)
    infoCapexu.text = str(table_capexu)
    

    # Contingencias (% CAPEX)
    Cont = 10
    Cont_tot = (CAPEX_eq + CAPEX_inst + CAPEX_dev) * Cont/100

    # Utilidades (% CAPEX)
    Util = 10
    Util_tot = (CAPEX_eq + CAPEX_inst + CAPEX_dev) * Util/100

    CAPEX = CAPEX_eq + CAPEX_inst + CAPEX_dev + Cont_tot + Util_tot + FIT
    
    EnerYear_op = balance.enerHeater.sum()
    
    # OPEX = Ecost*EnerYear_op
    
    COST_PIPHEX = CEQ_5+CEQ_6
    
    table_opex = TableOpexY(Ecost,EnerYear_op,vol_agua,agua_cost,Workers,CostW,CEQ_1,CEQ_4,CEQ_2,
                   COST_PIPHEX,perc_SST,perc_Cald,perc_Almac,perc_PipHEX)
    
    
    
    infoOpex.text = str(table_opex)
    
    table_res_anho = TableRes(anho_contr,anho_proy)
    
    infoResAnho.text = str(table_res_anho)

  
    # OPEX = CAPEX * percOpex/100
    
    
    
    SCAPEX_eq = pd.Series([CAPEX_eq])
    SCAPEX_inst = pd.Series([CAPEX_inst])
    SCAPEX_dev = pd.Series([CAPEX_dev])
    SCAPEX = pd.Series([CAPEX])
    
    new_data_capex = dict(capex_eq = SCAPEX_eq, capex_inst = SCAPEX_inst,
                                              capex_dev = SCAPEX_dev, capex_tot = SCAPEX)
    
    source_capex.data = new_data_capex
      
    infl_usa = 2
    val_depr = CAPEX/anho_depr
    dif_infl = (1+infl_usa/100) / (1+infl_cl/100) 
    
    table_eval,annual_res, annual_proy = LCOH_calc_upt(CAPEX,OPEX,tasa_deuda, pago_deuda,perc_deuda,impuesto,tasa_equi,dif_infl,infl_cl,
                                      anho_contr,anho_proy,val_depr,anho_depr,enerCol,indSol,indFuel,costFuel)


    annual_res.costSol[0] = np.nan
    an=pd.date_range('2021-01',freq='A',periods=len(annual_res))
    annual_res.index = an
    
    new_data=dict(x1=annual_res.index.year,ingEner=annual_res.ing_ener,
                                          opex=annual_res.opex,utils=annual_res.utilidades,
                                          perd=annual_res.perdidas,base_imp=annual_res.base_imp,
                                          imp_pc=annual_res.imp_PC,util_imp=annual_res.util_imp,
                                          fljNeto=annual_res.flujo_neto,fljAcum=annual_res.flujo_acum,
                                          van_vect=annual_res.vect_VAN)
    source_flujo.data = new_data
    infoEval.text = str(table_eval)
    
    table_fuel = TableFuel_LCOH(fuel,costFuel,effHeater,enerCol,solFrac)
    infoFuel.text = str(table_fuel)


    
    lcoh_f = float(table_fuel[2])
    
    cfuel = Vector(lcoh_f,anho_proy,indFuel)
    an=pd.date_range('2021-01',freq='A',periods=len(cfuel))
    cfuel = pd.DataFrame(cfuel,index=an)
    cfuel = cfuel.rename(columns={0:'costFuel'})
    cfuel = cfuel.rename_axis(None, axis=1).rename_axis('date', axis=0)
    
    csol=annual_res.costSol
    ener_cst = pd.concat([cfuel,csol], axis=1)
    
    source_cost.data = ener_cst
    
    lcoh = float(table_eval['LCOH (US$/MWh)'])
    
    cProy,table_proy = TableProy(lcoh,solFrac,enerCol,indSol,fuel,costFuel,indFuel,effHeater,anho_contr,anho_proy)
    an=pd.date_range('2021-01',freq='A',periods=len(cProy))
    cProy.index = an
    new_data=dict(x1=cProy.index,CSol=cProy.csol,CFuel=cProy.cfuel,CFoss=cProy.cfoss,CSST=cProy.SST)
    source_proy.data = new_data
    # infoProy.text = str(table_proy)
    
    return lcoh

# def CreateWalk():
#     df = pd.DataFrame()
    
#     effHeater = float(eff_heater.value)
#     indice = ind.value
#     factInd = float(fctInd.value)
#     anho_contr = int(anhoContr.value)
#     anho_proy = int(anhoProy.value)
#     indSol = float(indexSolar.value)
    
#     if indice == 'Mont Belvieu':
#         df = mont
#     elif indice == 'Brent':
#         df = brent
#     elif indice == 'WTI':
#         df = wti
#     elif indice == 'Henry Hub':
#         df = hhub
#     elif indice == 'GLP ENAP':
#         df = enp_glp
#     elif indice == 'DSL ENAP':
#         df = enp_dsl
    
#     rnd_walk = RandomWalk(df,indice,30)
#     rnd_walk = EnerConvProy(rnd_walk,indice,'Semanal','proy')
#     source_rnd.data=rnd_walk

#     lcoh = CalcEcon()
    
#     df_month, table_proy2 = ProyMonth(rnd_walk,'gen',indice,lcoh,indSol,anho_contr,anho_proy,effHeater,factInd,inicSolar = 2022)
#     sourceMonth.data = df_month
#     infoProy2.text = str(table_proy2)

# def RunMC():
    
#     lcoh = CalcEcon()
    
#     N_iter = int(n_esc.value)
#     effHeater = float(eff_heater.value)
    
#     df = pd.DataFrame()
#     indice = ind.value
#     factInd = float(fctInd.value)
#     anho_contr = int(anhoContr.value)
#     anho_proy = int(anhoProy.value)
#     indSol = float(indexSolar.value)
    
#     if indice == 'Mont Belvieu':
#         df = mont
#     elif indice == 'Brent':
#         df = brent
#     elif indice == 'WTI':
#         df = wti
#     elif indice == 'Henry Hub':
#         df = hhub
#     elif indice == 'GLP ENAP':
#         df = enp_glp
#     elif indice == 'DSL ENAP':
#         df = enp_dsl
    
#     ahr1 = MonteCarloParallel(df,0,indice,lcoh,indSol,anho_contr,anho_proy,effHeater,factInd,N_iter = N_iter, inicSolar = 2022)
#     ahr = np.array(ahr1)
#     hist, edges = np.histogram(ahr, density=True, bins=50)
#     hist_df = pd.DataFrame({'column': hist,
#                             "left": edges[:-1],
#                             "right": edges[1:]})
#     hist_df["interval"] = ["%d to %d" % (left, right) for left, 
#                             right in zip(hist_df["left"], hist_df["right"])]
    
#     src_hist.data = hist_df
#     p6.title.text = 'Histograma, ' + str(N_iter) + ' escenarios, indicador ' + indice
    
#     x_data, y_data = cdf(ahr1)
#     new_data=dict(x=x_data,y=y_data)
#     src_cdf.data  = new_data




buttCalcRad.on_click(CalcRad)
buttCalcEnergyYear.on_click(CalcSystemYear)
# buttCalcEnergyMonth.on_click(CalcSystemMonth)
buttCalcEcon.on_click(CalcEcon)
years_button_group.on_click(CalcSystemMonth)


#############
spc = 50
layout = column(Spacer(height=spc),
                row(dropdownData,dropdownSolData),
                row(incl,orie),
                buttCalcRad,
                row(p_rad,infoRad),
                
                
                row(Tin_proc,Tout_proc,dropdownFuel),#,flow_proc,selectTurno),
                row(pot_heater,eff_heater),
                row(pot_hpump,eff_hpump),#,dropdownFluid
                # row(presion_vapor,perc_cond),
                row(selectCol,areaCol,vol_sto,loss_sto),
                buttCalcEnergyYear,
                row(p_year,Spacer(width=spc),table_bal_year),
                row(infoEner,infoFuel),#infoSteam),
              
                
                Spacer(height=spc+30),
                row(years_button_group),
                # buttCalcEnergyMonth,
                row(p_month,Spacer(width=spc),table_bal_month),
              
                Spacer(height=spc),
                
                
                row(CCol, CCol_inst, C_instBOP),
                row(CCald, C_instCald, CSto, Cinst_Sto), #CBOP,
                row(CPiping, C_instPiping, CHEX, C_instHEX),
                row(C_prepTerr, CIng, CDev,fitm2),
                row (buttCalcEcon),
                row(infoCapexu),
                Spacer(height=spc),
                
        
                
                row(VolAgua,CostAg,Wkers,WCost),
                row(PercSST, PercCald, PercAlmac,Spacer(width=spc), PercPipHEX),
                row (buttCalcEcon),
                row(infoOpex),
                

                Spacer(height=spc+30),
                row(indexSolar,CFuel),#,POPEX
                row(indexFuel,CostE),
                Spacer(height = spc),
                row(infoResAnho),
                row(anhoDepr,percDeuda),
                row(tasaDeuda,pagoDeuda,tasaEqui,inflChile),
                row (buttCalcEcon),

                Spacer(height=spc+30),
                row(data_table,infoEval),  
                

                # row(p1,p2,infoProy),
                
                # Spacer(height=spc),
                # row(buttCalcWalk,ind,fctInd),
                # p3,
                # row(p4,p5,infoProy2),
                
                
                # Spacer(height=spc),
                # row(buttCalcMC,n_esc),
                # row(p6,p7) 
                )
                
############################################
curdoc().add_root(layout)