import numpy as np
import pandas as pd

# Suponiendo que ya tenés definidas estas clases (y que todo funciona)
from core.nodos import Nodo
from core.barra import Barra
from core.carga_puntual import CargaPuntual
from core.estructura import Estructura

# 1. Crear nodos
nodo_i = Nodo(id=1, x=1, y=2.236, z=0, restricciones = [True,True,True,True,True,True])
nodo_j = Nodo(id=2, x=1.5, y=2.598, z=0, restricciones = [True,True,True,True,True,True])

# 2. Crear barras
barra1 = Barra(
    id=1, nodo_i=1, nodo_f=2, E=21019000, I_y=0.00065104, I_z=0.0026042, G=8757900, J=0.0017881,
    A=0.125, tita=90, nodo_i_obj=nodo_i, nodo_f_obj=nodo_j
)


# 3. Crear cargas
#carga1 = CargaPuntual(id=1, x=2, y=0, z=0, q=(-1000), alpha_x=90, alpha_y=0, alpha_z=90)
#carga2 = CargaPuntual(id=2, x=7, y=0, z=0, q=(-1000), alpha_x=90, alpha_y=0, alpha_z=90)

#barra1.añadirCarga(carga1)


# 4. Crear estructura
estructura = Estructura()
estructura.agregar_barra(barra1)
estructura.agregar_nodo(nodo_i)
estructura.agregar_nodo(nodo_j)


# 5. Calcular matrices
XD1 = barra1.k_eje()
XD2 = barra1.k_altura()
K1loc = barra1.KlocXD()
K1 = barra1.Kglobal()
#K2 = barra2.matriz_rigidez_portico_3d()
K_global = estructura.ensamble_matriz_global()
F = estructura.ensamble_cargas_equivalentes()
D = estructura.resolver()
R = estructura.calcular_reacciones()


# 6. Exportar a Excel (cada una en su hoja)
with pd.ExcelWriter("matrices_rigidez_3D.xlsx") as writer:
    pd.DataFrame(K1loc).to_excel(writer, sheet_name="Barra 1 (K1local)", index=False, header=False)
    pd.DataFrame(XD1).to_excel(writer, sheet_name="K1 (K_eje)", index=False, header=False)
    pd.DataFrame(XD2).to_excel(writer, sheet_name="K1 (K_altura)", index=False, header=False)
    pd.DataFrame(K1).to_excel(writer, sheet_name="Barra 1 (K1)", index=False, header=False)
 #   pd.DataFrame(K2).to_excel(writer, sheet_name="Barra 2 (K2)", index=False, header=False)
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

