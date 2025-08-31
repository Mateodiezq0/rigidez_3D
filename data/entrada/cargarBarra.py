import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from core.barra import Barra  # tu clase Barra
import pandas as pd

# Leer el Excel, tomando la segunda fila como encabezado
ruta_excel = os.path.join(os.path.dirname(__file__), '..', 'Datos_template.xlsx')
df_barras = pd.read_excel(ruta_excel, sheet_name="Barra", header=1)

barras = []
def leer_barras():
    for idx, row in df_barras.iterrows():
        barra = Barra(
            id       = int(row.iloc[0]),   # id_Barra
            nodo_i   = int(row.iloc[1]),   # Id_Nodo_in
            nodo_f   = int(row.iloc[2]),   # Id_Nodo_fin
            E        = float(row.iloc[3]), # E
            A        = float(row.iloc[4]), # A
            I_y      = float(row.iloc[5]), # Inercia en X
            I_z      = float(row.iloc[6]), # Inercia en Y
            G        = float(row.iloc[7]), # G
            J        = float(row.iloc[8]), # J
            tita     = float(row.iloc[9])  # Tita
        )
        barras.append(barra)

    return barras

def unir_barras_nodos(barras,nodos):
    for barra in barras:
        print(barra.nodo_i)
        for nodo in nodos:
            print(nodo.id)
            if barra.nodo_i == nodo.id:
                barra.nodo_i_obj = nodo
            elif barra.nodo_f == nodo.id:
                barra.nodo_f_obj = nodo 
                 
