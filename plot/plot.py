import sys
import os
import numpy as np
import pyvista as pv

# Asegurarse que se puede importar core.*
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.nodos import Nodo
from core.barra import Barra

# --- Crear nodos ---
nodos = {
    0: Nodo(0, 0, 0, 0),
    1: Nodo(1, 1, 0, 0),
    2: Nodo(2, 1, 1, 1),
    3: Nodo(3, 0, 1, 1)
}

# --- Crear barras ---
barras = [
    Barra(0, 0, 1, E=200000, I_x=1, I_y=1, I_z=1, G=80000, J=0.5, nodo_i_obj=nodos[0], nodo_f_obj=nodos[1]),
    Barra(1, 1, 2, E=200000, I_x=1, I_y=1, I_z=1, G=80000, J=0.5, nodo_i_obj=nodos[1], nodo_f_obj=nodos[2]),
    Barra(2, 2, 3, E=200000, I_x=1, I_y=1, I_z=1, G=80000, J=0.5, nodo_i_obj=nodos[2], nodo_f_obj=nodos[3]),
]

# --- Visualización ---
plotter = pv.Plotter()

# Dibujar nodos (esferas y etiquetas)
for nodo in nodos.values():
    coord = nodo.get_coord()
    plotter.add_mesh(pv.Sphere(center=coord, radius=0.05), color='red')
    plotter.add_point_labels([coord], [f"N{nodo.id}"], font_size=12)

# Dibujar barras
for barra in barras:
    p1 = barra.nodo_i_obj.get_coord()
    p2 = barra.nodo_f_obj.get_coord()
    plotter.add_mesh(pv.Line(p1, p2), color='blue', line_width=5)

plotter.show()
