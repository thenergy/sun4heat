#!/bin/bash

LAUNCH_SCRIPTS_ROUTE=/home/programaenergias/visualizaciones/revision/viz_test/launch_scripts/;
pm2 start --name mapa_dev $LAUNCH_SCRIPTS_ROUTE/mapa_dev.sh
pm2 start --name est_DMC_dev $LAUNCH_SCRIPTS_ROUTE/est_DMC_dev.sh
pm2 start --name est_soiling_dev $LAUNCH_SCRIPTS_ROUTE/est_soiling_dev.sh
pm2 start --name perf_ratioDTS_dev $LAUNCH_SCRIPTS_ROUTE/perf_ratioDA_dev.sh
pm2 start --name recursoSolarDTS_dev $LAUNCH_SCRIPTS_ROUTE/recursoSolarDA_dev.sh
pm2 start --name soilingDTS_dev $LAUNCH_SCRIPTS_ROUTE/soilingDA_dev.sh
pm2 start --name dash $LAUNCH_SCRIPTS_ROUTE/dash.sh
pm2 start --name dash_gen_tec $LAUNCH_SCRIPTS_ROUTE/dash_gen_tec.sh
pm2 start --name dash_plantas_chile $LAUNCH_SCRIPTS_ROUTE/dash_plantas_chile.sh
pm2 start --name eclipse2019 $LAUNCH_SCRIPTS_ROUTE/eclipse2019.sh
