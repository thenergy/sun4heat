#!/bin/bash

CONDA_BASE=$(conda info --base)
#source $CONDA_BASE/etc/profile.d/conda.sh

#conda activate bokeh2
cd /home/ubuntu/Thenergy/diego/sun4heat/visualizaciones
bokeh serve swh_calc --port 5014 --allow-websocket-origin=18.216.118.176:5014 &
#bokeh serve swh_calc --port 5611 --show
#bokeh serve swh_calc --allow-websocket-origin=18.222.135.159:5511 &