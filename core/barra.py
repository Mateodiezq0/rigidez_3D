from dataclasses import dataclass, field
import numpy as np
from core.nodos import Nodo
from typing import List, Optional
from math import radians, cos, sin, pi

@dataclass
class Barra:
    id: int
    nodo_i: int
    nodo_f: int
    E: float  # Módulo de elasticidad (Tn/cm^2)
    I_x: float  # Momento de inercia en torno al eje X
    I_y: float  # Momento de inercia en torno al eje Y
    I_z: float  # Momento de inercia en torno al eje Z
    G: float  # Módulo de corte
    J: float  # Módulo de torsión
    L: Optional[float] = None  # Longitud del elemento
    #tita: Optional[float] = None  # Ángulo de inclinación del elemento

    # Nuevos atributos para guardar los objetos Nodo
    nodo_i_obj: Optional["Nodo"] = None
    nodo_f_obj: Optional["Nodo"] = None

    # Nuevos atributos para trabajar en 3D
    beta_x: Optional[float] = None  # Rotación alrededor del eje X
    beta_y: Optional[float] = None  # Rotación alrededor del eje Y
    beta_z: Optional[float] = None  # Rotación alrededor del eje Z

    def calcular_longitud_y_angulos(self):                                                  #DONE
        if self.nodo_i_obj is None or self.nodo_f_obj is None:
            raise ValueError("Debe asignar nodo_i_obj y nodo_f_obj antes de calcular.")

        coord_i = self.nodo_i_obj.get_coord()
        coord_f = self.nodo_f_obj.get_coord()

        Vx = coord_f[0] - coord_i[0]
        Vy = coord_f[1] - coord_i[1]
        Vz = coord_f[2] - coord_i[2]

        self.L = np.sqrt(Vx**2 + Vy**2 + Vz**2)

        # Cosenos directores
        self.lambda_x = Vx / self.L
        self.lambda_y = Vy / self.L
        self.lambda_z = Vz / self.L

        # Ángulos con los ejes, en grados (de 0° a 180°)
        self.beta_x = np.degrees(np.arccos(self.lambda_x))
        self.beta_y = np.degrees(np.arccos(self.lambda_y))
        self.beta_z = np.degrees(np.arccos(self.lambda_z))


    def matriz_rigidez_portico_3d(self):
        #assert self.L is not None and self.tita is not None, "Longitud y ángulo deben estar definidos"
        L = self.L
        E = self.E
        A = self.area()  # Área de la sección transversal (se supone que la clase tiene un área definida, si es necesario)
        I_x = self.I_x
        I_y = self.I_y
        I_z = self.I_z
        G = self.G
        J = self.J

        # Matriz de rigidez para 3D (12x12)
        Kloc = np.zeros((12, 12))  # 12 grados de libertad

        # Los términos de la matriz de rigidez local (según la imagen que nos diste)
        Kloc[0, 0] = E * A / L  # Rigidez axial (A * E / L)
        Kloc[1, 1] = 12 * E * I_z / L**3  # Rigidez de flexión en Z
        Kloc[1, 5] = -6 * E * I_z / L**2  # Flexión en Z
        Kloc[2, 2] = 12 * E * I_y / L**3  # Rigidez de flexión en Y
        Kloc[2, 4] = 6 * E * I_y / L**2  # Flexión en Y
        Kloc[3, 3] = G * J / L  # Rigidez torsional
        Kloc[4, 4] = 4 * E * I_y / L  # Flexión en Y
        Kloc[4, 5] = 6 * E * I_y / L**2  # Flexión en Y
        Kloc[5, 5] = 4 * E * I_z / L  # Flexión en Z
        Kloc[5, 4] = 6 * E * I_z / L**2  # Flexión en Z
        Kloc[6, 6] = E * A / L  # Rigidez axial (A * E / L)
        Kloc[7, 7] = 12 * E * I_z / L**3  # Rigidez de flexión en Z
        Kloc[8, 8] = 12 * E * I_y / L**3  # Rigidez de flexión en Y
        Kloc[9, 9] = G * J / L  # Rigidez torsional
        Kloc[10, 10] = 4 * E * I_z / L  # Flexión en Z
        Kloc[11, 11] = 4 * E * I_y / L  # Flexión en Y

        # Rellenamos las otras entradas simétricas de la matriz
        Kloc[1, 2] = Kloc[2, 1] = -6 * E * I_y / L**2
        Kloc[1, 3] = Kloc[3, 1] = 6 * E * I_z / L**2
        Kloc[2, 3] = Kloc[3, 2] = -12 * E * I_z / L**3
        Kloc[4, 5] = Kloc[5, 4] = -6 * E * I_y / L**2
        Kloc[5, 5] = 4 * E * I_z / L
        Kloc[6, 6] = E * A / L  # Rigidez axial (repetido)

        R = self.matriz_rotacion()  # Necesitamos la matriz de rotación 3D
        return R.T @ Kloc @ R

    def matriz_rotacion(self) -> np.ndarray:
        """Genera la matriz de rotación para 3D usando las rotaciones alrededor de los ejes X, Y, Z."""
        # Cálculos de los ángulos de rotación en 3D
        c_x = cos(np.radians(self.beta_x))
        s_x = sin(np.radians(self.beta_x))
        c_y = cos(np.radians(self.beta_y))
        s_y = sin(np.radians(self.beta_y))
        c_z = cos(np.radians(self.beta_z))
        s_z = sin(np.radians(self.beta_z))

        # Matriz de rotación en 3D
        R_x = np.array([
            [1, 0, 0],
            [0, c_x, -s_x],
            [0, s_x, c_x]
        ])

        R_y = np.array([
            [c_y, 0, s_y],
            [0, 1, 0],
            [-s_y, 0, c_y]
        ])

        R_z = np.array([
            [c_z, -s_z, 0],
            [s_z, c_z, 0],
            [0, 0, 1]
        ])

        # Rotación total: R = R_z * R_y * R_x
        R = R_z @ R_y @ R_x
        return R
    
    def __init__(
            self,
            id: int,
            nodo_i: int,
            nodo_f: int,
            E: float,
            I_x: float,
            I_y: float,
            I_z: float,
            G: float,
            J: float,
            L: Optional[float] = None,
            nodo_i_obj: Optional["Nodo"] = None,
            nodo_f_obj: Optional["Nodo"] = None,
            beta_x: Optional[float] = None,
            beta_y: Optional[float] = None,
            beta_z: Optional[float] = None
        ):
            self.id = id
            self.nodo_i = nodo_i
            self.nodo_f = nodo_f
            self.E = E
            self.I_x = I_x
            self.I_y = I_y
            self.I_z = I_z
            self.G = G
            self.J = J
            self.L = L  

            self.nodo_i_obj = nodo_i_obj
            self.nodo_f_obj = nodo_f_obj

            self.beta_x = beta_x
            self.beta_y = beta_y
            self.beta_z = beta_z

            if self.L is None and self.nodo_i_obj and self.nodo_f_obj:
                self.calcular_longitud_y_angulos()
        
    


    def base_local_rotada(self, theta_perfil=0.0):
            # 1. Eje z local (barra)
            coord_i = self.nodo_i_obj.get_coord()
            coord_f = self.nodo_f_obj.get_coord()
            z_local = coord_f - coord_i
            z_local = z_local / np.linalg.norm(z_local)
            # 2. x_local inicial (puede ser vertical global cruz z_local)
            if abs(z_local[2]) < 0.99:
                ref = np.array([0, 0, 1])
            else:
                ref = np.array([0, 1, 0])
            x_local_0 = np.cross(ref, z_local)
            x_local_0 = x_local_0 / np.linalg.norm(x_local_0)
            # 3. y_local_0
            y_local_0 = np.cross(z_local, x_local_0)
            # 4. Armá matriz base local inicial
            base_0 = np.column_stack((x_local_0, y_local_0, z_local))
            # 5. Rotá en el plano local x-y (alrededor de z local)
            theta = np.radians(theta_perfil)
            rot_xy = np.array([
                [np.cos(theta), -np.sin(theta), 0],
                [np.sin(theta),  np.cos(theta), 0],
                [0,             0,              1]
            ])
            # 6. Base local rotada final
            base_final = base_0 @ rot_xy
            return base_final  # Columnas: x_local, y_local, z_local

    def transformar_carga_global_a_local(self, carga):
        """
        Transforma una carga definida en global (por módulo y dirección) a local,
        usando el giro del perfil dado por la propia carga.
        Soporta tanto cosenos directores como ángulos esféricos.
        """
        # Construir vector global según cómo venga la carga
        if hasattr(carga, 'lambda_x'):
            F_global = np.array([
                carga.q1 * carga.lambda_x,
                carga.q1 * carga.lambda_y,
                carga.q1 * carga.lambda_z
            ])
        elif hasattr(carga, 'alpha_x') and hasattr(carga, 'alpha_y') and hasattr(carga, 'alpha_z'):
            # Usando ángulos respecto a ejes globales
            lam_x = np.cos(np.radians(carga.alpha_x))
            lam_y = np.cos(np.radians(carga.alpha_y))
            lam_z = np.cos(np.radians(carga.alpha_z))
            F_global = carga.q1 * np.array([lam_x, lam_y, lam_z])
        else:
            # Si tenés azimut y elevación (esféricas)
            theta = np.radians(carga.azimut_deg)
            phi = np.radians(carga.elev_deg)
            F_global = np.array([
                carga.q1 * np.cos(phi) * np.cos(theta),
                carga.q1 * np.cos(phi) * np.sin(theta),
                carga.q1 * np.sin(phi)
            ])
        
        # Usar el ángulo de giro guardado en la carga
        theta_perfil = getattr(carga, 'theta_perfil', 0.0)
        base_local = self.base_local_rotada(theta_perfil=theta_perfil)
        F_local = base_local.T @ F_global
        return F_local
