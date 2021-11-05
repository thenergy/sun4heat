#!/bin/bash

CONDA_BASE=$(conda info --base)
source $CONDA_BASE/etc/profile.d/conda.sh

conda activate bokeh2
cd /Users/fcuevas/Documents/Trabajo/thenergy/sun4heat/visualizaciones
bokeh serve mapa_emisiones --port 5509