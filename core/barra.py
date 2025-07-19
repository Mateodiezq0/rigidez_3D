from dataclasses import dataclass, field
import numpy as np
from core.nodos import Nodo
from typing import List, Optional
from math import radians, cos, sin, pi


class Barra:
    id: int
    nodo_i: int
    nodo_f: int
    E: float  # Módulo de elasticidad (Tn/cm^2)
    A: Optional[float] = None # Área de la sección transversal (si no se calcula automáticamente)
    I_x: float  # Momento de inercia en torno al eje X
    I_y: float  # Momento de inercia en torno al eje Y
    I_z: float  # Momento de inercia en torno al eje Z
    G: float  # Módulo de corte
    J: float  # Módulo de torsión
    L: Optional[float] = None  # Longitud del perfil (si no se calcula automáticamente)
    tita: Optional[float] = None  # Ángulo de inclinación del perfil (en grados)

    z_local: Optional[np.ndarray] = None  # Cosenos directores z_local respecto a global
    x_local: Optional[np.ndarray] = None  # Cosenos directores x_local respecto a global
    y_local: Optional[np.ndarray] = None  # Cosenos directores y_local respecto a global
    
    cargas = field(default_factory=list)  # Cargas aplicadas a la barra


    # Nuevos atributos para guardar los objetos Nodo
    nodo_i_obj: Optional["Nodo"] = None
    nodo_f_obj: Optional["Nodo"] = None

    def calcular_longitud_y_bases(self):            #DONEEEEE
        # 1. Calcula vector de barra
        coord_i = self.nodo_i_obj.get_coord()
        coord_f = self.nodo_f_obj.get_coord()

        v_barra = coord_f - coord_i
        self.L = np.linalg.norm(v_barra)
        self.z_local = v_barra / self.L  # <---- Cosenos directores z_local respecto a global

        # 2. "up" referencia para armar la base inicial
        if abs(self.z_local[2]) < 0.99:
            up = np.array([0, 0, 1])
        else:
            up = np.array([0, 1, 0])

        # 3. Base local sin giro de perfil (tita=0)
        x0 = np.cross(up, self.z_local)
        x0 = x0 / np.linalg.norm(x0)
        y0 = np.cross(self.z_local, x0)

        # 4. Aplica giro tita (perfil) en el plano x0-y0
        theta = np.radians(self.tita or 0.0)  # Por si es None
        rot_2d = np.array([
            [np.cos(theta), -np.sin(theta)],
            [np.sin(theta),  np.cos(theta)]
        ])
        base_xy = np.column_stack((x0, y0))  # 3x2
        x_y_rotados = base_xy @ rot_2d
        self.x_local = x_y_rotados[:, 0]   # <--- Cosenos directores x_local respecto a global
        self.y_local = x_y_rotados[:, 1]   # <--- Cosenos directores y_local respecto a global

    def reacciones_carga_puntual_global(self, carga):
        f_equiv_local = self.reacciones_carga_puntual(carga)
        R = self.matriz_R()
        return R @ f_equiv_local

    def matriz_r(self):
        # Asegura que las bases están calculadas
        if self.x_local is None or self.y_local is None or self.z_local is None:
            self.calcular_longitud_y_bases()
        # Matriz r: cada COLUMNA = eje local expresado en global
        r = np.column_stack([self.x_local, self.y_local, self.z_local])
        return r

    def matriz_R(self):
        # Matriz de rotación 12x12 para transformar matrices/vectores 3D
        r = self.matriz_r()
        R = np.zeros((12, 12))
        for i in range(4):
            R[i*3:(i+1)*3, i*3:(i+1)*3] = r
        return R

    def añadirCarga(self, carga):
        """
        Añade una carga a la barra.
        La carga debe ser un objeto que tenga los atributos necesarios para transformarla a local.
        """
        self.cargas.append(carga)

    def matriz_rigidez_portico_3d(self):
        # Asegura que la longitud y las bases están listas
        self.calcular_longitud_y_bases()
        L = self.L
        E = self.E
        # Calcula el área de la sección transversal usando los datos del objeto
        A = self.A
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

        R = self.matriz_R()
        
        return R.T @ Kloc @ R
    
    def reacciones_carga_puntual(self, carga: "CargaPuntual"):
        """
        Calcula las reacciones equivalentes en los extremos de la barra
        debidas a una carga puntual en cualquier parte de la barra, usando sistema local.
        Retorna un vector de fuerzas nodales equivalentes (12) en local.
        """

        # 1. Calcula la base local si hace falta
        if self.z_local is None or self.x_local is None or self.y_local is None:
            self.calcular_longitud_y_bases()

        # 2. Proyecta la carga en el sistema local de la barra
        modulo = carga.q
        alpha_x = np.radians(carga.alpha_x)
        alpha_y = np.radians(carga.alpha_y)
        alpha_z = np.radians(carga.alpha_z)
        v_carga_global = modulo * np.array([np.cos(alpha_x), np.cos(alpha_y), np.cos(alpha_z)])
        # Cambio de base: global -> local
        r_base = np.vstack([self.x_local, self.y_local, self.z_local])  # matriz r 3x3
        f_local = r_base @ v_carga_global  # fuerza en sistema local [Fx, Fy, Fz]

        # 3. POSICIÓN RELATIVA DE LA CARGA SOBRE LA BARRA
        # - li: distancia desde nodo_i a la carga
        # - lj: distancia desde nodo_j a la carga
        # Proyectamos el vector (nodo_i -> carga) sobre el eje de barra (z_local)
        nodo_i = self.nodo_i_obj.get_coord()
        pos_carga = np.array([carga.x, carga.y, carga.z])
        vec_ic = pos_carga - nodo_i
        li = np.dot(vec_ic, self.z_local)
        lj = self.L - li

        # 4. Usar super-fórmulas tipo Timoshenko (o Cook) para cada eje local
        # Generalizando la clásica de 2D (revisá si usás diferente convención):

        # Axial (Z local)
        N = f_local[2]  # Componente axial (Fz en local)
        Ni = N * (lj / self.L)
        Nj = N * (li / self.L)

        # Cortantes (X local)
        Qx = f_local[0]
        Qy = f_local[1]

        Qi_x = Qx * ((lj / self.L) ** 2) * (3 - 2 * (lj / self.L))
        Qj_x = Qx * ((li / self.L) ** 2) * (3 - 2 * (li / self.L))
        # Momentos flectores respecto X local (Y-Z plano)
        Mi_x = Qy * li * (lj / self.L) ** 2
        Mj_x = Qy * lj * (li / self.L) ** 2

        # Cortantes (Y local)
        Qi_y = Qy * ((lj / self.L) ** 2) * (3 - 2 * (lj / self.L))
        Qj_y = Qy * ((li / self.L) ** 2) * (3 - 2 * (li / self.L))
        # Momentos flectores respecto Y local (X-Z plano)
        Mi_y = Qx * li * (lj / self.L) ** 2
        Mj_y = Qx * lj * (li / self.L) ** 2

        # (No incluimos torsión ni momento puntual, podés sumarlo si la carga genera momento)

        # 5. Armar el vector de fuerzas nodales equivalentes para barra 3D
        # [u_xi, u_yi, u_zi, rot_xi, rot_yi, rot_zi, u_xj, u_yj, u_zj, rot_xj, rot_yj, rot_zj]
        # Asignar cada resultado a su grado de libertad correspondiente

        f_equiv = np.zeros(12)
        # Nodo inicial (i) [Qi_x, Qi_y, Ni, Mi_x, Mi_y, 0]
        f_equiv[2] = -Ni        # Fuerza axial (X_local) en nodo i
        f_equiv[1] = -Qi_y      # Fuerza Y_local en nodo i (cortante principal)
        f_equiv[0] = -Qi_x      # Fuerza Z_local en nodo i (cortante secundaria)
        f_equiv[3] = -Mi_x      # Momento torsor (X_local) en nodo i
        f_equiv[4] = -Mi_y      # Momento flexor principal (Y_local) en nodo i
        #f_equiv[5] = Mi_z      # Momento flexor secundario (Z_local) en nodo i #NO  TENEMOS TODAVIA

        # Nodo final (j) [Qj_x, Qj_y, Nj, Mj_x, Mj_y, 0]
        f_equiv[8] = -Nj        # Fuerza axial (X_local) en nodo j
        f_equiv[7] = -Qj_y      # Fuerza Y_local en nodo j (cortante principal)
        f_equiv[6] = -Qj_x      # Fuerza Z_local en nodo j (cortante secundaria)
        f_equiv[9] = Mj_x     # Momento torsor (X_local) en nodo j
        f_equiv[10] = Mj_y    # Momento flexor principal (Y_local) en nodo j
        #f_equiv[11] = -Mj_z    # Momento flexor secundario (Z_local) en nodo j #NO  TENEMOS TODAVIA

        return f_equiv






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
            A: Optional[float] = None,
            tita: Optional[float] = None  # Ángulo de inclinación del perfil (en grados, si no se calcula automáticamente)
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
            self.A = A  # Área de la sección transversal
            self.nodo_i_obj = nodo_i_obj
            self.nodo_f_obj = nodo_f_obj
            self.tita = tita  # Ángulo de inclinación del perfil (en grados)

            if self.L is None and self.nodo_i_obj and self.nodo_f_obj:
                self.calcular_longitud_y_bases()
        
    


    def base_local_rotada(self, theta_perfil=0.0): #ESTO NO VA ACA XDXDXD
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

    def transformar_carga_global_a_local(self, carga): #ESTO NO VA ACA XDXDXD
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
