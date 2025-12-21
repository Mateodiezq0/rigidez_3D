import numpy as np
import pandas as pd

# Suponiendo que ya tenés definidas estas clases (y que todo funciona)
from core.nodos import Nodo
from core.carga_nodal import CargaNodal
from core.barra import Barra
from core.carga_puntual import CargaPuntual
from core.carga_distribuida import CargaDistribuida
from core.estructura import Estructura

# 1. Crear nodos
#Base
nodo_i = Nodo(id=1, x=0, y=0, z=0, restricciones = [True,True,True,False,False,False]) #Ruedita
nodo_j = Nodo(id=2, x=300, y=0, z=0, restricciones = [True,True,True,True,True,True]) #Empotramiento

#Top
nodo_m = Nodo(id=3, x=0, y=300, z=0, restricciones = [None,None,None,None,None,None])
nodo_n = Nodo(id=4, x=300, y=300, z=0, restricciones = [None,None,None,None,None,None])
nodo_o = Nodo(id=5, x=300, y=300, z=600, restricciones = [True,True,True,True,True,True]) #Empotramiento 


elexd=2100
elgxd=807.7
eljd=1408.33
elaxd=100
eli_zd=833.33
eli_yd=833.33

# 2. Crear barras
#Verticales
barra1 = Barra(
    id=1, nodo_i=1, nodo_f=3, E=elexd, I_y=eli_yd, I_z=eli_zd, G=elgxd, J=eljd,
    A=elaxd, tita=0, nodo_i_obj=nodo_i, nodo_f_obj=nodo_m
)

barra2 = Barra(
    id=2, nodo_i=2, nodo_f=4, E=elexd, I_y=eli_yd, I_z=eli_zd, G=elgxd, J=eljd,
    A=elaxd, tita=0, nodo_i_obj=nodo_j, nodo_f_obj=nodo_n
)

barra3 = Barra(
    id=3, nodo_i=3, nodo_f=4, E=elexd, I_y=eli_yd, I_z=eli_zd, G=elgxd, J=eljd,
    A=elaxd, tita=0, nodo_i_obj=nodo_m, nodo_f_obj=nodo_n
)
barra4 = Barra(
    id=4, nodo_i=4, nodo_f=5, E=elexd, I_y=eli_yd, I_z=eli_zd, G=elgxd, J=eljd,
    A=elaxd, tita=0, nodo_i_obj=nodo_n, nodo_f_obj=nodo_o
)


# 3. Crear cargas
#carga2 = CargaDistribuida(id=2, x=300, y=300, z=0, q=(-5), x_f = 300 ,y_f = 300 , z_f = 600 , q_f=(-5), alpha_x=90, alpha_y=0, alpha_z=90)   #CARGAS EN TONELADAS
#carga2 = CargaNodal(nodo_id=7, fx=10, fy=10, fz=0, mx=0, my=0, mz=0) 
#carga2  = CargaPuntual(id=2, x=150, y=300, z=0, q=(-10), alpha_x=90, alpha_y=0, alpha_z=90)
carga1  = CargaPuntual(id=1, x=150, y=300, z=0, q=(-10), alpha_x=90, alpha_y=0, alpha_z=90)
carga2  = CargaPuntual(id=2, x=300, y=150, z=0, q=(10), alpha_x=90, alpha_y=90, alpha_z=0)
carga3  = CargaPuntual(id=3, x=300, y=300, z=300, q=(-20), alpha_x=90, alpha_y=0, alpha_z=90)
carga4  = CargaPuntual(id=4, x=300, y=300, z=300, q=(-20), alpha_x=0, alpha_y=90, alpha_z=90)

# 4. Crear estructura
estructura = Estructura()
estructura.agregar_barra(barra1)
estructura.agregar_barra(barra2)
estructura.agregar_barra(barra3)
estructura.agregar_barra(barra4)

estructura.agregar_nodo(nodo_i)
estructura.agregar_nodo(nodo_j)
estructura.agregar_nodo(nodo_m)
estructura.agregar_nodo(nodo_n)
estructura.agregar_nodo(nodo_o)

barra2.añadirCarga(carga2)
barra3.añadirCarga(carga1)
barra4.añadirCarga(carga3)
barra4.añadirCarga(carga4)


#barra4.añadirCarga(carga2)
# 5. Calcular matrices

K1loc = barra1.Kloc()
K2loc = barra2.Kloc()
K3loc = barra3.Kloc()


K1 = barra1.Kglobal()
K2 = barra2.Kglobal()
K3 = barra3.Kglobal()


#K3 = barra3.Kglobal()
K_global = estructura.ensamble_matriz_global()
F = estructura.ensamble_vector_cargas_nodales_equivalentes()
D = estructura.resolver_desplazamientos()
R = estructura.calcular_reacciones()
R_loc = estructura.calcular_reacciones_locales()
# 6 cargas  


#barra1.debug_bases()
#barra2.debug_bases()
#barra3.debug_bases()

#



# 7. Exportar a Excel (cada una en su hoja)
with pd.ExcelWriter("matrices_rigidez_3D.xlsx") as writer:
    pd.DataFrame(K1loc).to_excel(writer, sheet_name="Barra 1 (K1local)", index=False, header=False)
    pd.DataFrame(K2loc).to_excel(writer, sheet_name="Barra 2 (K2local)", index=False, header=False)
    #pd.DataFrame(K3loc).to_excel(writer, sheet_name="Barra 3 (K3local)", index=False, header=False)
    pd.DataFrame(K1).to_excel(writer, sheet_name="Barra 1 (K1)", index=False, header=False)
    pd.DataFrame(K2).to_excel(writer, sheet_name="Barra 2 (K2)", index=False, header=False)
    #pd.DataFrame(K3).to_excel(writer, sheet_name="Barra 3 (K3)", index=False, header=False)
    pd.DataFrame(K_global).to_excel(writer, sheet_name="Global", index=False, header=False)
    pd.DataFrame(F).to_excel(writer, sheet_name="F_nodal_equivalente", index=False, header=False)
    pd.DataFrame(D).to_excel(writer, sheet_name="Desplazamientos", index=False, header=False)
    pd.DataFrame(R).to_excel(writer, sheet_name="Reacciones", index=False, header=False)
    pd.DataFrame(R_loc).to_excel(writer, sheet_name="Reacciones locales", index=False, header=False)
print("Matrices exportadas en 'matrices_rigidez_3D.xlsx'")
