import numpy as np
import pandas as pd

# Suponiendo que ya tenés definidas estas clases (y que todo funciona)
from core.nodos import Nodo
from core.barra import Barra
from core.carga_puntual import CargaPuntual
from core.estructura import Estructura

# 1. Crear nodos
nodo_i = Nodo(id=1, x=0, y=0, z=0, restricciones = [True,True,True,True,True,True])
nodo_j = Nodo(id=2, x=5, y=0, z=0, restricciones = [None, None, None, None, None, None])
nodo_k = Nodo(id=3, x=10, y=0, z=0, restricciones = [True,True,True,True,True,True])

# 2. Crear barras
barra1 = Barra(
    id=1, nodo_i=1, nodo_f=2, E=21000, I_x= 0.166, I_y=0.0833, I_z=0.0833, G=8000, J=0.5,
    A=1, tita=0, nodo_i_obj=nodo_i, nodo_f_obj=nodo_j
)
barra2 = Barra(
    id=2, nodo_i=2, nodo_f=3, E=21000, I_x=0.166, I_y=0.0833, I_z=0.0833, G=8000, J=0.5,
    A=1, tita=0, nodo_i_obj=nodo_j, nodo_f_obj=nodo_k
)

# 3. Crear cargas
carga1 = CargaPuntual(id=1, x=2, y=0, z=0, q=(-1000), alpha_x=90, alpha_y=0, alpha_z=90)
carga2 = CargaPuntual(id=2, x=7, y=0, z=0, q=(-1000), alpha_x=90, alpha_y=0, alpha_z=90)

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
K1 = barra1.matriz_rigidez_portico_3d()
K2 = barra2.matriz_rigidez_portico_3d()
K_global = estructura.ensamble_matriz_global()
F = estructura.ensamble_cargas_equivalentes()
D = estructura.resolver()
R = estructura.calcular_reacciones()


# 6. Exportar a Excel (cada una en su hoja)
with pd.ExcelWriter("matrices_rigidez_3D.xlsx") as writer:
    pd.DataFrame(K1).to_excel(writer, sheet_name="Barra 1 (K1)", index=False, header=False)
    pd.DataFrame(K2).to_excel(writer, sheet_name="Barra 2 (K2)", index=False, header=False)
    pd.DataFrame(K_global).to_excel(writer, sheet_name="Global", index=False, header=False)
    pd.DataFrame(F).to_excel(writer, sheet_name="F", index=False, header=False)
    pd.DataFrame(D).to_excel(writer, sheet_name="Desplazamientos", index=False, header=False)
    pd.DataFrame(R).to_excel(writer, sheet_name="Reacciones", index=False, header=False)
print("Matrices exportadas en 'matrices_rigidez_3D.xlsx' 🎉🚀")

def debug_bases(self):
    print("\n=== DEBUG BASES LOCALES BARRA", self.id, "===")
    print("x_local:", self.x_local)
    print("y_local:", self.y_local)
    print("z_local:", self.z_local)
    print("Normas:", np.linalg.norm(self.x_local), np.linalg.norm(self.y_local), np.linalg.norm(self.z_local))
    print("Ortogonalidad x·y:", np.dot(self.x_local, self.y_local))
    print("Ortogonalidad x·z:", np.dot(self.x_local, self.z_local))
    print("Ortogonalidad y·z:", np.dot(self.y_local, self.z_local))
    print("Determinante base (debe ser +1):", np.linalg.det(np.column_stack([self.x_local, self.y_local, self.z_local])))
    print("====================================\n")
