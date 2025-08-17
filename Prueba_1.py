import numpy as np
import pandas as pd

# Suponiendo que ya tenés definidas estas clases (y que todo funciona)
from core.nodos import Nodo
from core.barra import Barra
from core.carga_puntual import CargaPuntual
from core.estructura import Estructura

# 1. Crear nodos
nodo_i = Nodo(id=1, x=0, y=0, z=0, restricciones = [True,True,True,True,True,True])
nodo_j = Nodo(id=2, x=0, y=5, z=0, restricciones = [None, None, None, None, None, None])
nodo_k = Nodo(id=3, x=10, y=5, z=0, restricciones = [None, None, None, None, None, None])
nodo_l = Nodo(id=4, x=10, y=0, z=0, restricciones = [True,True,True,True,True,True])

# 2. Crear barras
barra1 = Barra(
    id=1, nodo_i=1, nodo_f=2, E=10, I_y=10, I_z=10, G=80.77, J=2,
    A=1, tita=0, nodo_i_obj=nodo_i, nodo_f_obj=nodo_j
)
barra2 = Barra(
    id=2, nodo_i=2, nodo_f=3, E=10, I_y=10, I_z=10, G=80.77, J=2,
    A=1, tita=0, nodo_i_obj=nodo_j, nodo_f_obj=nodo_k
)
barra3 = Barra(
    id=3, nodo_i=3, nodo_f=4, E=10, I_y=10, I_z=10, G=80.77, J=2,
    A=1, tita=0, nodo_i_obj=nodo_k, nodo_f_obj=nodo_l
)

# 3. Crear cargas
carga1 = CargaPuntual(id=1, x=0, y=3, z=0, q=(7.07), alpha_x=45, alpha_y=-45, alpha_z=90)
carga2 = CargaPuntual(id=2, x=2, y=5, z=0, q=(-10), alpha_x=60, alpha_y=-30, alpha_z=90)
carga3 = CargaPuntual(id=3, x=5, y=5, z=0, q=(-8), alpha_x=90, alpha_y=0, alpha_z=90)
carga4 = CargaPuntual(id=4, x=9, y=5, z=0, q=(10), alpha_x=60, alpha_y=-30, alpha_z=90)
carga5 = CargaPuntual(id=5, x=10, y=1, z=0, q=(7.07), alpha_x=45, alpha_y=-45, alpha_z=90)


barra1.añadirCarga(carga1)
barra2.añadirCarga(carga2)
barra2.añadirCarga(carga3)
barra2.añadirCarga(carga4)
barra3.añadirCarga(carga5)

# 4. Crear estructura
estructura = Estructura()
estructura.agregar_barra(barra1)
estructura.agregar_barra(barra2)
estructura.agregar_barra(barra3)
estructura.agregar_nodo(nodo_i)
estructura.agregar_nodo(nodo_j)
estructura.agregar_nodo(nodo_k)
estructura.agregar_nodo(nodo_l)

# 5. Calcular matrices

K1loc = barra1.KlocXD()
K1 = barra1.Kglobal()
K_global = estructura.ensamble_matriz_global()
F = estructura.ensamble_vector_cargas_nodales_equivalentes()
D = estructura.resolver_desplazamientos(1)
R = estructura.calcular_reacciones(1)

# 6 cargas  


#barra1.debug_bases()
#barra2.debug_bases()
#barra3.debug_bases()

#



# 7. Exportar a Excel (cada una en su hoja)
with pd.ExcelWriter("matrices_rigidez_3D.xlsx") as writer:
    pd.DataFrame(K1loc).to_excel(writer, sheet_name="Barra 1 (K1local)", index=False, header=False)
    pd.DataFrame(K1).to_excel(writer, sheet_name="Barra 1 (K1)", index=False, header=False)
    pd.DataFrame(K_global).to_excel(writer, sheet_name="Global", index=False, header=False)
    pd.DataFrame(F).to_excel(writer, sheet_name="F", index=False, header=False)
    pd.DataFrame(D).to_excel(writer, sheet_name="Desplazamientos", index=False, header=False)
    pd.DataFrame(R).to_excel(writer, sheet_name="Reacciones", index=False, header=False)
print("Matrices exportadas en 'matrices_rigidez_3D.xlsx'")
