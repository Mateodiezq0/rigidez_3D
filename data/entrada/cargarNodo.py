import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from core.nodos import Nodo
import pandas as pd

# Leer el Excel, tomando la segunda fila como encabezado
ruta_excel = os.path.join(os.path.dirname(__file__), '..', 'Datos_template.xlsx')
df = pd.read_excel(ruta_excel, sheet_name="Nodo", header=1)

restric_cols = ['Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz']
valores_cols = ['Dx', 'Dy', 'Dz', 'Tita_x', 'Tita_y', 'Tita_z']

nodos = []

for idx, row in df.iterrows():
    print(row)
    nodo = Nodo(
        id = int(row['id_Nodo']),
        x = float(row['x_global']),
        y = float(row['y_global']),
        z = float(row['z_global']),
        restricciones = [str(row[c]).strip().upper() == ("VERDADERO" or 1) for c in restric_cols],
        valores_prescritos = [float(row[c]) for c in valores_cols]
    )
    nodos.append(nodo)

print(nodos)
