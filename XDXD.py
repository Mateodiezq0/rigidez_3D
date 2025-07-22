import numpy as np

# Suponiendo que ya tenés definidas estas clases:
from core.nodos import Nodo
from core.barra import Barra
from core.carga_puntual import CargaPuntual
from core.estructura import Estructura

# 1. Crear dos nodos para la barra (ejemplo sencillo)
nodo_i = Nodo(id=1, x=0, y=0, z=0)
nodo_j = Nodo(id=2, x=5, y=0, z=0)  # Barra de 5m en X
nodo_k = Nodo(id=3, x=10, y=0, z=0)  # Barra de 5m en X

# 2. Crear la barra
barra1 = Barra(
    id=1, nodo_i=1, nodo_f=2, E=21000, I_x=1, I_y=1, I_z=1, G=8000, J=0.5,
    A=10, tita=0, nodo_i_obj=nodo_i, nodo_f_obj=nodo_j
)

barra2 = Barra(
    id=2, nodo_i=2, nodo_f=3, E=21000, I_x=1, I_y=1, I_z=1, G=8000, J=0.5,
    A=10, tita=0, nodo_i_obj=nodo_j, nodo_f_obj=nodo_k
)

# 3. Crear una carga puntual ubicada a 2m desde el nodo_i,
#    magnitud 10kN, dirigida a lo largo de Z global
carga1 = CargaPuntual(id=1, x=2, y=0, z=0, q=(-10), alpha_x=90, alpha_y=0, alpha_z=90)
carga2 = CargaPuntual(id=2, x=7, y=0, z=0, q=(-10), alpha_x=90, alpha_y=0, alpha_z=90)
# Con estos ángulos, la fuerza va sobre eje Z global

barra1.añadirCarga(carga1)
barra2.añadirCarga(carga2)

estructura = Estructura()
estructura.agregar_barra(barra1)
estructura.agregar_barra(barra2)
estructura.agregar_nodo(nodo_i)
estructura.agregar_nodo(nodo_j)
estructura.agregar_nodo(nodo_k)
estructura.ensamble_cargas_equivalentes()

print()
print("========== LOCALES ==========")
print("Vector total local (barra 1):")
print(barra1.reaccion_total_local)
print("Nodo i (local):", barra1.reac_eq_i_local)
print("Nodo f (local):", barra1.reac_eq_f_local)
print()
print("Vector total local (barra 2):")
print(barra2.reaccion_total_local)
print("Nodo i (local):", barra2.reac_eq_i_local)
print("Nodo f (local):", barra2.reac_eq_f_local)
print()


print("========== GLOBALES ==========")
print("Vector total global (barra 1):")
print(barra1.reaccion_total_global)
print("Nodo i (global):", barra1.reac_eq_i_global)
print("Nodo f (global):", barra1.reac_eq_f_global)
print("Vector total global (barra 2):")
print(barra2.reaccion_total_global)
print("Nodo i (global):", barra2.reac_eq_i_global)
print("Nodo f (global):", barra2.reac_eq_f_global)
print()
print("========== GLOBALES ==========")
print(estructura.vector_nodal_equivalente)