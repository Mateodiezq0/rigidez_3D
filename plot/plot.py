import sys
import os
import numpy as np
import pyvista as pv

# Asegurarse que se puede importar core.*
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.nodos import Nodo
from core.barra import Barra

# --- Crear nodos ---
#Base
nodo_i = Nodo(id=1, x=0, y=0, z=0, restricciones = [True,True,True,True,True,True]) #Empotramiento
nodo_j = Nodo(id=2, x=300, y=0, z=0, restricciones = [True,True,True,True,True,True]) #Empotramiento
nodo_k = Nodo(id=3, x=0, y=0, z=600, restricciones = [True,True,True,True,True,True]) #Empotramiento
nodo_l = Nodo(id=4, x=300, y=0, z=600, restricciones = [True,True,True,True,True,True]) #Empotramiento

#Top
nodo_m = Nodo(id=5, x=0, y=300, z=0, restricciones = [None,None,None,None,None,None])
nodo_n = Nodo(id=6, x=300, y=300, z=0, restricciones = [None,None,None,None,None,None])
nodo_o = Nodo(id=7, x=0, y=300, z=600, restricciones = [None,None,None,None,None,None])
nodo_p = Nodo(id=8, x=300, y=300, z=600, restricciones = [None,None,None,None,None,None])


nodos = [nodo_i, nodo_j, nodo_k, nodo_l, nodo_m, nodo_n, nodo_o, nodo_p


]


barra1 = Barra(
    id=1, nodo_i=1, nodo_f=5, E=2100, I_y=10.88, I_z=10.88, G=7720, J=0.121,
    A=3.61, tita=0, nodo_i_obj=nodo_i, nodo_f_obj=nodo_m
)

barra2 = Barra(
    id=2, nodo_i=2, nodo_f=6, E=2100, I_y=10.88, I_z=10.88, G=7720, J=0.121,
    A=3.61, tita=0, nodo_i_obj=nodo_j, nodo_f_obj=nodo_n
)
barra3 = Barra(
    id=3, nodo_i=3, nodo_f=7, E=2100, I_y=10.88, I_z=10.88, G=7720, J=0.121,
    A=3.61, tita=0, nodo_i_obj=nodo_k, nodo_f_obj=nodo_o
)

barra4 = Barra(
    id=4, nodo_i=4, nodo_f=8, E=2100, I_y=10.88, I_z=10.88, G=7720, J=0.121,
    A=3.61, tita=0, nodo_i_obj=nodo_l, nodo_f_obj=nodo_p
)

#Acostadas

barra5 = Barra(
    id=5, nodo_i=5, nodo_f=7, E=2100, I_y=10.88, I_z=10.88, G=7720, J=0.121,
    A=3.61, tita=0, nodo_i_obj=nodo_m, nodo_f_obj=nodo_o
)
barra6 = Barra(
    id=6, nodo_i=5, nodo_f=6, E=2100, I_y=10.88, I_z=10.88, G=7720, J=0.121,
    A=3.61, tita=0, nodo_i_obj=nodo_m, nodo_f_obj=nodo_n
)

barra7 = Barra(
    id=7, nodo_i=8, nodo_f=6, E=2100, I_y=10.88, I_z=10.88, G=7720, J=0.121,
    A=3.61, tita=0, nodo_i_obj=nodo_p, nodo_f_obj=nodo_n
)

barra8 = Barra(
    id=8, nodo_i=8, nodo_f=7, E=2100, I_y=10.88, I_z=10.88, G=7720, J=0.121,
    A=3.61, tita=0, nodo_i_obj=nodo_p, nodo_f_obj=nodo_o
)
# --- Crear barras ---
barras = [barra1, barra2, barra3, barra4, barra5, barra6, barra7, barra8

]

# --- Visualización ---
plotter = pv.Plotter()

# Dibujar nodos (esferas y etiquetas)
for nodo in nodos:
    coord = nodo.get_coord()
    plotter.add_mesh(pv.Sphere(center=coord, radius=0.05), color='red')
    plotter.add_point_labels([coord], [f"N{nodo.id}"], font_size=12)

# Dibujar barras
for barra in barras:
    p1 = barra.nodo_i_obj.get_coord()
    p2 = barra.nodo_f_obj.get_coord()
    plotter.add_mesh(pv.Line(p1, p2), color='blue', line_width=5)

plotter.show()
