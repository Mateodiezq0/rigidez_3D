import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from core.carga_puntual import CargaPuntual  # tu clase carga
import pandas as pd

# Leer el Excel, tomando la segunda fila como encabezado
ruta_excel = os.path.join(os.path.dirname(__file__), '..', 'Datos_template.xlsx')
df_cargas = pd.read_excel(ruta_excel, sheet_name="Carga Puntual",header=1)


cargas = []
def leer_cargas():
    for idx, row in df_cargas.iterrows():
        carga = CargaPuntual(
            id = int(row.iloc[0]),   # id_BarraW
            x        = float(row.iloc[1]), # x_global
            y        = float(row.iloc[2]), # y_global
            z        = float(row.iloc[3]), # z_global
            q        = float(row.iloc[4]), # q
            alpha_x  = float(row.iloc[5]), # alpha_x
            alpha_y  = float(row.iloc[6]), # alpha_y
            alpha_z  = float(row.iloc[7])  # alpha_z
        )
        cargas.append(carga)

    return cargas

