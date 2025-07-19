import numpy as np

# Suponiendo que ya tenés definidas estas clases:
from core.nodos import Nodo
from core.barra import Barra
from core.carga_puntual import CargaPuntual

# 1. Crear dos nodos para la barra (ejemplo sencillo)
nodo_i = Nodo(id=1, x=0, y=0, z=0)
nodo_j = Nodo(id=2, x=5, y=0, z=0)  # Barra de 5m en X

# 2. Crear la barra
barra = Barra(
    id=1, nodo_i=1, nodo_f=2, E=21000, I_x=1, I_y=1, I_z=1, G=8000, J=0.5,
    A=10, tita=0, nodo_i_obj=nodo_i, nodo_f_obj=nodo_j
)

# 3. Crear una carga puntual ubicada a 2m desde el nodo_i,
#    magnitud 10kN, dirigida a lo largo de Z global
carga = CargaPuntual(id=1, x=2, y=0, z=0, q=(-10), alpha_x=90, alpha_y=0, alpha_z=90)
# Con estos ángulos, la fuerza va sobre eje Z global

# 4. Calcular las reacciones equivalentes locales
f_eq_local = barra.reacciones_carga_puntual(carga)

print("========== REACCIONES NODALES EQUIVALENTES EN LOCAL ==========")
print("Nodo inicial (i):")
print(f"  DOF 0 (Xlocal):  {f_eq_local[0]: .3f}")
print(f"  DOF 1 (Ylocal):  {f_eq_local[1]: .3f}")
print(f"  DOF 2 (Zlocal):  {f_eq_local[2]: .3f}  <- Axial")
print(f"  DOF 3 (M_xlocal):{f_eq_local[3]: .3f}")
print(f"  DOF 4 (M_ylocal):{f_eq_local[4]: .3f}")
print(f"  DOF 5 (M_zlocal):{f_eq_local[5]: .3f}")

print("Nodo final (j):")
print(f"  DOF 6 (Xlocal):  {f_eq_local[6]: .3f}")
print(f"  DOF 7 (Ylocal):  {f_eq_local[7]: .3f}")
print(f"  DOF 8 (Zlocal):  {f_eq_local[8]: .3f}  <- Axial")
print(f"  DOF 9 (M_xlocal):{f_eq_local[9]: .3f}")
print(f"  DOF 10(M_ylocal):{f_eq_local[10]:.3f}")
print(f"  DOF 11(M_zlocal):{f_eq_local[11]:.3f}")

print("\nResumen fuerzas/momentos locales:")
print(f"Axial Zlocal:    Nodo i = {f_eq_local[2]: .3f}, Nodo j = {f_eq_local[8]: .3f}")
print(f"Cortante Xlocal: Nodo i = {f_eq_local[0]: .3f}, Nodo j = {f_eq_local[6]: .3f}")
print(f"Cortante Ylocal: Nodo i = {f_eq_local[1]: .3f}, Nodo j = {f_eq_local[7]: .3f}")
print(f"Momento Xlocal:  Nodo i = {f_eq_local[3]: .3f}, Nodo j = {f_eq_local[9]: .3f}")
print(f"Momento Ylocal:  Nodo i = {f_eq_local[4]: .3f}, Nodo j = {f_eq_local[10]:.3f}")
print(f"Momento Zlocal:  Nodo i = {f_eq_local[5]: .3f}, Nodo j = {f_eq_local[11]:.3f}")

print("\n---------------------------------------------------------------")
# 5. Calcular las reacciones equivalentes en global
f_eq_global = barra.reacciones_carga_puntual_global(carga)

print("========== REACCIONES NODALES EQUIVALENTES EN GLOBAL ==========")
print("Nodo inicial (i):")
print(f"  DOF 0 (Xglobal):  {f_eq_global[0]: .3f}")
print(f"  DOF 1 (Yglobal):  {f_eq_global[1]: .3f}")
print(f"  DOF 2 (Zglobal):  {f_eq_global[2]: .3f}")
print(f"  DOF 3 (M_xglobal):{f_eq_global[3]: .3f}")
print(f"  DOF 4 (M_yglobal):{f_eq_global[4]: .3f}")
print(f"  DOF 5 (M_zglobal):{f_eq_global[5]: .3f}")

print("Nodo final (j):")
print(f"  DOF 6 (Xglobal):  {f_eq_global[6]: .3f}")
print(f"  DOF 7 (Yglobal):  {f_eq_global[7]: .3f}")
print(f"  DOF 8 (Zglobal):  {f_eq_global[8]: .3f}")
print(f"  DOF 9 (M_xglobal):{f_eq_global[9]: .3f}")
print(f"  DOF 10(M_yglobal):{f_eq_global[10]:.3f}")
print(f"  DOF 11(M_zglobal):{f_eq_global[11]:.3f}")

print("\nResumen fuerzas/momentos globales:")
print(f"Axial Zglobal:    Nodo i = {f_eq_global[2]: .3f}, Nodo j = {f_eq_global[8]: .3f}")
print(f"Cortante Xglobal: Nodo i = {f_eq_global[0]: .3f}, Nodo j = {f_eq_global[6]: .3f}")
print(f"Cortante Yglobal: Nodo i = {f_eq_global[1]: .3f}, Nodo j = {f_eq_global[7]: .3f}")
print(f"Momento Xglobal:  Nodo i = {f_eq_global[3]: .3f}, Nodo j = {f_eq_global[9]: .3f}")
print(f"Momento Yglobal:  Nodo i = {f_eq_global[4]: .3f}, Nodo j = {f_eq_global[10]:.3f}")
print(f"Momento Zglobal:  Nodo i = {f_eq_global[5]: .3f}, Nodo j = {f_eq_global[11]:.3f}")
