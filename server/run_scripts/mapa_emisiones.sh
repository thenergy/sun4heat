#!/bin/bash

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh

#conda activate bokeh2
cd /home/ubuntu/Thenergy/diego/sun4heat/visualizaciones
#bokeh serve mapa_emisiones --port 5509
bokeh serve mapa_emisiones --port 5012 --allow-websocket-origin=18.216.118.176:5012 &
#bokeh serve mapa_emisiones -- port 5609 --show
#bokeh serve mapa_emisiones --allow-websocket-origin=18.222.135.159:5509 &