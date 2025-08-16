import numpy as np
import pandas as pd

# Suponiendo que ya tenés definidas estas clases (y que todo funciona)
from core.nodos import Nodo
from core.barra import Barra
from core.carga_puntual import CargaPuntual
from core.estructura import Estructura

# 1. Crear nodos
nodo_i = Nodo(id=1, x=100, y=0, z=0, restricciones = [True,True,True,True,True,True]) #Nudo 1
nodo_j = Nodo(id=2, x=0, y=0, z=0, restricciones = [True,True,True,True,True,True]) #Nudo 2
nodo_k = Nodo(id=3, x=100, y=0, z=-100, restricciones = [True,True,True,True,True,True]) #Nudo 3
nodo_l = Nodo(id=4, x=100, y=-100, z=0, restricciones = [True,True,True,True,True,True]) #Nudo 4

# 2. Crear barras
barra1 = Barra(
    id=1, nodo_i=2, nodo_f=1, E=30000, I_y=100, I_z=100, G=10000, J=50,
    A=10 , tita=0, nodo_i_obj=nodo_j, nodo_f_obj=nodo_i
)
barra2 = Barra(
    id=2, nodo_i=3, nodo_f=1, E=30000, I_y=100, I_z=100, G=10000, J=50,
    A=10 , tita=0, nodo_i_obj=nodo_k, nodo_f_obj=nodo_i
)
barra3 = Barra(
    id=3, nodo_i=4, nodo_f=1, E=30000, I_y=100, I_z=100, G=10000, J=50,
    A=10 , tita=0, nodo_i_obj=nodo_l, nodo_f_obj=nodo_i
)

# 3. Crear cargas
carga1 = CargaPuntual(id=1, x=0, y=0, z=3, q=(7.07), alpha_x=-45, alpha_y=90, alpha_z=45)
carga2 = CargaPuntual(id=2, x=2, y=0, z=5, q=(-10), alpha_x=-60, alpha_y=90, alpha_z=30)
carga3 = CargaPuntual(id=3, x=5, y=0, z=5, q=(-8), alpha_x=-90, alpha_y=90, alpha_z=0)
carga4 = CargaPuntual(id=4, x=9, y=0, z=5, q=(10), alpha_x=-60, alpha_y=90, alpha_z=30)
carga5 = CargaPuntual(id=5, x=10, y=0, z=1, q=(7.07), alpha_x=-45, alpha_y=90, alpha_z=45)


barra1.añadirCarga(carga1)


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
XD1 = barra1.k_eje()
XD2 = barra1.k_altura()
K1loc = barra1.KlocXD()
K1 = barra1.Kglobal()
k2loc = barra2.KlocXD()
XD3 = barra2.k_eje()
XD4 = barra2.k_altura()
K2 = barra2.Kglobal()
K3 = barra3.Kglobal()
#K2 = barra2.matriz_rigidez_portico_3d()
K_global = estructura.ensamble_matriz_global()
F = estructura.ensamble_vector_cargas_nodales_equivalentes()
D = estructura.resolver_desplazamientos()
R = estructura.calcular_reacciones()

# 6 cargas  

#barra1.reacciones_de_empotramiento_carga_puntual(carga1)
#barra2.reacciones_de_empotramiento_carga_puntual(carga2)
#barra2.reacciones_de_empotramiento_carga_puntual(carga3)
#barra2.reacciones_de_empotramiento_carga_puntual(carga4)
#barra3.reacciones_de_empotramiento_carga_puntual(carga5)
#barra1.p_eje()
#barra1.p_base()
#barra1.p_global()
#barra2.p_eje()
#barra2.p_base()
#barra2.p_global()
#barra3.p_eje()
#barra3.p_base()
#barra3.p_global()
#barra1.debug_bases()
#barra2.debug_bases()
#barra3.debug_bases()


# 7. Exportar a Excel (cada una en su hoja)
with pd.ExcelWriter("matrices_rigidez_3D.xlsx") as writer:
    pd.DataFrame(K1loc).to_excel(writer, sheet_name="Barra 1 (K1local)", index=False, header=False)
    pd.DataFrame(XD1).to_excel(writer, sheet_name="K1 (K_eje)", index=False, header=False)
    pd.DataFrame(XD2).to_excel(writer, sheet_name="K1 (K_altura)", index=False, header=False)
    pd.DataFrame(K1).to_excel(writer, sheet_name="Barra 1 (K1)", index=False, header=False)
    pd.DataFrame(XD3).to_excel(writer, sheet_name="K2 (K_eje)", index=False, header=False)
    pd.DataFrame(XD4).to_excel(writer, sheet_name="K2 (K_altura)", index=False, header=False)
    pd.DataFrame(k2loc).to_excel(writer, sheet_name="Barra 2 (K2local)", index=False, header=False)
    pd.DataFrame(K2).to_excel(writer, sheet_name="Barra 2 (K2)", index=False, header=False)
    pd.DataFrame(K3).to_excel(writer, sheet_name="Barra 3 (K3)", index=False, header=False)
    pd.DataFrame(K_global).to_excel(writer, sheet_name="Global", index=False, header=False)
    pd.DataFrame(F).to_excel(writer, sheet_name="F", index=False, header=False)
    pd.DataFrame(D).to_excel(writer, sheet_name="Desplazamientos", index=False, header=False)
    pd.DataFrame(R).to_excel(writer, sheet_name="Reacciones", index=False, header=False)
print("Matrices exportadas en 'matrices_rigidez_3D.xlsx' 🎉🚀")
