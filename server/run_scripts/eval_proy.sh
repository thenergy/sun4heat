#!/bin/bash

#source activate bokeh2
cd /home/ubuntu/Thenergy/diego/sun4heat/visualizaciones
#bokeh serve eval_proy --port 5510 --allow-websocket-origin=18.222.135.159:5510 &
#bokeh serve eval_proy --port 5610 --show
bokeh serve eval_proy --allow-websocket-origin=18.222.135.159:5510 &