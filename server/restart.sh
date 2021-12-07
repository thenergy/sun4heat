#!/bin/bash

pm2 restart mapa_emisiones
#pm2 restart eval_proy
pm2 restart ind_ener
pm2 restart swh_calc

#pm2 restart mapa_dev 
#pm2 restart est_DMC_dev
#pm2 restart est_soiling_dev
#pm2 restart perf_ratioDTS_dev
#pm2 restart recursoSolarDTS_dev
#pm2 restart soilingDTS_dev
#pm2 restart dash
#pm2 restart dash_gen_tec
#pm2 restart dash_plantas_chile
#pm2 restart eclipse2019