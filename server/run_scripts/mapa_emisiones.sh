#!/bin/bash

#CONDA_BASE=$(conda info --base)
source /home/ubuntu/anaconda3/etc/profile.d/conda.sh

#conda activate bokeh2
cd /home/ubuntu/Thenergy/diego/sun4heat/visualizaciones
#bokeh serve mapa_emisiones --port 5509
bokeh serve 2019_mapa_emisiones --port 5333 --allow-websocket-origin=18.117.130.153:5333 &
#bokeh serve mapa_emisiones -- port 5609 --show
#bokeh serve mapa_emisiones --allow-websocket-origin=18.222.135.159:5509 &
