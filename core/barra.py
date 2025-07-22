from dataclasses import dataclass, field
import numpy as np
from core.carga_puntual import CargaPuntual
from core.nodos import Nodo
from typing import List, Optional
from math import radians, cos, sin, pi

@dataclass
class Barra:
    id: int
    nodo_i: int
    nodo_f: int
    E: float  # Módulo de elasticidad (Tn/cm^2)
    A: Optional[float] = None # Área de la sección transversal (si no se calcula automáticamente)
    I_x: float = None   # Momento de inercia en torno al eje X
    I_y: float = None  # Momento de inercia en torno al eje Y
    I_z: float = None  # Momento de inercia en torno al eje Z
    G: float  = None # Módulo de corte
    J: float  = None # Módulo de torsión
    L: Optional[float] = None  # Longitud del perfil (si no se calcula automáticamente)
    tita: Optional[float] = None  # Ángulo de inclinación del perfil (en grados)

    z_local: Optional[np.ndarray] = None  # Cosenos directores z_local respecto a global
    x_local: Optional[np.ndarray] = None  # Cosenos directores x_local respecto a global
    y_local: Optional[np.ndarray] = None  # Cosenos directores y_local respecto a global
    
    cargas: list = field(default_factory=list)  # Cargas aplicadas a la barra


    # Nuevos atributos para guardar los objetos Nodo
    nodo_i_obj: Optional["Nodo"] = None     #Objeto de nodo inicial
    nodo_f_obj: Optional["Nodo"] = None     #Objeto de nodo final

    reaccion_total_local: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(12))    #Reaccion total de las barras LOCAL
    reac_eq_i_local: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))          #Reaccion equivalente de nodo inicial LOCAL
    reac_eq_f_local: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))          #Reaccion equivalente de nodo final LOCAL
    
    reaccion_total_global: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(12))    #Reaccion total de las barras GLOBAL
    reac_eq_i_global: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))          #Reaccion equivalente de nodo inicial GLOBAL
    reac_eq_f_global: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))          #Reaccion equivalente de nodo final GLOBAL
    
    
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

    def conversion_local_global(self):
        R = self.matriz_R()
        self.reaccion_total_global = R @ self.reaccion_total_local
        self.reac_eq_i_global = -(self.reaccion_total_global[:6])
        self.reac_eq_f_global = -(self.reaccion_total_global[6:])

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
        self.reacciones_carga_puntual(carga)               # Mejora 
        self.cargas = np.append(self.cargas, carga)

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
        Kloc[2, 2] = 12 * E * I_y / L**3  # Rigidez de flexión en Y
        Kloc[3, 3] = G * J / L  # Rigidez torsional
        Kloc[4, 4] = 4 * E * I_y / L  # Flexión en Y
        Kloc[5, 5] = 4 * E * I_z / L  # Flexión en Z
        Kloc[6, 6] = E * A / L  # Rigidez axial (A * E / L)
        Kloc[7, 7] = 12 * E * I_z / L**3  # Rigidez de flexión en Z
        Kloc[8, 8] = 12 * E * I_y / L**3  # Rigidez de flexión en Y
        Kloc[9, 9] = G * J / L  # Rigidez torsional
        Kloc[10, 10] = 4 * E * I_y / L  # Flexión en Y
        Kloc[11, 11] = 4 * E * I_z / L  # Flexión en Z

        # Rellenamos las otras entradas simétricas de la matriz
        Kloc[4, 2] = Kloc[2, 4] = -6 * E * I_y / L**2
        Kloc[1, 5] = Kloc[5, 1] = 6 * E * I_z / L**2 
        Kloc[6, 0] = Kloc[0, 6] = - E * A / L 
        Kloc[7, 1] = Kloc[1, 7] = - 12 * E * I_z / L**3  
        Kloc[7, 5] = Kloc[5, 7] = - 6 * E * I_z / L**2  
        Kloc[8, 2] = Kloc[2, 8] = - 12 * E * I_y / L**3 
        Kloc[8, 4] = Kloc[4, 8] = 6 * E * I_y / L**2 
        Kloc[9, 3] = Kloc[3, 9] = - G * J / L
        Kloc[10, 2] = Kloc[2, 10] = -6 * E * I_y / L**2
        Kloc[10, 4] = Kloc[4, 10] = 2 * E * I_y / L
        Kloc[10, 8] = Kloc[8, 10] = 6 * E * I_y / L**2
        Kloc[11, 1] = Kloc[1, 11] = 6 * E * I_z / L**2  
        Kloc[11, 5] = Kloc[5, 11] = 2 * E * I_z / L
        Kloc[11, 7] = Kloc[7, 11] = -6 * E * I_z / L**2  
        
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

        f_emp = np.zeros(12) #Reacciones de empotramiento
        # Nodo inicial (i) [Qi_x, Qi_y, Ni, Mi_x, Mi_y, 0]
        f_emp[2] = -Ni        # Fuerza axial (X_local) en nodo i
        f_emp[1] = -Qi_y      # Fuerza Y_local en nodo i (cortante principal)
        f_emp[0] = -Qi_x      # Fuerza Z_local en nodo i (cortante secundaria)
        f_emp[3] = -Mi_x      # Momento torsor (X_local) en nodo i
        f_emp[4] = -Mi_y      # Momento flexor principal (Y_local) en nodo i
        #f_equiv[5] = Mi_z      # Momento flexor secundario (Z_local) en nodo i #NO  TENEMOS TODAVIA

        # Nodo final (j) [Qj_x, Qj_y, Nj, Mj_x, Mj_y, 0]
        f_emp[8] = -Nj        # Fuerza axial (X_local) en nodo j
        f_emp[7] = -Qj_y      # Fuerza Y_local en nodo j (cortante principal)
        f_emp[6] = -Qj_x      # Fuerza Z_local en nodo j (cortante secundaria)
        f_emp[9] = Mj_x     # Momento torsor (X_local) en nodo j
        f_emp[10] = Mj_y    # Momento flexor principal (Y_local) en nodo j
        #f_equiv[11] = -Mj_z    # Momento flexor secundario (Z_local) en nodo j #NO  TENEMOS TODAVIA
        
        self.reaccion_total_local += f_emp
        self.reac_eq_i_local -= f_emp[:6]
        self.reac_eq_f_local -= f_emp[6:]
        
        return f_emp


    def debugging_reacciones_carga_puntual(self, carga: "CargaPuntual"):
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

            f_emp = np.zeros(12) #Reacciones de empotramiento
            # Nodo inicial (i) [Qi_x, Qi_y, Ni, Mi_x, Mi_y, 0]
            f_emp[2] = -Ni        # Fuerza axial (X_local) en nodo i
            f_emp[1] = -Qi_y      # Fuerza Y_local en nodo i (cortante principal)
            f_emp[0] = -Qi_x      # Fuerza Z_local en nodo i (cortante secundaria)
            f_emp[3] = -Mi_x      # Momento torsor (X_local) en nodo i
            f_emp[4] = -Mi_y      # Momento flexor principal (Y_local) en nodo i
            #f_equiv[5] = Mi_z      # Momento flexor secundario (Z_local) en nodo i #NO  TENEMOS TODAVIA

            # Nodo final (j) [Qj_x, Qj_y, Nj, Mj_x, Mj_y, 0]
            f_emp[8] = -Nj        # Fuerza axial (X_local) en nodo j
            f_emp[7] = -Qj_y      # Fuerza Y_local en nodo j (cortante principal)
            f_emp[6] = -Qj_x      # Fuerza Z_local en nodo j (cortante secundaria)
            f_emp[9] = Mj_x     # Momento torsor (X_local) en nodo j
            f_emp[10] = Mj_y    # Momento flexor principal (Y_local) en nodo j
            #f_equiv[11] = -Mj_z    # Momento flexor secundario (Z_local) en nodo j #NO  TENEMOS TODAVIA
            
            return f_emp
