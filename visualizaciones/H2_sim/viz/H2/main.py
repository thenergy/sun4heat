#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 20:46:28 2021

@author: fcuevas
"""

import sys
sys.path
# sys.path.append('/Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/scripts')
sys.path.append('/home/diegonaranjo/Documentos/Thenergy/sun4heat/scripts')

from funciones_econ import LCOE_FV

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
# path = '/Users/fcuevas/Documents/Trabajo/thenergy/H2_sim'
path = '/home/diegonaranjo/Documentos/Thenergy/H2_sim'

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

res_tot['sys_powMW'] = res_tot['sys_pow']/1000

res_tot['hr_el'] = res_tot['sys_powMW'].mask(res_tot.sys_pow > 0,1)




res_tot['hr_elOvLoad'] = res_tot['sys_powMW'].mask(res_tot.sys_powMW < max_powEl,1)

res_tot['hr_elOvLoad'] = res_tot['hr_elOvLoad'].mask(res_tot.hr_elOvLoad > 0.999999999,0)

#res_tot['hr_elOvload'] = res_tot['sys_powMW'].replace({(res_tot['sys_powMW']>max_powEl) : 1 , (res_tot['sys_powMW']<max_powEl) : 0})

#res_tot['hr_elOvload'] = res_tot['sys_powMW'].mask(res_tot.sys_powMW < max_powEl,0,other=1)
#res_tot['hr_elOvload'] = res_tot['sys_powMW'].mask(res_tot.sys_powMW > max_powEl,1)




res_month = res_tot.groupby([res_tot.index.year,res_tot.index.month]).sum()
res_month = res_month.reset_index()
res_month['Meses'] = res_month.level_1.map(mnths)

month_max = res_tot.groupby([res_tot.index.year,res_tot.index.month]).max()
month_max = month_max.reset_index()
month_max['Meses'] = month_max.level_1.map(mnths)

res_month['max_FV'] = month_max.tot_pow

res_ann = res_tot.groupby([res_tot.index.year]).sum()
res_ann = res_ann.reset_index()
res_ann['Total'] = 'Total'


source_month = ColumnDataSource(data=res_month)
source_ann = ColumnDataSource(data=res_ann)

cols_month = [
        TableColumn(field="Meses", title="Mes",width=60),
        TableColumn(field="tot_pow", title="FV (MWh/mes)",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="max_FV", title="max FV (MW)",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="h2", title="H2 (ton/mes)",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="agua", title="Agua (m3/mes)",width=150, formatter=NumberFormatter(format="0"))]

table_month = DataTable(columns=cols_month, source=source_month,width=600, height=450,
                       editable=True)

cols_ann = [
        TableColumn(field="Total", title=" ",width=60),
        TableColumn(field="tot_pow", title="FV (MWh/año)",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="h2", title="H2 (ton/año)",width=150, formatter=NumberFormatter(format="0")),
        TableColumn(field="agua", title="Agua (m3/año)",width=150, formatter=NumberFormatter(format="0"))]

table_ann = DataTable(columns=cols_ann, source=source_ann,width=600, height=450,
                       editable=True)



#################################
wdt = 250
PotFV = TextInput(value=str(pot_fv), title="Potencia FV (MW)",width=wdt)
WatEl = TextInput(value=str(wat_el), title="Agua electrolizador (lt/kg)",width=wdt)
EffEl = TextInput(value=str(eff_el), title="Eficiencia electrolizador (%)",width=wdt)

PotEl = TextInput(value=str(pot_el), title="Potencia electrolizador (MW)",width=wdt)
NumEl = TextInput(value=str(num_el), title="Número electrolizadores (-)",width=wdt)
OvLoadEl = TextInput(value=str(num_el), title="Overload electrolizador (%)",width=wdt)

menuRes=["Generacion FV","Agua Electrolizador","Generacion H2"]
dropdownRes = Select(value="Generacion FV", title="Resultado",options=menuRes,width=300) 

buttCalcUpdate = Button(label="Calcular", button_type="success",width=wdt)

res = 'tot_pow'

day_val = res_tot[res].groupby([res_tot.index.year,res_tot.index.month,res_tot.index.day]).sum()
day_val = day_val.reset_index()

day_val['months'] = day_val.level_1.map(mnths)

dayVal = day_val.level_2
monthValue = day_val.months
val = day_val[res].round(1) 

source_day = ColumnDataSource(data=dict(day_vs = dayVal,monthValue=monthValue,val_vs=val))

y_rg = np.arange(1,32)
y_rg = [str(x) for x in y_rg]



# costo fv (US$/kW)
costoFV_kW = 1000

CAPEX = pot_fv * costoFV_kW 

percOpex = 1.5

OPEX = CAPEX * percOpex/100

indSol = 1.5

degFV = 0.5
#################################
# INFORMACION EVALUACION
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

enerYield = res_tot.tot_pow.sum()/1000

table_eval,annual_res, annual_proy = LCOE_FV(CAPEX,OPEX,tasa_deuda, pago_deuda,perc_deuda,impuesto,tasa_equi,dif_infl,infl_cl,
              anho_contr,anho_proy,val_depr,anho_depr,enerYield,indSol)

annual_res.costSol[0] = np.nan
an=pd.date_range('2021-01',freq='A',periods=len(annual_res))
annual_res.index = an
lcoe = float(table_eval['LCOE (US$/MWh)'])
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
    TableColumn(field="fljAcum", title="Flujo acumulado (kUS$)", formatter=NumberFormatter(format="0.00"))
]

data_table = DataTable(columns=columns, source=source_flujo,width=700, height=480)


infoEval = PreText(text=str(table_eval), width=320)



CFV = TextInput(value=str(costoFV_kW), title="Costo FV (US$/kW):",width=wdt)
POPEX = TextInput(value=str(percOpex), title="OPEX (% CAPEX):",width=wdt)
indexSolar = TextInput(value=str(indSol), title="Indexación solar (%)",width=wdt)
degSolar = TextInput(value=str(degFV), title="Degradación anual FV (%)",width=wdt)
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
buttCalcEcon = Button(label="Calcular", button_type="success",width=wdt)
################################################################################################## 
TOOLS="hover,crosshair,pan,wheel_zoom,box_zoom,reset,box_select,lasso_select"
p1 = Figure(y_range=y_rg,x_range=FactorRange(*months),
           x_axis_location="below", plot_width=1360, plot_height=750,
           tools=TOOLS, toolbar_location='above')

p1.grid.grid_line_color = None
p1.axis.axis_line_color = 'black'
p1.axis.major_tick_line_color = 'black'
p1.axis.major_label_text_font_size = "10pt"
p1.axis.major_label_standoff = 0
p1.axis.axis_label_text_align = 'center'

p1.xaxis.major_label_orientation = pi / 3

mapper1 = LinearColorMapper(palette=cc.rainbow, low=0, high=val.max())
p1.rect(x='monthValue', y='day_vs', width=1.0, height=1.0,
       source=source_day,
       fill_color={'field': 'val_vs', 'transform': mapper1},
       line_color='black')

text_props1 = {"source": source_day, "text_align": "center", "text_baseline": "middle"}
r1 = p1.text(x='monthValue', y='day_vs', text="val_vs", **text_props1)
r1.glyph.text_font_style="bold"
r1.glyph.text_font_size="10pt"

color_bar1 = ColorBar(color_mapper=mapper1, major_label_text_font_size="8pt",
                     ticker=BasicTicker(desired_num_ticks=6),
                     formatter=PrintfTickFormatter(format="%d"),
                     label_standoff=6, border_line_color=None, location=(0, 0))
p1.add_layout(color_bar1, 'right')





def ChangeData():
    # Potencia instalada sistema FV (MW)
    pot_fv = float(PotFV.value)
    # calcular energía total según la potencia definida
    pv['tot_pow'] = pv.sys_pow * pot_fv / 1000 
    # agua necesaria para producir 1 kg de H2
    wat_el = float(WatEl.value) 
    # eficiencia del electrolizador (%)
    eff_el = float(EffEl.value) 
    #  energía necesaria para producir 1 kg de H2 con electrólisis
    ener_h2 = enerTeo_h2 /(eff_el/100)
     
    res_tot = pv[['sys_pow','ac_pow','dc_pow','tot_pow']]
    res_tot['h2'] = res_tot.tot_pow / ener_h2
    res_tot['agua'] = res_tot.h2 * wat_el
    
    res_month = res_tot.groupby([res_tot.index.year,res_tot.index.month]).sum()
    res_month = res_month.reset_index()
    res_month['Meses'] = res_month.level_1.map(mnths)
    
    month_max = res_tot.groupby([res_tot.index.year,res_tot.index.month]).max()
    month_max = month_max.reset_index()
    month_max['Meses'] = month_max.level_1.map(mnths)
    
    res_month['max_FV'] = month_max.tot_pow
    
    res_ann = res_tot.groupby([res_tot.index.year]).sum()
    res_ann = res_ann.reset_index()
    res_ann['Total'] = 'Total'
    
    new_data = dict(res_month)
    source_month.data = new_data
    
    new_data = dict(res_ann)
    source_ann.data = new_data
    
    men = dropdownRes.value
    
    if men == "Generacion FV":
        res = 'tot_pow'
        
    elif men == "Agua Electrolizador":
        res = 'agua'
        
    elif men == "Generacion H2":
        res = 'h2'
    
    day_val = res_tot[res].groupby([res_tot.index.year,res_tot.index.month,res_tot.index.day]).sum()
    day_val = day_val.reset_index()
    
    day_val['months'] = day_val.level_1.map(mnths)
    
    dayVal = day_val.level_2
    monthValue = day_val.months
    val = day_val[res].round(1) 
    
    new_data=dict(day_vs = dayVal,monthValue=monthValue,val_vs=val)
    source_day.data = new_data





    #############################
def CalcEcon():
    
    # Potencia instalada sistema FV (MW)
    pot_fv = float(PotFV.value)
    # calcular energía total según la potencia definida
    pv['tot_pow'] = pv.sys_pow * pot_fv / 1000 
    res_tot = pv[['sys_pow','ac_pow','dc_pow','tot_pow']]
    
    
    costoFV_kW = float(CFV.value)
    percOpex = float(POPEX.value)
    CAPEX = pot_fv * costoFV_kW 
    
    percOpex = float(POPEX.value)
    
    OPEX = CAPEX * percOpex/100
    
    indSolar = float(indexSolar.value)
    degFV = float(degSolar.value)


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
    
    
    enerYield = res_tot.tot_pow.sum()/1000

    table_eval,annual_res, annual_proy = LCOE_FV(CAPEX,OPEX,tasa_deuda, pago_deuda,perc_deuda,impuesto,tasa_equi,dif_infl,infl_cl,
              anho_contr,anho_proy,val_depr,anho_depr,enerYield,indSol)
    
    annual_res.costSol[0] = np.nan
    an=pd.date_range('2021-01',freq='A',periods=len(annual_res))
    annual_res.index = an
    lcoe = float(table_eval['LCOE (US$/MWh)'])
    
    new_data=dict(x1=annual_res.index.year,ingEner=annual_res.ing_ener,
                                          opex=annual_res.opex,utils=annual_res.utilidades,
                                          perd=annual_res.perdidas,base_imp=annual_res.base_imp,
                                          imp_pc=annual_res.imp_PC,util_imp=annual_res.util_imp,
                                          fljNeto=annual_res.flujo_neto,fljAcum=annual_res.flujo_acum,
                                          van_vect=annual_res.vect_VAN)
    
    source_flujo.data = new_data
    
    infoEval.text = str(table_eval)

#
#CFV = TextInput(value=str(costoFV_kW), title="Costo FV (US$/kW):",width=wdt)
#POPEX = TextInput(value=str(percOpex), title="OPEX (% CAPEX):",width=wdt)
#indexSolar = TextInput(value=str(indSol), title="Indexación solar (%)",width=wdt)
#degSolar = TextInput(value=str(degFV), title="Degradación anual FV (%)",width=wdt)
## Evaluación económica
#anhoContr = TextInput(value=str(anho_contr), title="Años de contrato ESCO",width=wdt)
#anhoProy = TextInput(value=str(anho_proy), title="Años evaluación escenario",width=wdt)
#anhoDepr = TextInput(value=str(anho_depr), title="Años depreciación",width=wdt)
#percDeuda = TextInput(value=str(perc_deuda), title="Porcentaje deuda",width=wdt)
#tasaDeuda = TextInput(value=str(tasa_deuda), title="Tasa deuda (%)",width=wdt)
#pagoDeuda = TextInput(value=str(pago_deuda), title="Años pago deuda",width=wdt)
#tasaEqui = TextInput(value=str(tasa_equi), title="Tasa capital propio (%)",width=wdt)
#inflChile = TextInput(value=str(infl_cl), title="Inflación Chile (%)",width=wdt)




buttCalcUpdate.on_click(ChangeData)
buttCalcEcon.on_click(CalcEcon)
##############
spc = 50
layout = column(Spacer(height=spc),
                row(PotFV),
                row(PotEl, NumEl, OvLoadEl, WatEl, EffEl),
                row(dropdownRes),
                row(buttCalcUpdate),
                row(p1,column(table_month, table_ann)),
                
                Spacer(height=spc),
                row(CFV,POPEX,indexSolar),
                row(degSolar),

                Spacer(height=spc),
                row(anhoContr,anhoProy,anhoDepr,pagoDeuda),
                row(percDeuda,tasaDeuda,tasaEqui,inflChile),
                buttCalcEcon,
                
                Spacer(height=spc),
                row(data_table,infoEval))
############################################
curdoc().add_root(layout)