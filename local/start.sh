#!/bin/bash

LAUNCH_SCRIPTS_ROUTE=/home/diegonaranjo/Documentos/Thenergy/sun4heat/local/run_scripts;
pm2 start --name mapa_emisiones $LAUNCH_SCRIPTS_ROUTE/mapa_emisiones.sh
#pm2 start --name eval_proy $LAUNCH_SCRIPTS_ROUTE/eval_proy.sh
pm2 start --name ind_ener $LAUNCH_SCRIPTS_ROUTE/ind_ener.sh
pm2 start --name swh_calc $LAUNCH_SCRIPTS_ROUTE/swh_calc.sh
