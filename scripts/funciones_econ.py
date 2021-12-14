#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 13:05:09 2019

@author: fcuevas
"""
import pandas as pd
import numpy as np

from funciones import flat_list

#path = '/Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/'
#path = '/home/diegonaranjo/Documentos/Thenergy/sun4heat/'
path = '/home/ubuntu/Thenergy/diego/sun4heat/'

def TableCapex(aCol,costCol_m2,costInst_m2, cost_storage, vol, land_prep, fact_uso, cont, fit, fee, 
               table_inst, cHH_mec, cHH_mec_help, cHH_elec, cHH_elec_help):
    '''
    Calcula el CAPEX de la inversión.

    Parameters
    ----------
    aCol : int
        Área del colector.
    costCol_m2 : float
        Costo del colector por m**2
    costInst_m2 : float
        Costo de la isntalación por m**2.
    cost_storage : float
        Costo por almacenamiento.
    vol : int
        Volumen del almacenador.
    land_prep : TYPE
        DESCRIPTION.
    fact_uso : TYPE
        DESCRIPTION.
    cont : TYPE
        DESCRIPTION.
    fit : TYPE
        DESCRIPTION.
    fee : TYPE
        DESCRIPTION.
    table_inst : TYPE
        DESCRIPTION.
    cHH_mec : TYPE
        DESCRIPTION.
    cHH_mec_help : TYPE
        DESCRIPTION.
    cHH_elec : TYPE
        DESCRIPTION.
    cHH_elec_help : TYPE
        DESCRIPTION.

    Returns
    -------
    table_capex : TYPE
        DESCRIPTION.

    '''
    #Mano obra local (US$/m2)
    manObra = table_inst.mecanico.sum() * cHH_mec + table_inst.mecanico.sum() * cHH_mec_help + \
    table_inst.electrico.sum() * cHH_elec + table_inst.electrico.sum() * cHH_elec_help
    
    costCol = costCol_m2*aCol
    costInst = costInst_m2*aCol
    # Capex 
    Capex_pre = (costCol + cost_storage*vol + land_prep*aCol*fact_uso + costInst) * (1+cont/100) + aCol*fit 
    fee_th = Capex_pre*fee/100
    Capex = Capex_pre + fee_th
    
    
    table_capex = pd.Series()
    table_capex['Costo paneles (MUS$)']     = "{:10.1f}".format(costCol/1000)
    table_capex['Costo instalación (MUS$)'] = "{:10.1f}".format(costInst/1000)
    table_capex['Costo lugar instalación (MUS$)']     = "{:10.1f}".format(aCol * fact_uso * land_prep / 1000)
    table_capex['Freight, Insurance, Tax (MUS$)']             = "{:10.1f}".format(fit*aCol / 1000)
    table_capex['Mano obra (MUS$)']         = "{:10.1f}".format(manObra / 1000)
    table_capex['Capex_pre (MUS$)']         = "{:10.1f}".format(Capex_pre / 1000)
    table_capex['Fee (MUS$)']    = "{:10.1f}".format(fee_th / 1000)
    table_capex['CAPEX (MUS$)']             = "{:10.1f}".format(Capex/1000)
    
    return table_capex
 
def TableOpex(aCol,costCol_m2,SF_refresh,PM,consElectrico,costElectrico,nLimp,costLimp,nOper,salOper,
              aguaLimp,aguaCost,nInspect,cInspect,monitoreo):
    '''
    

    Parameters
    ----------
    aCol : int
        Área colector.
    costCol_m2 : float
        Costo del colector por m**2.
    SF_refresh : TYPE
        DESCRIPTION.
    PM : TYPE
        DESCRIPTION.
    consElectrico : TYPE
        DESCRIPTION.
    costElectrico : TYPE
        DESCRIPTION.
    nLimp : TYPE
        DESCRIPTION.
    costLimp : TYPE
        DESCRIPTION.
    nOper : TYPE
        DESCRIPTION.
    salOper : TYPE
        DESCRIPTION.
    aguaLimp : TYPE
        DESCRIPTION.
    aguaCost : TYPE
        DESCRIPTION.
    nInspect : TYPE
        DESCRIPTION.
    cInspect : TYPE
        DESCRIPTION.
    monitoreo : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    costCol = costCol_m2*aCol
    #Solar Field maintenance
    SFM = SF_refresh + PM
    
    OPEX=aCol*costCol_m2*SFM/100 + aCol*consElectrico*costElectrico/1000 + (nLimp*costLimp*aCol) + nOper*salOper + \
(aguaLimp*aCol/1000*aguaCost) + nInspect*cInspect + monitoreo     

    table_opex = pd.Series()
    table_opex['Mantenimiento campo solar (MUS$/año)'] = "{:10.1f}".format(costCol*SFM/100/1000)
    table_opex['Consumo eléctrico (MUS$/año)']         = "{:10.1f}".format(aCol*consElectrico*costElectrico/1000/1000)
    table_opex['Costo limpieza (MUS$/año)']            = "{:10.1f}".format(nLimp*costLimp*aCol/1000)
    table_opex['Costo agua (MUS$/año)']                = "{:10.1f}".format(aguaLimp*aCol/1000*aguaCost/1000)
    table_opex['Costo operarios (MUS$/año)']           = "{:10.1f}".format(nOper*salOper/1000)
    table_opex['Costo inspecciones (MUS$/año)']        = "{:10.1f}".format(nInspect*cInspect/1000)
    table_opex['Costo monitoreo (MUS$/año)']        = "{:10.1f}".format(monitoreo/1000)
    table_opex['OPEX (MUS$/año)']        = "{:10.1f}".format(OPEX/1000)
    
    return table_opex


#table_eval,flujo_acum,vals_econ,eje_anho = TableEval(Capex,OPEX,tasa_deuda, pago_deuda,perc_deuda,
#                                                                              impuesto,tasa_equi,dif_infl,anho_contr,val_depr,anho_depr,inSol)
def TableEval(Capex,OPEX,tasa_deuda, pago_deuda,perc_deuda,impuesto,tasa_equi,dif_infl,anho_contr,val_depr,anho_depr,inSol):
    '''
    

    Parameters
    ----------
    Capex : TYPE
        DESCRIPTION.
    OPEX : TYPE
        DESCRIPTION.
    tasa_deuda : TYPE
        DESCRIPTION.
    pago_deuda : TYPE
        DESCRIPTION.
    perc_deuda : TYPE
        DESCRIPTION.
    impuesto : TYPE
        DESCRIPTION.
    tasa_equi : TYPE
        DESCRIPTION.
    dif_infl : TYPE
        DESCRIPTION.
    anho_contr : TYPE
        DESCRIPTION.
    val_depr : TYPE
        DESCRIPTION.
    anho_depr : TYPE
        DESCRIPTION.
    inSol : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    
#    print ("funcion eval")
    # monto de la deuda
    deuda = perc_deuda/100 * Capex
    # porcentaje equity
    perc_equi = 100 - perc_deuda
    # anualidad deuda
    pg = Pago(tasa_deuda/100,pago_deuda,deuda)
    #wacc chile
    wacc_cl = perc_deuda/100 * tasa_deuda/100 * (1-impuesto/100) + perc_equi/100 * tasa_equi/100
    wacc_us = (1+wacc_cl)*dif_infl - 1
    
    inversion = np.zeros(anho_contr+1).reshape(anho_contr+1,1) 
    inversion[0] = Capex
    debt = np.zeros(anho_contr+1).reshape(anho_contr+1,1) 
    debt[0] = deuda
    
#    print ("check 1")
    amrt,interes = PagoPrinInt(pg,tasa_deuda/100,pago_deuda,deuda,anho_contr)
#    print ("check 2")
    opex = Vector(OPEX,anho_contr,2)
    ing_enrg = Vector(inSol,anho_contr,2)
    depr = Depr(val_depr,anho_depr,anho_contr)
    
    utilidades = ing_enrg - opex - interes - depr
    
    perdidas = Perdidas(utilidades)
    base_impuesto = BaseImpuesto(utilidades,perdidas)
    impuestoPrimCat = -base_impuesto * impuesto/100
    util_impuesto = utilidades + impuestoPrimCat
    
    flujo_neto = -inversion + debt + depr + util_impuesto - amrt
    flujo_acum = FlujoAcum(flujo_neto)
    VAN = Van(wacc_us,flujo_neto).sum()/1000
    TIR = Tir(flujo_neto)*100
    payback = Payback(flujo_acum)   
    
    
    table_eval = pd.Series()
    table_eval['VAN (MUSD)'] = "{:10.1f}".format(VAN)
    table_eval['TIR (%)'] = "{:10.1f}".format(TIR)
    table_eval['Payback (Años)'] = "{:10.1f}".format(payback)
    
    anhos = np.arange(0,anho_contr+1)
    
    anh = ["Año " + str(anho) for anho in anhos]
    vars_econ = ['Energía','OPEX','Deuda','Utilidades','Flujo neto']
    eje_anho = [(an,vr) for an in anh for vr in vars_econ]
    vals_econ = [(enr,opx,deu,util,flu) for enr,opx,deu,util,flu in zip(ing_enrg/1000,-opex/1000,-interes/1000,utilidades/1000,flujo_neto/1000)]
    vals_econ = flat_list(vals_econ)
    
    return table_eval,flujo_acum,vals_econ,eje_anho


def LCOH_calc(Capex,OPEX,tasa_deuda, pago_deuda,perc_deuda,impuesto,tasa_equi,dif_infl,infl_cl,
              anho_contr,anho_proy,val_depr,anho_depr,enerYield,indSol,indFuel,CFuel):
    '''
    

    Parameters
    ----------
    Capex : TYPE
        DESCRIPTION.
    OPEX : TYPE
        DESCRIPTION.
    tasa_deuda : TYPE
        DESCRIPTION.
    pago_deuda : TYPE
        DESCRIPTION.
    perc_deuda : TYPE
        DESCRIPTION.
    impuesto : int
        Porcentaje de impuesto.
    tasa_equi : TYPE
        DESCRIPTION.
    dif_infl : TYPE
        DESCRIPTION.
    infl_cl : TYPE
        DESCRIPTION.
    anho_contr : TYPE
        DESCRIPTION.
    anho_proy : TYPE
        DESCRIPTION.
    val_depr : TYPE
        DESCRIPTION.
    anho_depr : TYPE
        DESCRIPTION.
    enerYield : TYPE
        DESCRIPTION.
    indSol : TYPE
        DESCRIPTION.
    indFuel : TYPE
        DESCRIPTION.
    CFuel : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
#    print ("funcion eval")
    # monto de la deuda
    deuda = perc_deuda/100 * Capex
    # porcentaje equity
    perc_equi = 100 - perc_deuda
    # anualidad deuda
    pg = Pago(tasa_deuda/100,pago_deuda,deuda)
    #wacc chile
    wacc_cl = perc_deuda/100 * tasa_deuda/100 * (1-impuesto/100) + perc_equi/100 * tasa_equi/100
#    wacc_us = (1+wacc_cl)*dif_infl - 1 
#    print (wacc_cl,wacc_us)
    
    inversion = np.zeros(anho_contr+1).reshape(anho_contr+1,1) 
    inversion[0] = Capex
    debt = np.zeros(anho_contr+1).reshape(anho_contr+1,1) 
    debt[0] = deuda
    
#    print ("check 1")
    amrt,interes = PagoPrinInt(pg,tasa_deuda/100,pago_deuda,deuda,anho_contr)
#    print ("check 2")
    opex = Vector(OPEX,anho_contr,infl_cl)
    
#    lcoh = 120.42
    vm = []
    lc = []
    for n,lcoh in enumerate(np.arange(1,1000,1)):
        inSol = enerYield * lcoh
        
        ing_enrg = Vector(inSol,anho_contr,indSol)
        depr = Depr(val_depr,anho_depr,anho_contr)
        
        utilidades = ing_enrg - opex - interes - depr
        
        perdidas = Perdidas(utilidades)
        base_impuesto = BaseImpuesto(utilidades,perdidas)
        impuestoPrimCat = -base_impuesto * impuesto/100
    #    impuestoPrimCat = ImpuestoPrimCat(utilidades,impuesto)
        util_impuesto = utilidades + impuestoPrimCat
        
        flujo_neto = -inversion + debt + depr + util_impuesto - amrt
        flujo_acum = FlujoAcum(flujo_neto)
        vn = Van(wacc_cl,flujo_neto)
        VAN = vn.sum()/1000
        
        vm.append(VAN)
        lc.append(lcoh)
        
        if n == 0:
            pass
        
        else:
            vn_tmp = vm[n] * vm[n-1]
            if vn_tmp < 0:
                break
    
    for n,l in enumerate(np.arange(lc[-2],lc[-1],0.001)):

        inSol = enerYield * l
        
        ing_enrg = Vector(inSol,anho_contr,indSol)
        depr = Depr(val_depr,anho_depr,anho_contr)
        
        utilidades = ing_enrg - opex - interes - depr
        
        perdidas = Perdidas(utilidades)
        base_impuesto = BaseImpuesto(utilidades,perdidas)
        impuestoPrimCat = -base_impuesto * impuesto/100
    #    impuestoPrimCat = ImpuestoPrimCat(utilidades,impuesto)
        util_impuesto = utilidades + impuestoPrimCat
        
        flujo_neto = -inversion + debt + depr + util_impuesto - amrt
        flujo_acum = FlujoAcum(flujo_neto)
        vn = Van(wacc_cl,flujo_neto)
        VAN = vn.sum()/1000        

        if (VAN < 0.5 and VAN > -0.5):
            lcoh = l
            break
    
    TIR = Tir(flujo_neto)*100
    payback = Payback(flujo_acum)   
    
    costSolar = Vector(lcoh,anho_contr,indSol)
    costFuel = Vector(CFuel,anho_contr,indFuel)
    
    table_eval = pd.Series()
    table_eval['LCOH (US$/MWh)'] = "{:10.1f}".format(lcoh)
    table_eval['CAPEX (kUS$)'] = "{:10.1f}".format(Capex/1000)
    table_eval['OPEX (kUS$)'] = "{:10.1f}".format(OPEX/1000)
    table_eval['VAN (kUS$)'] = "{:10.1f}".format(VAN)
    table_eval['TIR (%)'] = "{:10.1f}".format(TIR)
    table_eval['Payback (Años)'] = "{:10.1f}".format(payback)
    
    anhos = np.arange(0,anho_contr+1)    
    annual_table = pd.DataFrame(index=anhos)
    annual_table['ing_ener'] = ing_enrg/1000
    annual_table['opex'] = opex/1000
    annual_table['utilidades'] = utilidades/1000
    annual_table['perdidas'] = perdidas/1000
    annual_table['base_imp'] = base_impuesto/1000
    annual_table['imp_PC'] = impuestoPrimCat/1000
    annual_table['util_imp'] = util_impuesto/1000
    annual_table['flujo_neto'] = flujo_neto/1000
    annual_table['flujo_acum'] = flujo_acum/1000
    annual_table['vect_VAN'] = vn/1000
    annual_table['costFuel'] = costFuel
    annual_table['costSol'] = costSolar
    
    anhosPr = np.arange(0,anho_proy+1)    
    annual_proy = pd.DataFrame(index=anhosPr)
    costFl = Vector(CFuel,anho_proy,indFuel)
    costSlr = Vector(lcoh,anho_proy,indSol)
    oym = Vector(OPEX,anho_proy,infl_cl)
    annual_proy['cost_fuel'] = costFl
    annual_proy['cost_sol'] = costSlr
    annual_proy['oym'] = oym
    
    lc_vect = []
    for n,lc in enumerate(annual_proy.cost_sol):
        if n < anho_contr:
            lc_vect.append(lc)
        else:
            lc_vect.append(0)
            
    annual_proy['cost_sol'] = lc_vect
    
    return table_eval, annual_table, annual_proy


###################################    
def Pago(tasa,periodo,monto):
    pago =  (tasa * (1+tasa)**periodo * monto) / ((1+tasa)**periodo -1)
    return pago    

def PagoPrinInt(pago,tasa,periodo,monto,contrato):
    n = contrato+1
    vct = np.zeros(n).reshape(n,1)
    vctInt = np.zeros(n).reshape(n,1)
    A1 = pago - monto*tasa
    vct[1] = A1
    vctInt[1] = pago-A1
    anhos = np.arange(2,periodo+1)
    for anho in anhos:
        An = A1*(1+tasa)**(anho-1)
        vct[anho] = An
        vctInt[anho] = pago-An
        
    return vct,vctInt

def Vector(val,contrato,infl):
    n = contrato+1
    vct = np.zeros(n).reshape(n,1)
    anhos = np.arange(1,n)
    for anho in anhos:
        if anho == 1:
            vct[anho] = val
        else:
            vct[anho] = vct[anho-1]*(1+infl/100)
        
    return vct

def Depr(val,per,contrato):
    n = contrato+1
    vct = np.zeros(n).reshape(n,1)
    anhos = np.arange(1,per+1)
    for anho in anhos:
        vct[anho] = val
        
    return vct  
            
def Perdidas(util):
    perdidas = util * 0
    for num,val in enumerate(util):
        if num == 1:
            if val < 0:
                perdidas[num] = val
            else:
                perdidas[num] = 0
                
        else:
            if perdidas[num-1]+val<val:
                perdidas[num]=perdidas[num-1]+val
            else:
                0   
    return perdidas

def BaseImpuesto(util, perd):
    base_imp = util * 0 
    for num,(utl, prd) in enumerate(zip(util,perd)):
        
        if ((utl<0)):
            base_imp[num] = 0
#        elif (prd>0):
#            base_imp[num] = prd
        else:
            base_imp[num] = utl
    return base_imp

def ImpuestoPrimCat(util,imp):
    imp_pc = util*0
    for num,utl in enumerate(util):
        if utl < 0:
#            print ('0 ',utl)
            imp_pc[num]=0
        else:
#            print ('1 ',utl)
            imp_pc[num]=utl*imp/100
            
    return imp_pc
    
    
    
def FlujoAcum(flujo):
    flujoAc=flujo*0
    for num,val in enumerate(flujo):
        if val == 0:
            flujoAc[num] = val
        else:
            flujoAc[num] = val + flujoAc[num-1]
    return flujoAc

def Van(tasa,flujo):
    van_vect = flujo*0
    for num,val in enumerate(flujo):
        if num == 0:
            van_vect[num] = val
        else:
            van_vect[num] = val/(1+tasa)**num
            
#    print (van_vect)
    return van_vect
        
def Tir(flujo):
    for i in np.arange(0,1,0.0005):
        van_tmp = Van(i,flujo).sum()
        if van_tmp < 10000 and van_tmp > -10000:
            break
    return i
        
def Payback(flujo):
    for enum,val in enumerate(flujo):
        if val > 0:
            break
        
    return enum



####################################################################
####################################################################
indicadores = {'Mont Belvieu'   : {'std_unit':'gal',    'PCI':91330,    'abrev':'mont'},
               'Brent'          : {'std_unit':'barrel', 'PCI':5800000,'abrev':'brent'},
               'WTI'            : {'std_unit':'barrel', 'PCI':5800000,  'abrev':'wti'},
               'Henry Hub'      : {'std_unit':'MMBtu', 'PCI':1e6,         'abrev':'hhub'},
               'GLP ENAP'       : {'std_unit':'ton',    'PCI':12956008,        'abrev':'glp'},
               'DSL ENAP'       : {'std_unit':'m3',     'PCI':35960000,        'abrev':'dsl'}}

periodos = {'Diario':'D',
            'Semanal':'W',
            'Mensual':'M',
            'Anual':'A'}

tipos = {'USD/unidad std':'std_unit',
         'USD/MMBtu':'MMBtu',
         'Normalizado':'norm',
         'Tasa crecimiento':'perc'}


def RandomWalk(df,indice,anho):
    # Definir número de semanas
    tot_proy = anho*52
    # Convertir Dataframe a archivo semanal
    df_new = EnerConv(df,indice,'Semanal')
    # Calcular el cambio porcentual en el tiempo del precio del combustible
    df_new['returns'] = df_new.std_unit.pct_change()
    # Eliminar primer valor de returns ( es NaN)
    sample = df_new.returns.dropna()
    # Contar la cantidad de datos disponibles
    n_obs = df_new.returns.count()
    
    # Definir n_eval (número de evaluaciones), según el menor valor entre n_obs y tot_proy
    if n_obs > tot_proy:
        n_eval = tot_proy
    
    else:
        n_eval=n_obs
    
    # Calcular los valores random
    rnd_walk = np.random.choice(sample,n_eval)
    # Crear pd.Series con los datos del random walk y el índice de sample (valores pasados, todavía sin proyección)
    random_walk = pd.Series(rnd_walk[0:n_eval], index=sample.index[0:n_eval])
    # Tomar el primer precio 
    start = df_new.std_unit.first('D')
    # juntar el primer precio con el random walk, sumando 1
    ind_random = start.append(random_walk.add(1))
    # 
    df_new['rnd'] = ind_random.cumprod()
    
    start_proy = df_new.std_unit.last('D')
    ind_proy = pd.date_range(start_proy.index[0]+pd.Timedelta('1W'),freq='W',periods=n_eval, name='Date')
    random_walk = pd.Series(rnd_walk, index=ind_proy)
    proy_random = start_proy.append(random_walk.add(1))
    proy_walk = proy_random.cumprod()    
    df_tmp = pd.concat([df_new,proy_walk])
    df_tmp = df_tmp.rename(columns={0:'proy'})
    
    
    while ( (df_new.rnd.max() > 1.4*df_new.std_unit.max()) | (df_new.rnd.min() < 0.6*df_new.std_unit.min()) ):
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
        
    
    return df_tmp


def ProyMonth(df,pry,indice,lcoh,indSol,anho_contr,anho_proy,effHeater,factInd,inicSolar = 2022):
    #
    
    df_month = df.resample('M').mean()
    df_month = df_month[df_month.index.year > 2020]
    
    df_month['month'] = df_month.index.month
    df_month['year'] = df_month.index.year
    
    precSol = VectorAnual(lcoh,anho_contr,indSol,2021)
    prSol = dict(precSol)
    
    if pry == 'gen':
        header = ['n','monthProc','monthSol','SF']
        df_sol = pd.read_csv(path + 'visualizaciones/swh_calc/balance_mensual.csv',sep=',',names=header,nrows=12,index_col='n',skiprows=1)
        enerProc = dict(df_sol.monthProc)
        enerSol = dict(df_sol.monthSol)
        
    else:
        
        ar = np.arange(1,13,1)
        proc = prys[pry]['enerProc']
        enerProc = dict(zip(ar,proc))
        sol = prys[pry]['enerSol']
        enerSol = dict(zip(ar,sol))
    
    
    df_month['precioSol'] = df_month.year.map(prSol).fillna(0)
    df_month['enerProc'] = df_month.month.map(enerProc)
    df_month['enerSol'] = df_month.month.map(enerSol)
    
    finSolar = inicSolar + anho_contr
#    finEval = inicSolar + anho_proy
    
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
    table_proy2['Ahorro (kUS$): '] = "{:10.1f}".format(df_month.convPay.sum() - df_month.totPay.sum())
    
    return df_month, table_proy2


def EnerConv(df,indice,periodo):
    df_c = df.resample(periodos[periodo]).mean()
    df_c['MMBtu'] = df_c.std_unit * 1e6 / indicadores[indice]['PCI']
    df_c['MWh'] =df_c.MMBtu * 3.412
    
    df_c['shifted'] = df_c.std_unit.shift(periods=1)
    df_c['perc'] = 100 - df_c.std_unit / df_c.shifted*100
    df_c['norm'] = df_c.std_unit / df_c.std_unit.iloc[0]*100
    
    return df_c


def EnerConvProy(df,indice,periodo,val):
    df_c = df.resample(periodos[periodo]).mean()
    df_c['MMBtu_proy'] = df_c[val] * 1e6 / indicadores[indice]['PCI']
    df_c['MWh_proy'] =df_c.MMBtu_proy * 3.412
        
    return df_c

def VectorAnual(val,contrato,index,anhoInic):
    n = contrato+1
    vct = np.zeros(n) #.reshape(n,1)
    anhos = np.arange(1,n)
    for anho in anhos:
        if anho == 1:
            vct[anho] = val
        else:
            vct[anho] = vct[anho-1]*(1+index/100)
            
    ind = np.arange(anhoInic,anhoInic+contrato+1,1)
    res = pd.Series(vct,index=ind)
        
    return res


def MonteCarlo(df,pry,indice,lcoh,indSol,anho_contr,anho_proy,effHeater,factInd,N_iter = 2, inicSolar = 2022):
    tot_periods = anho_contr*12
    rng = pd.date_range('2022',periods=tot_periods,freq='M')
    
    df_month = pd.DataFrame(index=rng)
    
    df_month['month'] = df_month.index.month
    df_month['year'] = df_month.index.year
    
    precSol = VectorAnual(lcoh,anho_contr,indSol,2021)
    prSol = dict(precSol)
    
    ar = np.arange(1,13,1)
    proc = prys[pry]['enerProc']
    enerProc = dict(zip(ar,proc))
    sol = prys[pry]['enerSol']
    enerSol = dict(zip(ar,sol))
    
    df_month['precioSol'] = df_month.year.map(prSol).fillna(0)
    
    df_month['enerProc'] = df_month.month.map(enerProc)
    df_month['enerSol'] = df_month.month.map(enerSol)
    
    finSolar = inicSolar + anho_contr
#    finEval = inicSolar + anho_proy
    
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
        
        ahr_tmp = df_month.convPay.sum() - df_month.totPay.sum()
        ahr.append(ahr_tmp)
    
    return ahr


import multiprocessing
from joblib import Parallel, delayed

def MonteCarloParallel(df,pry,indice,lcoh,indSol,anho_contr,anho_proy,effHeater,factInd,N_iter = 2, inicSolar = 2022):
    tot_periods = anho_contr*12
    rng = pd.date_range('2022',periods=tot_periods,freq='M')
    
    df_month = pd.DataFrame(index=rng)
    
    df_month['month'] = df_month.index.month
    df_month['year'] = df_month.index.year
    
    precSol = VectorAnual(lcoh,anho_contr,indSol,2021)
    prSol = dict(precSol)
    
    if pry == 0:
        header = ['n','monthProc','monthSol','SF']
        df_sol = pd.read_csv(path + 'visualizaciones/swh_calc/balance_mensual.csv',sep=',',names=header,nrows=12,index_col='n',skiprows=1)
        
        enerProc = dict(df_sol.monthProc)
        enerSol = dict(df_sol.monthSol)
        
    else:
        
        ar = np.arange(1,13,1)
        proc = prys[pry]['enerProc']
        enerProc = dict(zip(ar,proc))
        sol = prys[pry]['enerSol']
        enerSol = dict(zip(ar,sol))
    
    df_month['precioSol'] = df_month.year.map(prSol).fillna(0)
    
    df_month['enerProc'] = df_month.month.map(enerProc)
    df_month['enerSol'] = df_month.month.map(enerSol)
    
    finSolar = inicSolar + anho_contr
#    finEval = inicSolar + anho_proy
    
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
    
    
    num_cores = multiprocessing.cpu_count()
    l_iter = list(np.arange(N_iter))
    # if __name__ == "__main__":
    ahr = Parallel(n_jobs=num_cores)(delayed(MC)(n,sample,n_eval,df_new,finSolar,df_month,factInd,indice,effHeater) for n in l_iter)
    
    return ahr


def MC(val,sample,n_eval,df_new,finSolar,df_month,factInd,indice,effHeater):

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
    
    ahr_tmp = df_month.convPay.sum() - df_month.totPay.sum()
    return ahr_tmp


def cdf(data):
    n = len(data)
    x = np.sort(data) # sort your data
    y = np.arange(1, n + 1) / n # calculate cumulative probability
    return x, y


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