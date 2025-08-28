import numpy as np
import pandas as pd

# Suponiendo que ya tenés definidas estas clases (y que todo funciona)
from core.nodos import Nodo
from core.barra import Barra
from core.carga_puntual import CargaPuntual
from core.carga_distribuida import CargaDistribuida
from core.estructura import Estructura

# 1. Crear nodos
nodo_i = Nodo(id=1, x=0, y=0, z=0, restricciones = [True,True,True,True,True,True])
nodo_j = Nodo(id=2, x=700, y=0, z=0, restricciones = [True,True,True,True,True,True])

# 2. Crear barras
barra1 = Barra(
    id=1, nodo_i=1, nodo_f=2, E=30000, I_y=100, I_z=100, G=10000, J=50,
    A=10, tita=0, nodo_i_obj=nodo_i, nodo_f_obj=nodo_j
)

barra2 = Barra(
    id=2, nodo_i=1, nodo_f=2, E=30000, I_y=100, I_z=100, G=10000, J=50,
    A=10, tita=0, nodo_i_obj=nodo_i, nodo_f_obj=nodo_j
)

cargaDist = CargaDistribuida(id=1, x=100, y=0, z=0, 
                                x_f=400, y_f=0, z_f=0, 
                                q=(-5.0), q_f=(-5.0), 
                                alpha_x=90, alpha_y=0, alpha_z=90)

cargaPunt = CargaPuntual(id=1, x=250, y=0, z=0, 
                                q=(-1500.0),
                                alpha_x=90, alpha_y=0, alpha_z=90)


print(cargaDist.reacciones_de_empotramiento(barra1))
print("------------------- XDXDXDXDXDXD -------------------")
print(cargaPunt.reacciones_de_empotramiento(barra2))