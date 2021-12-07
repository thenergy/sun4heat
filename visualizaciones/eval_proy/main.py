#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 15:33:06 2019

@author: fcuevas
"""
import sys
sys.path
#sys.path.append('/home/ubuntu/sun4heat/scripts')
#sys.path.append('/Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/scripts')
sys.path.append('/home/ubuntu/Thenergy/diego/sun4heat/scripts')

import numpy as np
import pandas as pd

from funciones_econ import Vector, LCOH_calc
from funciones import TableFuel_LCOH, TableProy

from bokeh.plotting import Figure
from bokeh.layouts import column, Spacer, row
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, DatetimeTickFormatter, DataTable, TableColumn, NumberFormatter, Range1d
from bokeh.io import curdoc
from bokeh.models.widgets import Select, TextInput, Button, PreText

from bokeh.tile_providers import get_provider, CARTODBPOSITRON, CARTODBPOSITRON_RETINA, STAMEN_TERRAIN,\
STAMEN_TERRAIN_RETINA, STAMEN_TONER, STAMEN_TONER_BACKGROUND,\
STAMEN_TONER_LABELS, OSM, WIKIMEDIA, ESRI_IMAGERY

####################################################################
def cdf(data):
    n = len(data)
    x = np.sort(data) # sort your data
    y = np.arange(1, n + 1) / n # calculate cumulative probability
    return x, y
####################################################################
def wgs84_to_web_mercator(df, lon="Longitud", lat="Latitud"):

      k = 6378137
      df["x"] = df[lon] * (k * np.pi/180.0)
      df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k

      return df
####################################################################
meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select,save"
####################################################################
prys = {'Agro_SVTT_esc1'    :{'enerProc':[2539,2258,2539,2340,2558,2439,2440,2559,2341,2539,2459,2420],
                              'enerSol' :[2474,2180,1907,1139,674,393,522,825,1209,1831,2052,2311],
                              'areaCol': 12020,'Sto':3000,'Pow':10,'CAPEX':4440,
                              'OM':50900,'Elect':350,'Precio':29.45,'indPrec':2,                              
                              'Lat':-34.428233 ,'Long':-71.082992,'Rad':1860},
    
        'Agro_SVTT_esc2'    :{'enerProc':[2871,2550,2865,2646,2891,2751,2759,2891,2640,2871,2777,2733],
                              'enerSol' :[2727,2442,2131,1260,729,417,569,893,1340,2051,2303,2597],
                              'areaCol': 13822,'Sto':3500,'Pow':10,'CAPEX':5440,
                              'OM':57000,'Elect':389,'Precio':34.1,'indPrec':2,                              
                              'Lat':-34.428233 ,'Long':-71.082992,'Rad':1860},
                              
        'SQM_CS_suministro' :{'enerProc':[9314,8383,9314,9005,10317,9937,10317,10317,9972,9314,9004,9314],
                              'enerSol' :[7322,6545,7045,5532,4528,3562,3928,5100,6285,7481,7614,8133],
                              'areaCol': 43269,'Sto':10000,'Pow':36, 'CAPEX':20520,
                              'OM':np.nan,'Elect':np.nan,'Precio':35,'indPrec':2,
                              'Lat':-22.386882,'Long':-69.629873,'Rad':2551},
                              
        'SQM_CS_proceso'    :{'enerProc':[9314,8383,9314,9005,10317,9937,10317,10317,9972,9314,9004,9314],
                              'enerSol' :[8670,7692,8242,6689,5952,4858,5325,6505,7644,8616,8726,9113],
                              'areaCol': 43269,'Sto':7000,'Pow':36, 'CAPEX':18400,
                              'OM':np.nan,'Elect':np.nan,'Precio':27,'indPrec':2,
                              'Lat':-22.386882,'Long':-69.629873,'Rad':2551},
                              
                              
        'RefChq_pinch4'     :{'enerProc':[6355,5740,6355,6150,6355,6150,6355,6355,6150,6355,6150,6355],
                              'enerSol' :[5096,4282,4433,3459,2572,1974,2408,3219,4027,4969,5251,5342],
                              'areaCol': 30048,'Sto':7000,'Pow':36, 'CAPEX':11074,
                              'OM':np.nan,'Elect':np.nan,'Precio':40,'indPrec':2,
                              'Lat':-22.308875,'Long':-68.915290,'Rad':2590},
                              
        'RefChq_pinch10'     :{'enerProc':[6355,5740,6355,6150,6355,6150,6355,6355,6150,6355,6150,6355],
                              'enerSol' :[4855,4055,4125,3303,2345,1789,2251,3028,3753,4801,5071,5129],
                              'areaCol': 30048,'Sto':7000,'Pow':36, 'CAPEX':11056,
                              'OM':np.nan,'Elect':np.nan,'Precio':40,'indPrec':2,
                              'Lat':-22.308875,'Long':-68.915290,'Rad':2590},
                              
                              
        'Mina_Zdr'          :{'enerProc':[2831,2557,2831,2739,2831,2739,2831,2831,2739,2831,2739,2831],
                              'enerSol' :[2642,2294,2455,2134,1576,1345,1621,1957,2460,2770,2739,2831],
                              'areaCol': 16857,'Sto':4000,'Pow':13.7,'CAPEX':7200,
                              'OM':65000,'Elect':500,'Precio':40,'indPrec':0.75,
                              'Lat':-24.231945,'Long':-69.132952,'Rad':2341},
                              
        'CCU_esc1'          :{'enerProc':[877,780,877,812,877,844,844,877,812,877,844,844],
                              'enerSol' :[839,727,614,365,228,140,207,274,397,596,735,770],
                              'areaCol': 4214,'Sto':1000,'Pow':3.42,'CAPEX':2001,
                              'OM':26260,'Elect':117.8,'Precio':41.51,'indPrec':2,
                              'Lat':-33.3555,'Long':-70.7063,'Rad':1746},
                              
        'CCU_esc2'          :{'enerProc':[877,780,877,812,877,844,844,877,812,877,844,844],
                              'enerSol' :[877,780,862,495,302,187,263,354,519,762,844,844],
                              'areaCol': 5286,'Sto':3000,'Pow':4.28,'CAPEX':2534,
                              'OM':32150,'Elect':141.8,'Precio':43.3,'indPrec':2,
                              'Lat':-33.3555,'Long':-70.7063,'Rad':1746}}
####################################################################

df_proys = pd.DataFrame.from_dict(prys,orient='index')
df_proys = df_proys.rename_axis('Proy')
ener = [sum(df_proys.enerProc[n]) for n in np.arange(len(df_proys))]

df_proys['CapEsp'] = df_proys.CAPEX * 1000 / df_proys.areaCol 
df_proys['SolEner'] = ener
df_proys['EnerEsp'] = df_proys.SolEner * 1000/ df_proys.areaCol
df_proys['CapEner'] = df_proys.CAPEX * 1000 / df_proys.SolEner
####################################################################
####################################################################
sourcePrys = ColumnDataSource(data=df_proys)

columnsProyectos = [
    TableColumn(field='Proy', title="Proyecto",width=100),
    TableColumn(field="areaCol", title="Área (m2)", formatter=NumberFormatter(format="0")),
    TableColumn(field="Pow", title="Potencia (MW)", formatter=NumberFormatter(format="0.0")),
    TableColumn(field="Sto", title="Almacenamiento (m3)", formatter=NumberFormatter(format="0.0")),
    TableColumn(field="Rad", title="Radiación ref (kWh/m2/año)", formatter=NumberFormatter(format="0")),
    TableColumn(field="CAPEX", title="CAPEX (kUS$)", formatter=NumberFormatter(format="0.0")),
    TableColumn(field="OM", title="OPEX (US$)", formatter=NumberFormatter(format="0.0")),
    TableColumn(field="SolEner", title="Energía anual (MWh)", formatter=NumberFormatter(format="0.0")),
    TableColumn(field="CapEsp", title="Inversión por área (US$/m2)", formatter=NumberFormatter(format="0.0")),
    TableColumn(field="EnerEsp", title="Energía por área (kWh/m2)", formatter=NumberFormatter(format="0.0")),
    TableColumn(field="CapEner", title="Inversión específi a (US$/MWh)", formatter=NumberFormatter(format="0.0")),
]

data_tableProy = DataTable(columns=columnsProyectos, source=sourcePrys,width=900, height=450)
####################################################################
####################################################################
# Convertir coordenadas a Mercator
wgs84_to_web_mercator(df_proys, lon="Long", lat="Lat")

# Obtener coordenadas del proyecto
lat = df_proys.y
lon = df_proys.x

# Definir el rango en el que se ve el mapa
offSet = 1000
ymin = lat.iloc[0] - offSet
ymax = lat.iloc[0] + offSet
yrng = Range1d()
yrng.start = ymin
yrng.end=ymax

xmin = lon.iloc[0] - offSet
xmax = lon.iloc[0] + offSet
xrng = Range1d()
xrng.start = xmin
xrng.end=xmax

# Definir el proveedor del tile (tipo de mapa en el cual proyectar)
tile_provider = get_provider(ESRI_IMAGERY)
p = Figure(plot_width=600, plot_height=450,tools=["pan,wheel_zoom,box_zoom,reset,save"],
           x_axis_type="mercator", y_axis_type="mercator",
           x_range=xrng,y_range=yrng)
p.add_tile(tile_provider)

source = ColumnDataSource(
    data=dict(lat=lat,
              lon=lon))

p.circle(x="lon", y="lat", size=10, fill_color="blue", fill_alpha=0.8, source=source)
####################################################################
####################################################################
# Proyecto
pry = 'Agro_SVTT_esc1'

#Area de colector (m2)
areaCol = prys[pry]['areaCol']

# Energía del sistema solar (MWh/año)
enerCol = sum(prys[pry]['enerSol'])

# Fracción solar
solFrac = sum(prys[pry]['enerSol'])/sum(prys[pry]['enerProc']) *100

# Indexaciçon del precio solar
indSol = 2

# Eficiencia de la caldera
effHeater = 85

# Combustible fósil a utilizar
fuel = 'GLP (kg)'

# Costo del combustible
costFuel = 0.32

# Indexación del combustible
indFuel = 2.4

# costo colector (US$/m2)
costCol_m2 = (prys[pry]['CAPEX']*1000)/prys[pry]['areaCol']

#
FIT_m2 = 0
FIT = FIT_m2 * areaCol

CPX = areaCol * costCol_m2 

perc_fee = 0
fee = (CPX+FIT)*perc_fee/100
CAPEX = CPX+ FIT + fee 

percOpex = 1.5

OPEX = CPX * percOpex/100

table_fuel = TableFuel_LCOH(fuel,costFuel,effHeater,enerCol,solFrac)
####################################################################
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

####################################################################
# inputs para función LCOH_calc, definida en funciones_econ.
# La función entrega 3 resultados
# table_eval: Valores resumen para tabla, LCOH, CAPEX, OPEX, VAN, TIR, Payback
# annual_res: Valores por año de la evaluación económica
# annual_proy: 
table_eval,annual_res, annual_proy = LCOH_calc(CAPEX,OPEX,tasa_deuda, pago_deuda,perc_deuda,impuesto,tasa_equi,dif_infl,infl_cl,
                                  anho_contr,anho_proy,val_depr,anho_depr,enerCol,indSol,indFuel,costFuel)
####################################################################
# Crear arreglos con valores del precio solar y precio del combustible por año
annual_res.costSol[0] = np.nan
an=pd.date_range('2021-01',freq='A',periods=len(annual_res))
annual_res.index = an

# Obtener valor del combustible desde la tabla de resultados table_fuel. LLenar vector con valor indexado
lcoh_f = float(table_fuel[2])
cfuel = Vector(lcoh_f,anho_proy,indFuel)
an=pd.date_range('2021-01',freq='A',periods=len(cfuel))
cfuel = pd.DataFrame(cfuel,index=an)
cfuel = cfuel.rename(columns={0:'costFuel'})
cfuel = cfuel.rename_axis(None, axis=1).rename_axis('date', axis=0)

csol=annual_res.costSol
cst = pd.concat([cfuel,csol], axis=1)
source_cost = ColumnDataSource(data=cst)
####################################################################
####################################################################
# Crear tabla con valores anuales de la evaluación económica
lcoh = float(table_eval['LCOH (US$/MWh)'])
source_flujo = ColumnDataSource(data=dict(x1=annual_res.index.year,ingEner=annual_res.ing_ener,
                                          opex=annual_res.opex,utils=annual_res.utilidades,
                                          perd=annual_res.perdidas,base_imp=annual_res.base_imp,
                                          imp_pc=annual_res.imp_PC,util_imp=annual_res.util_imp,
                                          fljNeto=annual_res.flujo_neto,fljAcum=annual_res.flujo_acum,
                                          van_vect=annual_res.vect_VAN))

columns = [
    TableColumn(field="x1", title="Año",width=25),
    TableColumn(field="ingEner", title="Ingreso Energía (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="opex", title="OPEX (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="utils", title="Utilidades (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="base_imp", title="Base impuesto (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="util_imp", title="Utilidades despues impuesto (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="fljNeto", title="Flujo neto (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="fljAcum", title="Flujo acumulado (kUS$)", formatter=NumberFormatter(format="0.00")),
]

data_table = DataTable(columns=columns, source=source_flujo,width=700, height=480)
####################################################################
cProy,table_proy = TableProy(lcoh,solFrac,enerCol,indSol,fuel,costFuel,indFuel,effHeater,anho_contr,anho_proy)
anhoProyect = np.arange(0,anho_proy+1,1)
an=pd.date_range('2021-01',freq='A',periods=len(cProy))
cProy.index = an
source_proy = ColumnDataSource(data=dict(x1=cProy.index,CSol=cProy.csol,CFuel=cProy.cfuel,CFoss=cProy.cfoss,CSST=cProy.SST))
#################################
wdt = 250
# Widget del proyecto a evaluar
dropdownProy = Select(value=pry,title='Proyecto',options=list(prys.keys()),width=wdt)

# Widgets de la evaluación económica
fitm2 = TextInput(value=str(FIT_m2), title="Envío, seguro e impuesto (US$/m2)",width=wdt)
percFee = TextInput(value=str(perc_fee), title="Fee desarrollador (% CAPEX)",width=wdt)
POPEX = TextInput(value=str(percOpex), title="OPEX (% CAPEX):",width=wdt)
indexSolar = TextInput(value=str(indSol), title="Indexación solar (%)",width=wdt)

# widgets de campos relacionados al combustible
eff_heater= TextInput(value=str(effHeater), title="Eficiencia caldera (%):",width=wdt)
fuels = ['Diesel (lt)','GNL (m3)','GLP (kg)']
dropdownFuel = Select(value=fuel,title='Combustible',options=fuels,width=wdt)
CFuel = TextInput(value=str(costFuel), title="Precio combustible (US$/unidad):",width=wdt)
indexFuel = TextInput(value=str(indFuel), title="Indexación combustible (%)",width=wdt)
#################################
# Evaluación económica
anhoContr = TextInput(value=str(anho_contr), title="Años de contrato ESCO",width=wdt)
anhoProy = TextInput(value=str(anho_proy), title="Años evaluación escenario",width=wdt)
anhoDepr = TextInput(value=str(anho_depr), title="Años depreciación",width=wdt)
percDeuda = TextInput(value=str(perc_deuda), title="Porcentaje deuda",width=wdt)
tasaDeuda = TextInput(value=str(tasa_deuda), title="Tasa deuda (%)",width=wdt)
pagoDeuda = TextInput(value=str(pago_deuda), title="Años pago deuda",width=wdt)
tasaEqui = TextInput(value=str(tasa_equi), title="Tasa capital propio (%)",width=wdt)
inflChile = TextInput(value=str(infl_cl), title="Inflación Chile (%)",width=wdt)
#####################
# Botón CALCULAR
# Actualiza todos los valores según los parámetros ingresados en cada campo
buttCalcEcon = Button(label="Calcular", button_type="success",width=wdt)
infoEval = PreText(text=str(table_eval), width=320)
infoFuel = PreText(text=str(table_fuel), width=320)
infoProy = PreText(text=str(table_proy), width=320)
################################################
plot_w = 700
plot_h = 360
###############################################
p1 = Figure(tools=TOOLS,title="Costo de energía", x_axis_label="Fecha", y_axis_label= "Costo (US$/MWh)", 
            plot_width=plot_w, plot_height=plot_h)

line1_p1 = p1.line(x='date',y='costFuel',source=source_cost,color='red',legend_label='Costo MWh combustible')
line2_p1 = p1.line(x='date',y='costSol',source=source_cost,color='green',legend_label='Costo MWh solar')

p1.xaxis.formatter=DatetimeTickFormatter(hours = ['%d/%m %H:00'],days = ['%F'])
p1.legend.click_policy="hide"
p1.add_tools(HoverTool(renderers=[line1_p1], tooltips=[('Fecha: ', '@date{%F}'),
     ('Costo combustible (US$/MWh): ', '@costFuel{0.0}'),
     ('Costo solar (US$/MWh): ', '@costSol{0.0}')],mode='vline',formatters={'@date':'datetime'}))
###############################################
p2 = Figure(tools=TOOLS,title="Costo proyectos", x_axis_label="Fecha", y_axis_label= "Pago (kUS$/año)", 
            plot_width=plot_w, plot_height=plot_h, x_range=p1.x_range)

line1_p2 = p2.line(x='x1',y='CFuel',source=source_proy,color='red',line_width=1.2, legend_label='Pago fósil con SST')
line2_p2 = p2.line(x='x1',y='CSol',source=source_proy,color='green',line_width=1.2,legend_label='Pago energía solar')
line3_p2 = p2.line(x='x1',y='CSST',source=source_proy,color='blue',line_width=2.4,legend_label='Pago total con SST')
line4_p2 = p2.line(x='x1',y='CFoss',source=source_proy,color='black',line_width=2.4,legend_label='Pago sin SST')

p2.xaxis.formatter=DatetimeTickFormatter(hours = ['%d/%m %H:00'],days = ['%F'])
p2.legend.click_policy="hide"
p2.add_tools(HoverTool(renderers=[line1_p2], tooltips=[('Fecha: ', '@x1{%F}'),
     ('Pago fósil con SST (kUS$): ', '@CFuel{0.0}'),
     ('Pago energía solar (kUS$): ', '@CSol{0.0}'),
     ('Pago total con SST (kUS$): ', '@CSST{0.0}'),
     ('Pago sin SST (kUS$): ', '@CFoss{0.0}')],mode='vline',formatters={'@x1':'datetime'}))
###############################################
###############################################

###############################################
###############################################
from funciones_econ import RandomWalk, EnerConvProy, ProyMonth, MonteCarlo, MonteCarloParallel

# https://www.engineeringtoolbox.com/energy-content-d_868.html
indicadores = {'Mont Belvieu'   : {'std_unit':'gal',    'PCI':91330,    'abrev':'mont'},
               'Brent'          : {'std_unit':'barrel', 'PCI':5800000,'abrev':'brent'},
               'WTI'            : {'std_unit':'barrel', 'PCI':5800000,  'abrev':'wti'},
               'Henry Hub'      : {'std_unit':'MMBtu', 'PCI':1e6,         'abrev':'hhub'},
               'GLP ENAP'       : {'std_unit':'ton',    'PCI':12956008,        'abrev':'glp'},
               'DSL ENAP'       : {'std_unit':'m3',     'PCI':35960000,        'abrev':'dsl'}}

# GLP   264.17*0.537*91330
#path = '/Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/datos/Combustibles'
path = '/home/ubuntu/Thenergy/diego/sun4heat/datos/Combustibles'

################################################
# Lista histórica de precios de combustibles, según la EIA

#https://www.eia.gov/dnav/pet/hist_xls/EER_EPLLPA_PF4_Y44MB_DPGd.xls
mont = pd.read_excel(path + '/EER_EPLLPA_PF4_Y44MB_DPGd.xls',sheet_name='Data 1',skiprows=2)
mont.set_index('Date',inplace=True)
mont = mont.rename(columns={'Mont Belvieu, TX Propane Spot Price FOB (Dollars per Gallon)':'std_unit'})

wti = pd.read_excel(path + '/RWTCd.xls',sheet_name='Data 1',skiprows=2)
wti.set_index('Date',inplace=True)
wti = wti.rename(columns={'Cushing, OK WTI Spot Price FOB (Dollars per Barrel)':'std_unit'})

brent = pd.read_excel(path + '/RBRTEd.xls',sheet_name='Data 1',skiprows=2)
brent.set_index('Date',inplace=True)
brent = brent.rename(columns={'Europe Brent Spot Price FOB (Dollars per Barrel)':'std_unit'})

hhub = pd.read_excel(path + '/RNGWHHDd.xls',sheet_name='Data 1',skiprows=2)
hhub.set_index('Date',inplace=True)
hhub = hhub.rename(columns={'Henry Hub Natural Gas Spot Price (Dollars per Million Btu)':'std_unit'})

# Lista histórica de precios de combustibles, según ENAP
enp_glp = pd.read_csv(path + '/glp_enap.csv',date_parser=['Date'])
enp_glp.set_index('Date',inplace=True)
enp_glp = enp_glp.rename(columns={'GLP_usd_ton':'std_unit'})
enp_glp.index = pd.to_datetime(enp_glp.index)

enp_dsl = pd.read_csv(path + '/dsl_enap.csv',date_parser=['Date'])
enp_dsl.set_index('Date',inplace=True)
enp_dsl = enp_dsl.rename(columns={'Diesel_m3':'std_unit'})
enp_dsl.index = pd.to_datetime(enp_dsl.index)
############
# Botón para correr el random walk del índice a analizar
indice = 'Mont Belvieu'
buttCalcWalk = Button(label="Random", button_type="success")
ind = Select(value=indice, title='Indicador', options=list(indicadores.keys()))

# Factor a sumar en caso de Chile
factInd = 0
fctInd = TextInput(value=str(factInd), title="Valor a agregar Chile (+)",width=wdt)
############
# Definir el índice a analizar
df = mont
# Llamar a función RandomWalk, definida en funciones_econ
# toma el df de los valores de EIA o ENAP, según el índicador definido y lo proyecta 30 años
rnd_walk = RandomWalk(df,indice,30)
# Conversión energética desde la unidad estandar a MWh y MMBtu
rnd_walk = EnerConvProy(rnd_walk,indice,'Semanal','proy')
source_rnd = ColumnDataSource(data=rnd_walk)
####################################################################
p3 = Figure(tools=TOOLS,title="", x_axis_label="Fecha", y_axis_label= "Precio (USD/unidad standar)", 
            plot_width=plot_w+450, plot_height=plot_h+100)
line1_p3 = p3.line('Date','std_unit',color='black',source=source_rnd, legend_label='Indice')
line2_p3 = p3.line('Date','proy',color='green',source=source_rnd, legend_label='Random walk proy')
p3.xaxis.formatter=DatetimeTickFormatter()

p3.add_tools(HoverTool(renderers=[line1_p3], tooltips=[('Fecha: ', '@Date{%F}'),
     ('Costo histórico (US$/unidad): ', '@std_unit{0.00}'),
     ('Costo histórico (US$/MMBtu): ', '@MMBtu{0.00}'),
     ('Costo histórico (US$/MWh): ', '@MWh{0.00}')],mode='vline',formatters={'@Date':'datetime'}))
p3.add_tools(HoverTool(renderers=[line2_p3], tooltips=[('Fecha: ', '@Date{%F}'),
     ('Costo proyectado (US$/unidad): ', '@proy{0.00}'),
     ('Costo proyectado (US$/MMBtu): ', '@MMBtu_proy{0.00}'),
     ('Costo proyectado (US$/MWh): ', '@MWh_proy{0.00}')],mode='vline',formatters={'@Date':'datetime'}))
#####################################################################

df_month, table_proy2 = ProyMonth(rnd_walk,pry,indice,lcoh,indSol,anho_contr,anho_proy,effHeater,factInd,inicSolar = 2022)

sourceMonth = ColumnDataSource(data=df_month)

###############################################
p4 = Figure(tools=TOOLS,title="Precio energía", x_axis_label="Fecha", y_axis_label= "Precio (USD/MWh)", 
            plot_width=plot_w, plot_height=plot_h)
line1_p4 = p4.line('Date','MWh_cl',color='black',source=sourceMonth, legend_label='Fósil')
line2_p4 = p4.line('Date','precioSol',color='green',source=sourceMonth, legend_label='Solar')
p4.xaxis.formatter=DatetimeTickFormatter()
p4.legend.click_policy="hide"
p4.add_tools(HoverTool(renderers=[line1_p4], tooltips=[('Fecha: ', '@Date{%F}'),
     ('Costo combustible (US$/MWh): ', '@MWh_cl{0.0}'),
     ('Costo solar (US$/MWh): ', '@precioSol{0.0}')],mode='vline',formatters={'@Date':'datetime'}))
###############################################
p5 = Figure(tools=TOOLS,title="Costo proyectos", x_axis_label="Fecha", y_axis_label= "Pago (kUS$/año)", 
            plot_width=plot_w, plot_height=plot_h)

line1_p5 = p5.line(x='Date',y='fossPay',source=sourceMonth,color='red',line_width=1.2, legend_label='Pago fósil con SST')
line2_p5 = p5.line(x='Date',y='solPay',source=sourceMonth,color='green',line_width=1.2,legend_label='Pago energía solar')
line3_p5 = p5.line(x='Date',y='totPay',source=sourceMonth,color='blue',line_width=2.4,legend_label='Pago total con SST')
line4_p5 = p5.line(x='Date',y='convPay',source=sourceMonth,color='black',line_width=2.4,legend_label='Pago sin SST')
p5.xaxis.formatter=DatetimeTickFormatter()
p5.legend.click_policy="hide"
p5.add_tools(HoverTool(renderers=[line1_p5], tooltips=[('Fecha: ', '@Date{%F}'),
     ('Pago fósil con SST (kUS$): ', '@fossPay{0.0}'),
     ('Pago energía solar (kUS$): ', '@solPay{0.0}'),
     ('Pago total con SST (kUS$): ', '@totPay{0.0}'),
     ('Pago sin SST (kUS$): ', '@convPay{0.0}')],mode='vline',formatters={'@Date':'datetime'}))
###############################################    

infoProy2 = PreText(text=str(table_proy2), width=320)

N_iter = 500

ahr1 = MonteCarloParallel(df,pry,indice,lcoh,indSol,anho_contr,anho_proy,effHeater,factInd,N_iter = N_iter, inicSolar = 2022)
ahr = np.array(ahr1)
hist, edges = np.histogram(ahr, density=True, bins=20)
hist_df = pd.DataFrame({'column': hist,
                        "left": edges[:-1],
                        "right": edges[1:]})
hist_df["interval"] = ["%d to %d" % (left, right) for left, 
                        right in zip(hist_df["left"], hist_df["right"])]

src_hist = ColumnDataSource(hist_df)

p6 = Figure(title='Histograma, ' + str(N_iter) + ' escenarios, Proyecto ' + pry + ', indicador ' + indice,
             tools=TOOLS,plot_width=plot_w, plot_height=plot_h+200) #, background_fill_color="#fafafa"
p6.quad(top='column', bottom=0, left='left', right='right',
           fill_color="navy", line_color="white", alpha=0.5, source=src_hist)


x_data, y_data = cdf(ahr1)
src_cdf = ColumnDataSource(data=dict(x=x_data,y=y_data))
p7 = Figure(tools=TOOLS,title = 'Histograma, ' + str(N_iter) + ' escenarios, Proyecto ' + pry + ', indicador ' + indice,
            plot_width=plot_w, plot_height=plot_h+200) #, background_fill_color="#fafafa"
p7.line('x','y',source=src_cdf)         
   

buttCalcMC = Button(label="Monte Carlo", button_type="success")
n_esc = TextInput(value=str(N_iter), title="Número de escenarios",width=wdt)


def CalcEcon():
    
    FIT_m2 = float(fitm2.value) 
    perc_fee = float(percFee.value)
    percOpex = float(POPEX.value)
    indSol = float(indexSolar.value)
    
    effHeater = float(eff_heater.value)
    fuel = dropdownFuel.value
    costFuel = float(CFuel.value)
    indFuel = float(indexFuel.value)
    
    pry = dropdownProy.value
    areaCol = prys[pry]['areaCol']
    enerCol = sum(prys[pry]['enerSol'])
    solFrac = sum(prys[pry]['enerSol'])/sum(prys[pry]['enerProc']) *100
    costCol_m2 = (prys[pry]['CAPEX']*1000)/prys[pry]['areaCol']
    
    FIT = FIT_m2 * areaCol
    CPX = areaCol * costCol_m2 
    
    fee = (CPX+FIT)*perc_fee/100
    CAPEX = CPX+ FIT + fee 
    
    OPEX = CPX * percOpex/100

    anho_contr = int(anhoContr.value)
    anho_proy = int(anhoProy.value)
    anho_depr = int(anhoDepr.value)
    pago_deuda = int(pagoDeuda.value)
     
    perc_deuda = float(percDeuda.value)
    tasa_deuda = float(tasaDeuda.value)
    tasa_equi = float(tasaEqui.value)
    infl_cl = float(inflChile.value)
    
    infl_usa = 2
    val_depr = CAPEX/anho_depr
    dif_infl = (1+infl_usa/100) / (1+infl_cl/100) 
    
    table_eval,annual_res, annual_proy = LCOH_calc(CAPEX,OPEX,tasa_deuda, pago_deuda,perc_deuda,impuesto,tasa_equi,dif_infl,infl_cl,
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
    cst = pd.concat([cfuel,csol], axis=1)
    
    source_cost.data = cst
    
    lcoh = float(table_eval['LCOH (US$/MWh)'])
    
    cProy,table_proy = TableProy(lcoh,solFrac,enerCol,indSol,fuel,costFuel,indFuel,effHeater,anho_contr,anho_proy)
    an=pd.date_range('2021-01',freq='A',periods=len(cProy))
    cProy.index = an
    new_data=dict(x1=cProy.index,CSol=cProy.csol,CFuel=cProy.cfuel,CFoss=cProy.cfoss,CSST=cProy.SST)
    source_proy.data = new_data
    infoProy.text = str(table_proy)
    
    return lcoh


def CreateWalk():
    df = pd.DataFrame()
    
    effHeater = float(eff_heater.value)
    indice = ind.value
    factInd = float(fctInd.value)
    anho_contr = int(anhoContr.value)
    anho_proy = int(anhoProy.value)
    indSol = float(indexSolar.value)
    
    if indice == 'Mont Belvieu':
        df = mont
    elif indice == 'Brent':
        df = brent
    elif indice == 'WTI':
        df = wti
    elif indice == 'Henry Hub':
        df = hhub
    elif indice == 'GLP ENAP':
        df = enp_glp
    elif indice == 'DSL ENAP':
        df = enp_dsl
    
    rnd_walk = RandomWalk(df,indice,30)
    rnd_walk = EnerConvProy(rnd_walk,indice,'Semanal','proy')
    source_rnd.data=rnd_walk

    lcoh = CalcEcon()
    
    df_month, table_proy2 = ProyMonth(rnd_walk,pry,indice,lcoh,indSol,anho_contr,anho_proy,effHeater,factInd,inicSolar = 2022)
    sourceMonth.data = df_month
    infoProy2.text = str(table_proy2)

def RunMC():
    lcoh = CalcEcon()
    
    pry = dropdownProy.value
    N_iter = int(n_esc.value)
    effHeater = float(eff_heater.value)
    
    df = pd.DataFrame()
    indice = ind.value
    factInd = float(fctInd.value)
    anho_contr = int(anhoContr.value)
    anho_proy = int(anhoProy.value)
    indSol = float(indexSolar.value)
    
    if indice == 'Mont Belvieu':
        df = mont
    elif indice == 'Brent':
        df = brent
    elif indice == 'WTI':
        df = wti
    elif indice == 'Henry Hub':
        df = hhub
    elif indice == 'GLP ENAP':
        df = enp_glp
    elif indice == 'DSL ENAP':
        df = enp_dsl
    
    ahr1 = MonteCarloParallel(df,pry,indice,lcoh,indSol,anho_contr,anho_proy,effHeater,factInd,N_iter = N_iter, inicSolar = 2022)
    ahr = np.array(ahr1)
    hist, edges = np.histogram(ahr, density=True, bins=50)
    hist_df = pd.DataFrame({'column': hist,
                            "left": edges[:-1],
                            "right": edges[1:]})
    hist_df["interval"] = ["%d to %d" % (left, right) for left, 
                            right in zip(hist_df["left"], hist_df["right"])]
    
    src_hist.data = hist_df
    p6.title.text = 'Histograma, ' + str(N_iter) + ' escenarios, Proyecto ' + pry + ', indicador ' + indice
    
    x_data, y_data = cdf(ahr1)
    new_data=dict(x=x_data,y=y_data)
    src_cdf.data  = new_data


###################
def function_source(attr, old, new):
    try:
        selected_index = sourcePrys.selected.indices[0]
        name_selected = sourcePrys.data['Proy'][selected_index]
        
        df_empr = df_proys[df_proys.Proy == name_selected]
        source.data = df_empr
        
        lat = df_empr.y
        lon = df_empr.x
        new_data=dict(lat=lat,lon=lon)
        source.data = new_data
        
        ymin = lat.iloc[0] - offSet
        ymax = lat.iloc[0] + offSet
        
        xmin = lon.iloc[0] - offSet
        xmax = lon.iloc[0] + offSet
        xrng.update(start=xmin, end=xmax)
        yrng.update(start=ymin, end=ymax)
        ##############
        
    except IndexError:
        pass
    
    
buttCalcEcon.on_click(CalcEcon)
buttCalcWalk.on_click(CreateWalk)
buttCalcMC.on_click(RunMC)
sourcePrys.selected.on_change('indices', function_source)
##############
spc = 50
layout = column(Spacer(height=spc),
                row(data_tableProy,p),
                row(dropdownProy),
                row(fitm2,percFee,POPEX,indexSolar),
                row(eff_heater,dropdownFuel,CFuel,indexFuel),

                 Spacer(height=spc),
                 row(anhoContr,anhoProy,anhoDepr,pagoDeuda),
                 row(percDeuda,tasaDeuda,tasaEqui,inflChile),
                 buttCalcEcon,
                 Spacer(height=spc),
                 row(data_table,infoEval,infoFuel),                 
                 row(p1,p2,infoProy),
                 
                 row(buttCalcWalk,ind,fctInd),
                 p3,
                 row(p4,p5,infoProy2),
                 
                 row(buttCalcMC,n_esc),
                 row(p6,p7)  )
############################################
curdoc().add_root(layout)