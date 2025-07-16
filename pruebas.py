from core.nodos import Nodo
from core.barra import Barra
import numpy as np

class TipoCarga:
    def __init__(self, id, tipo, L1, L2, q1, q2, alpha_x, alpha_y, alpha_z, theta_perfil=0.0):
        self.id = id
        self.tipo = tipo
        self.L1 = L1
        self.L2 = L2
        self.q1 = q1
        self.q2 = q2
        self.alpha_x = alpha_x  # Ángulo respecto a X global (°)
        self.alpha_y = alpha_y  # Ángulo respecto a Y global (°)
        self.alpha_z = alpha_z  # Ángulo respecto a Z global (°)
        self.theta_perfil = theta_perfil  # Giro del perfil (en grados)

    def vector_global(self):
        lam_x = np.cos(np.radians(self.alpha_x))
        lam_y = np.cos(np.radians(self.alpha_y))
        lam_z = np.cos(np.radians(self.alpha_z))
        return self.q1 * np.array([lam_x, lam_y, lam_z])

# Crear nodos:
nodo1 = Nodo(1, 0, 0, 0)
nodo2 = Nodo(2, 5, 0, 0)

# Crear barra:
barra = Barra(
    id=1, nodo_i=1, nodo_f=2, E=21000, I_x=10, I_y=10, I_z=10,
    G=8000, J=5, nodo_i_obj=nodo1, nodo_f_obj=nodo2
)

# Crear carga (10 unidades, ángulos en ° respecto a X, Y, Z, con giro de perfil):
carga = TipoCarga(
    id=1, tipo=2, L1=2.5, L2=2.5, q1=1.0, q2=0.0,
    alpha_x=90, alpha_y=0, alpha_z=0, theta_perfil=0.0
)

# Transformar la carga a local (usando el método de la barra que espera la instancia de la carga)
f_local = barra.transformar_carga_global_a_local(carga)
print("Carga en local (perfil parado):", f_local)
