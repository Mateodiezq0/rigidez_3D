import numpy as np
import pandas as pd

# Suponiendo que ya tenés definidas estas clases (y que todo funciona)
from core.nodos import Nodo
from core.barra import Barra
from core.carga_puntual import CargaPuntual
from core.estructura import Estructura

# 1. Crear nodos
nodo_i = Nodo(id=1, x=0, y=0, z=0, restricciones = [True,True,True,True,True,True])
nodo_j = Nodo(id=2, x=5, y=0, z=0)
nodo_k = Nodo(id=3, x=10, y=0, z=0, restricciones = [True,True,True,True,True,True])

# 2. Crear barras
barra1 = Barra(
    id=1, nodo_i=1, nodo_f=2, E=21000, I_x= 0.0833, I_y=0.0833, I_z=0.166, G=8000, J=0.5,
    A=1, tita=0, nodo_i_obj=nodo_i, nodo_f_obj=nodo_j
)
barra2 = Barra(
    id=2, nodo_i=2, nodo_f=3, E=21000, I_x=0.0833, I_y=0.0833, I_z=0.166, G=8000, J=0.5,
    A=1, tita=0, nodo_i_obj=nodo_j, nodo_f_obj=nodo_k
)

# 3. Crear cargas
carga1 = CargaPuntual(id=1, x=2, y=0, z=0, q=(-1000), alpha_x=90, alpha_y=90, alpha_z=0)
carga2 = CargaPuntual(id=2, x=7, y=0, z=0, q=(-1000), alpha_x=90, alpha_y=90, alpha_z=0)

barra1.añadirCarga(carga1)
barra2.añadirCarga(carga2)

# 4. Crear estructura
estructura = Estructura()
estructura.agregar_barra(barra1)
estructura.agregar_barra(barra2)
estructura.agregar_nodo(nodo_i)
estructura.agregar_nodo(nodo_j)
estructura.agregar_nodo(nodo_k)


# 5. Calcular matrices
r = barra1.matriz_r()
R = barra1.matriz_R()
K_loc = barra1.KlocXD()
K1 = barra1.matriz_rigidez_portico_3d()

# 6. Exportar a Excel (cada una en su hoja)
with pd.ExcelWriter("erres.xlsx") as writer:
    pd.DataFrame(r).to_excel(writer, sheet_name="r", index=False, header=False)
    pd.DataFrame(R).to_excel(writer, sheet_name="R", index=False, header=False)
    pd.DataFrame(K_loc).to_excel(writer, sheet_name="K_loc", index=False, header=False)
    pd.DataFrame(K1).to_excel(writer, sheet_name="K global", index=False, header=False)


