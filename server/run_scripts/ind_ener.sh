#!/bin/bash

CONDA_BASE=$(conda info --base)
#source $CONDA_BASE/etc/profile.d/conda.sh

#conda activate bokeh2
cd /home/ubuntu/Thenergy/diego/sun4heat/visualizaciones
bokeh serve ind_ener --port 5013 --allow-websocket-origin=18.216.118.176:5013 &
#bokeh serve ind_ener --port 5612 --show
#bokeh serve ind_ener --allow-websocket-origin=18.222.135.159:5512 &
