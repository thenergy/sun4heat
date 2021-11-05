#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 15:33:06 2019

@author: fcuevas
"""
import sys
sys.path
#sys.path.append('/home/ubuntu/sun4heat/scripts')
sys.path.append('/Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/scripts')

import numpy as np
import pandas as pd

from funciones_econ import  Pago, PagoPrinInt, Vector, Depr, Perdidas, BaseImpuesto, FlujoAcum,Van,Tir,Payback,TableCapex, TableOpex, TableEval, LCOH_calc
from funciones import TableFuel_LCOH, TableProy

from bokeh.plotting import Figure
from bokeh.layouts import column, Spacer, row
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, DatetimeTickFormatter, DataTable, TableColumn, NumberFormatter
from bokeh.io import curdoc
from bokeh.transform import factor_cmap
from bokeh.models.widgets import Select, TextInput, Button, PreText

import time

def cdf(data):
    n = len(data)
    x = np.sort(data) # sort your data
    y = np.arange(1, n + 1) / n # calculate cumulative probability
    return x, y

meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']


#ng = pd.read_excel('henry_hub.xlsx',sheet_name='Hoja1',skiprows=2,names=['date','price','perc'],index_col=0)

#Area de colector (m2)
areaCol = 12020

# Energía del sistema solar (MWh/año)
enerCol = 17516

# Fracción solar
solFrac = 60

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
costCol_m2 = 369.4

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
#################################################################################################   
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

table_eval,annual_res, annual_proy = LCOH_calc(CAPEX,OPEX,tasa_deuda, pago_deuda,perc_deuda,impuesto,tasa_equi,dif_infl,infl_cl,
                                  anho_contr,anho_proy,val_depr,anho_depr,enerCol,indSol,indFuel,costFuel)

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
cst = pd.concat([cfuel,csol], axis=1)


lcoh = float(table_eval['LCOH (US$/MWh)'])
source_flujo = ColumnDataSource(data=dict(x1=annual_res.index.year,ingEner=annual_res.ing_ener,
                                          opex=annual_res.opex,utils=annual_res.utilidades,
                                          perd=annual_res.perdidas,base_imp=annual_res.base_imp,
                                          imp_pc=annual_res.imp_PC,util_imp=annual_res.util_imp,
                                          fljNeto=annual_res.flujo_neto,fljAcum=annual_res.flujo_acum,
                                          van_vect=annual_res.vect_VAN))

source_cost = ColumnDataSource(data=cst)
    
columns = [
    TableColumn(field="x1", title="Año",width=25),
    TableColumn(field="ingEner", title="Ingreso Energía (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="opex", title="OPEX (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="utils", title="Utilidades (kUS$)", formatter=NumberFormatter(format="0.00")),
#    TableColumn(field="perd", title="Perdidas (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="base_imp", title="Base impuesto (kUS$)", formatter=NumberFormatter(format="0.00")),
#    TableColumn(field="imp_pc", title="Impuesto Primera cat (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="util_imp", title="Utilidades despues impuesto (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="fljNeto", title="Flujo neto (kUS$)", formatter=NumberFormatter(format="0.00")),
    TableColumn(field="fljAcum", title="Flujo acumulado (kUS$)", formatter=NumberFormatter(format="0.00")),
#    TableColumn(field="van_vect", title="Vector VAN (kUS$)", formatter=NumberFormatter(format="0.00"))
]

data_table = DataTable(columns=columns, source=source_flujo,width=700, height=480)
#################################
cProy,table_proy = TableProy(lcoh,solFrac,enerCol,indSol,fuel,costFuel,indFuel,effHeater,anho_contr,anho_proy)
anhoProyect = np.arange(0,anho_proy+1,1)
an=pd.date_range('2021-01',freq='A',periods=len(cProy))
cProy.index = an
source_proy = ColumnDataSource(data=dict(x1=cProy.index,CSol=cProy.csol,CFuel=cProy.cfuel,CFoss=cProy.cfoss,CSST=cProy.SST))


#################################
wdt = 250
ACol = TextInput(value=str(areaCol), title="Área colectores (m2):",width=wdt)
ECol = TextInput(value=str(enerCol), title="Energía SST (MWh/año):",width=wdt)
CCol = TextInput(value=str(costCol_m2), title="Costo SST (US$/m2):",width=wdt)
fitm2 = TextInput(value=str(FIT_m2), title="Envío, seguro e impuesto (US$/m2)",width=wdt)
percFee = TextInput(value=str(perc_fee), title="Fee desarrollador (% CAPEX)",width=wdt)
SFra = TextInput(value=str(solFrac), title="Fracción Solar (%):",width=wdt)
POPEX = TextInput(value=str(percOpex), title="OPEX (% CAPEX):",width=wdt)
indexSolar = TextInput(value=str(indSol), title="Indexación solar (%)",width=wdt)

mods = ['LCOH','Scenario1']
dropdownCalc = Select(value='LCOH',title='Modo cálculo',options=mods,width=wdt)

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
# CAPEX
costColm2= TextInput(value=str(costCol_m2), title="Costo colector (US$/m2)",width=wdt)

buttCalcEcon = Button(label="Calcular", button_type="success",width=wdt)
infoEval = PreText(text=str(table_eval), width=320)
infoFuel = PreText(text=str(table_fuel), width=320)
infoProy = PreText(text=str(table_proy), width=320)
################################################
TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select,save"
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
     ('Costo solar (US$/MWh): ', '@costSol{0.0}')],mode='vline',formatters={'date':'datetime'}))
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
     ('Pago sin SST (kUS$): ', '@CFoss{0.0}')],mode='vline',formatters={'x1':'datetime'}))
###############################################
###############################################

###############################################
###############################################
from funciones_econ import RandomWalk, EnerConv, EnerConvProy, VectorAnual

# https://www.engineeringtoolbox.com/energy-content-d_868.html
indicadores = {'Mont Belvieu'   : {'std_unit':'gal',    'PCI':91330,    'abrev':'mont'},
               'Brent'          : {'std_unit':'barrel', 'PCI':5800000,'abrev':'brent'},
               'WTI'            : {'std_unit':'barrel', 'PCI':5800000,  'abrev':'wti'},
               'Henry Hub'      : {'std_unit':'MMBtu', 'PCI':1e6,         'abrev':'hhub'}}

path = '/Users/fcuevas/Documents/Trabajo/thenergy/mapa_industrial/datos/Combustibles/indicadores'
################################################
# Lista histórica de precios de combustibles, según la EIA
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
############
indice = 'Mont Belvieu'
buttCalcWalk = Button(label="Random", button_type="success")
ind = Select(value=indice, title='Indicador', options=list(indicadores.keys()))

factInd = 0
fctInd = TextInput(value=str(factInd), title="Valor a agregar Chile (+)",width=wdt)
############
df = mont
rnd_walk = RandomWalk(df,indice,30)
rnd_walk = EnerConvProy(rnd_walk,indice,'Semanal','proy')
source_rnd = ColumnDataSource(data=rnd_walk)

p3 = Figure(tools=TOOLS,title="", x_axis_label="Fecha", y_axis_label= "Precio (USD/unidad standar)", 
            plot_width=plot_w+450, plot_height=plot_h+100)
line1_p3 = p3.line('Date','std_unit',color='black',source=source_rnd, legend_label='Indice')
line2_p3 = p3.line('Date','proy',color='green',source=source_rnd, legend_label='Random walk proy')
p3.xaxis.formatter=DatetimeTickFormatter()

p3.add_tools(HoverTool(renderers=[line1_p3], tooltips=[('Fecha: ', '@Date{%F}'),
     ('Costo histórico (US$/unidad): ', '@std_unit{0.00}'),
     ('Costo histórico (US$/MMBtu): ', '@MMBtu{0.00}'),
     ('Costo histórico (US$/MWh): ', '@MWh{0.00}')],mode='vline',formatters={'Date':'datetime'}))
p3.add_tools(HoverTool(renderers=[line2_p3], tooltips=[('Fecha: ', '@Date{%F}'),
     ('Costo proyectado (US$/unidad): ', '@proy{0.00}'),
     ('Costo proyectado (US$/MMBtu): ', '@MMBtu_proy{0.00}'),
     ('Costo histórico (US$/MWh): ', '@MWh_proy{0.00}')],mode='vline',formatters={'Date':'datetime'}))
#################################################################################################

def ProyMonth(df,indice,lcoh,anho_contr,anho_proy,effHeater,factInd,inicSolar = 2022):
    
    df_month = df.resample('M').mean()
    df_month = df_month[df_month.index.year > 2020]
    
    df_month['month'] = df_month.index.month
    df_month['year'] = df_month.index.year
    header = ['n','monthProc','monthSol']
    df_sol = pd.read_csv('balance.csv',sep=',',names=header,nrows=12,index_col='n')
    
    precSol = VectorAnual(lcoh,anho_contr,indSol,2021)
    
    enerProc = dict(df_sol.monthProc)
    enerSol = dict(df_sol.monthSol)
    prSol = dict(precSol)
    
    df_month['precioSol'] = df_month.year.map(prSol).fillna(0)
    
    df_month['enerProc'] = df_month.month.map(enerProc)
    df_month['enerSol'] = df_month.month.map(enerSol)
    
    finSolar = inicSolar + anho_contr
    finEval = inicSolar + anho_proy
    
    mask = (df_month.index.year < inicSolar) | (df_month.index.year > finSolar)
    col_name = 'enerSol'
    df_month.loc[mask,col_name] = 0
    df_month['enerHeater'] = df_month.enerProc/(effHeater/100)
    
    df_month['proy'] = df_month['proy'] + factInd
    df_month = EnerConvProy(df_month,indice,'Mensual','proy')
    
    df_month['MWh_cl'] = df_month.MWh_proy / (effHeater/100)
    
    df_month = df_month[(df_month.index.year > 2021) & (df_month.index.year < finSolar)]
    
    df_month['convPay'] = (df_month.MWh_cl * df_month.enerProc)/1e3
    df_month['solPay'] = (df_month.precioSol * df_month.enerSol)/1e3
    df_month['fossPay'] = (df_month.MWh_cl * (df_month.enerProc - df_month.enerSol))/1e3
    df_month['totPay'] = df_month.solPay + df_month.fossPay
    
#    df_month = df_month[df_month.index.year < finEval]
    
    table_proy2 = pd.Series()
    table_proy2['Pago sin SST (kUS$): '] = "{:10.1f}".format(df_month.convPay.sum())
    table_proy2['Pago con SST (kUS$): '] = "{:10.1f}".format(df_month.totPay.sum())
    table_proy2['Pago solar (kUS$): '] = "{:10.1f}".format(df_month.solPay.sum())
    table_proy2['Ahorro (kUS$): '] = "{:10.1f}".format(df_month.totPay.sum() - df_month.convPay.sum())
    
    return df_month, table_proy2


df_month, table_proy2 = ProyMonth(rnd_walk,indice,lcoh,anho_contr,anho_proy,effHeater,factInd,inicSolar = 2022)

sourceMonth = ColumnDataSource(data=df_month)

p4 = Figure(tools=TOOLS,title="Precio energía", x_axis_label="Fecha", y_axis_label= "Precio (USD/MWh)", 
            plot_width=plot_w, plot_height=plot_h)
line1_p4 = p4.line('Date','MWh_cl',color='black',source=sourceMonth, legend_label='Fósil')
line2_p4 = p4.line('Date','precioSol',color='green',source=sourceMonth, legend_label='Solar')
p4.xaxis.formatter=DatetimeTickFormatter()
p4.legend.click_policy="hide"
p4.add_tools(HoverTool(renderers=[line1_p4], tooltips=[('Fecha: ', '@Date{%F}'),
     ('Costo combustible (US$/MWh): ', '@MWh_cl{0.0}'),
     ('Costo solar (US$/MWh): ', '@precioSol{0.0}')],mode='vline',formatters={'Date':'datetime'}))
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
     ('Pago sin SST (kUS$): ', '@convPay{0.0}')],mode='vline',formatters={'Date':'datetime'}))
    

infoProy2 = PreText(text=str(table_proy2), width=320)

N_iter = 50

def MonteCarlo(df,indice,lcoh,anho_contr,anho_proy,effHeater,factInd,N_iter = 2, inicSolar = 2022):
    tot_periods = anho_contr*12
    rng = pd.date_range('2022',periods=tot_periods,freq='M')
    
    df_month = pd.DataFrame(index=rng)
    
    df_month['month'] = df_month.index.month
    df_month['year'] = df_month.index.year
    header = ['n','monthProc','monthSol']
    df_sol = pd.read_csv('balance.csv',sep=',',names=header,nrows=12,index_col='n')
    
    precSol = VectorAnual(lcoh,anho_contr,indSol,2021)
    
    enerProc = dict(df_sol.monthProc)
    enerSol = dict(df_sol.monthSol)
    prSol = dict(precSol)
    
    df_month['precioSol'] = df_month.year.map(prSol).fillna(0)
    
    df_month['enerProc'] = df_month.month.map(enerProc)
    df_month['enerSol'] = df_month.month.map(enerSol)
    
    finSolar = inicSolar + anho_contr
    finEval = inicSolar + anho_proy
    
    mask = (df_month.index.year < inicSolar) | (df_month.index.year > finSolar)
    col_name = 'enerSol'
    df_month.loc[mask,col_name] = 0
    df_month['enerHeater'] = df_month.enerProc/(effHeater/100)
    #########################    
    
    tot_proy = anho_proy*52
    df_new = EnerConv(df,indice,'Semanal')
    df_new['returns'] = df_new.std_unit.pct_change()
    sample = df_new.returns.dropna()
    n_obs = df_new.returns.count()
    
    if n_obs > tot_proy:
        n_eval = tot_proy
    
    else:
        n_eval=n_obs
    
    ahr = []
    for n in np.arange(0,N_iter,1):

        rnd_walk = np.random.choice(sample,n_eval)
        
        random_walk = pd.Series(rnd_walk[0:n_eval], index=sample.index[0:n_eval])
        start = df_new.std_unit.first('D')
        ind_random = start.append(random_walk.add(1))
        df_new['rnd'] = ind_random.cumprod()
        
        while ( (df_new.rnd.max() > 1.4*df_new.std_unit.max()) | (df_new.rnd.min() < 0.3*df_new.std_unit.min()) ):
            rnd_walk = np.random.choice(sample,n_eval)    
            random_walk = pd.Series(rnd_walk[0:n_eval], index=sample.index[0:n_eval])
            start = df_new.std_unit.first('D')
            ind_random = start.append(random_walk.add(1))
            df_new['rnd'] = ind_random.cumprod()


        start_proy = df_new.std_unit.last('D')
        ind_proy = pd.date_range(start_proy.index[0]+pd.Timedelta('1W'),freq='W',periods=n_eval, name='Date')
        random_walk = pd.Series(rnd_walk, index=ind_proy)
        proy_random = start_proy.append(random_walk.add(1))
        proy_walk = proy_random.cumprod()
        
        df_tmp = pd.concat([df_new,proy_walk])
        
        df_tmp = df_tmp.rename(columns={0:'proy'})
            
        df_tmp = df_tmp.proy
        
        df_tmp = df_tmp[(df_tmp.index.year > 2021) & (df_tmp.index.year < finSolar)]
        
        df_proy = df_tmp.resample('M').mean()
        df_month['proy'] = df_proy + factInd
        
        df_month = EnerConvProy(df_month,indice,'Mensual','proy')
        
        df_month['MWh_cl'] = df_month.MWh_proy / (effHeater/100)
        
#    df_month = df_month[df_month.index.year < finEval]
        
        df_month['convPay'] = (df_month.MWh_cl * df_month.enerProc)/1e3
        df_month['solPay'] = (df_month.precioSol * df_month.enerSol)/1e3
        df_month['fossPay'] = (df_month.MWh_cl * (df_month.enerProc - df_month.enerSol))/1e3
        df_month['totPay'] = df_month.solPay + df_month.fossPay
        
        ahr_tmp = df_month.totPay.sum() - df_month.convPay.sum()
        ahr.append(ahr_tmp)
    
    return ahr


ahr1 = MonteCarlo(df,indice,lcoh,anho_contr,anho_proy,effHeater,factInd,N_iter = N_iter, inicSolar = 2022)
ahr = np.array(ahr1)
hist, edges = np.histogram(ahr, density=True, bins=20)
hist_df = pd.DataFrame({'column': hist,
                        "left": edges[:-1],
                        "right": edges[1:]})
hist_df["interval"] = ["%d to %d" % (left, right) for left, 
                        right in zip(hist_df["left"], hist_df["right"])]

src_hist = ColumnDataSource(hist_df)

p6 = Figure(title='Histograma, ' + str(N_iter) + ' escenarios', tools=TOOLS, background_fill_color="#fafafa")
p6.quad(top='column', bottom=0, left='left', right='right',
           fill_color="navy", line_color="white", alpha=0.5, source=src_hist)


x_data, y_data = cdf(ahr1)
src_cdf = ColumnDataSource(data=dict(x=x_data,y=y_data))
p7 = Figure(tools=TOOLS, background_fill_color="#fafafa")
p7.line('x','y',source=src_cdf)         
   

buttCalcMC = Button(label="Monte Carlo", button_type="success")
n_esc = TextInput(value=str(N_iter), title="Número de escenarios",width=wdt)


def CalcEcon():
    
    areaCol = int(ACol.value)
    enerCol = float(ECol.value)
    solFrac = float(SFra.value)
    
    costCol_m2 = float(CCol.value)
    FIT_m2 = float(fitm2.value) 
    perc_fee = float(percFee.value)
    percOpex = float(POPEX.value)
    indSol = float(indexSolar.value)
    
    effHeater = float(eff_heater.value)
    fuel = dropdownFuel.value
    costFuel = float(CFuel.value)
    indFuel = float(indexFuel.value)
    
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
    if indice == 'Mont Belvieu':
        df = mont
    elif indice == 'Brent':
        df = brent
    elif indice == 'WTI':
        df = wti
    elif indice == 'Henry Hub':
        df = hhub
    
    rnd_walk = RandomWalk(df,indice,30)
    rnd_walk = EnerConvProy(rnd_walk,indice,'Semanal','proy')
    source_rnd.data=rnd_walk

    lcoh = CalcEcon()
    
    df_month, table_proy2 = ProyMonth(rnd_walk,indice,lcoh,anho_contr,anho_proy,effHeater,factInd,inicSolar = 2022)
    sourceMonth.data = df_month
    infoProy2.text = str(table_proy2)

def RunMC():
    lcoh = CalcEcon()
    N_iter = int(n_esc.value)
    effHeater = float(eff_heater.value)
    
    df = pd.DataFrame()
    indice = ind.value
    factInd = float(fctInd.value)
    anho_contr = int(anhoContr.value)
    anho_proy = int(anhoProy.value)
    if indice == 'Mont Belvieu':
        df = mont
    elif indice == 'Brent':
        df = brent
    elif indice == 'WTI':
        df = wti
    elif indice == 'Henry Hub':
        df = hhub
    
    ahr1 = MonteCarlo(df,indice,lcoh,anho_contr,anho_proy,effHeater,factInd,N_iter = N_iter, inicSolar = 2022)
    ahr = np.array(ahr1)
    hist, edges = np.histogram(ahr, density=True, bins=50)
    hist_df = pd.DataFrame({'column': hist,
                            "left": edges[:-1],
                            "right": edges[1:]})
    hist_df["interval"] = ["%d to %d" % (left, right) for left, 
                            right in zip(hist_df["left"], hist_df["right"])]
    
    src_hist.data = hist_df
    p6.title.text = 'Histograma, ' + str(N_iter) + ' escenarios'
    
    x_data, y_data = cdf(ahr1)
    new_data=dict(x=x_data,y=y_data)
    src_cdf.data  = new_data

buttCalcEcon.on_click(CalcEcon)
buttCalcWalk.on_click(CreateWalk)
buttCalcMC.on_click(RunMC)
##############
spc = 50
layout = column(Spacer(height=spc),
                row(ACol,ECol,SFra,dropdownCalc),
                row(CCol,fitm2,percFee,POPEX,indexSolar),
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