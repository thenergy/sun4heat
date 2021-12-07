#!/bin/bash

pm2 delete mapa_emisiones
#pm2 delete eval_proy
pm2 delete ind_ener
pm2 delete swh_calc

#pm2 delete mapa_dev 
#pm2 delete est_DMC_dev
#pm2 delete est_soiling_dev
#pm2 delete perf_ratioDTS_dev
#pm2 delete recursoSolarDTS_dev
#pm2 delete soilingDTS_dev
#pm2 delete dash
#pm2 delete dash_gen_tec
#pm2 delete dash_plantas_chile
#pm2 delete eclipse2019