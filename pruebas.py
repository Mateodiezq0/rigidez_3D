import numpy as np

# Suponiendo que ya tenés definidas estas clases:
from core.nodos import Nodo
from core.barra import Barra
from core.carga_puntual import CargaPuntual

# 1. Crear dos nodos para la barra (ejemplo sencillo)
nodo_i = Nodo(id=1, x=0, y=0, z=0)
nodo_j = Nodo(id=2, x=0, y=5, z=0)  # Barra de 5m en X

# 2. Crear la barra
barra = Barra(
    id=1, nodo_i=1, nodo_f=2, E=21000, I_x=1, I_y=1, I_z=1, G=8000, J=0.5,
    A=10, tita=0, nodo_i_obj=nodo_i, nodo_f_obj=nodo_j
)

# 3. Crear una carga puntual ubicada a 2m desde el nodo_i,
#    magnitud 10kN, dirigida a 45° respecto de X y 90° respecto de Y y Z (o sea, en el plano X-Y)
carga = CargaPuntual(id=1, x=0, y=2, z=0, q=10, alpha_x=90, alpha_y=30, alpha_z=-60)
# En este caso, apunta sobre el eje X global

# 4. Llamar al método de la barra para calcular las reacciones equivalentes locales
f_eq = barra.reacciones_carga_puntual(carga)

print("Vector de fuerzas nodales equivalentes (barra local):")
print("Nodo inicial i (DOF 0-5):", f_eq[:6])
print("Nodo final   j (DOF 6-11):", f_eq[6:])
print()
print("Desglose (Fuerza local):")
print(f"Axial N (Zlocal): {f_eq[2]:.2f}  /  {f_eq[8]:.2f}")
print(f"Cortante Xlocal:  {f_eq[0]:.2f}  /  {f_eq[6]:.2f}")
print(f"Cortante Ylocal:  {f_eq[1]:.2f}  /  {f_eq[7]:.2f}")
print(f"Momento Xlocal:   {f_eq[3]:.2f}  /  {f_eq[9]:.2f}")
print(f"Momento Ylocal:   {f_eq[4]:.2f}  /  {f_eq[10]:.2f}")
