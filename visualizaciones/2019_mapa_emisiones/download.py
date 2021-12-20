''' A column salary chart with minimum and maximum values.
This example shows the capability of exporting a csv file from ColumnDataSource.

'''
import os
from os.path import dirname, join

import pandas as pd

from bokeh.io import curdoc, showing
from bokeh.layouts import column, row
from bokeh.models import (Button, ColumnDataSource, CustomJS, DataTable,
                          NumberFormatter, RangeSlider, TableColumn)

# os.chdir('/home/diegonaranjo/Documentos/Thenergy/sun4heat/visualizaciones/2019_mapa_emisiones')
# print(os.getcwd())
df = pd.read_csv(join(dirname(__file__), 'empresas_filtradas.csv'), error_bad_lines= False)


source = ColumnDataSource(data=df)

button = Button(label="Download", button_type="success")
button.js_on_click(CustomJS(args=dict(source=source),
                            code=open(join(dirname(__file__), "download.js")).read()))

# columns = [
#     TableColumn(field="ID", title="Employee Name"),
#     TableColumn(field="ton_emision", title="Income", formatter=NumberFormatter(format="$0,0.00")),
#     TableColumn(field="n_equip", title="Numero equipos"),
#     TableColumn(field="raz_social", title="Raiz social"),
#     TableColumn(field="nombre", title="Nombre"),
#     TableColumn(field="rubro", title="Rubro"),
#     TableColumn(field="ciiu4", title="ciiu4"),
#     TableColumn(field="region", title="Region"),
#     TableColumn(field="provincia", title="Provincia"),
#     TableColumn(field="comuna", title="Comuna"),
#     TableColumn(field="Max_emision", title="Maxima emisión en toneladas")

# ]

# data_table = DataTable(source=source, columns=columns, width=800)

# controls = column(button)

curdoc().add_root(row(button))
curdoc().title = "Export CSV"


