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
    I_y: float = None  # Momento de inercia en torno al eje Y
    I_z: float = None  # Momento de inercia en torno al eje Z
    G: float  = None # Módulo de corte
    J: float  = None # Módulo de torsión
    L: Optional[float] = None  # Longitud del perfil (si no se calcula automáticamente)
    tita: Optional[float] = None  # Ángulo de inclinación del perfil (en grados)

    x_local: Optional[np.ndarray] = None  # Cosenos directores x_local respecto a global
    y_local: Optional[np.ndarray] = None  # Cosenos directores y_local respecto a global
    z_local: Optional[np.ndarray] = None  # Cosenos directores z_local respecto a global
    
    cargas: list = field(default_factory=list)  # Cargas aplicadas a la barra


    # Nuevos atributos para guardar los objetos Nodo
    nodo_i_obj: Optional["Nodo"] = None     #Objeto de nodo inicial
    nodo_f_obj: Optional["Nodo"] = None     #Objeto de nodo final

    reaccion_de_empotramiento_local_total: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(12))    #Reaccion total de las barras LOCAL
    reaccion_de_empotramiento_i_local: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))          #Reaccion equivalente de nodo inicial LOCAL
    reaccion_de_empotramiento_f_local: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))          #Reaccion equivalente de nodo final LOCAL

    reaccion_de_empotramiento_rotado_eje: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(12))          #Reaccion total de las barras en el eje de la barra
    reaccion_nudo_i_equivalente_rotado_eje: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))          #Reaccion equivalente de nodo inicial en el eje de la barra
    reaccion_nudo_f_equivalente_rotado_eje: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))          #Reaccion equivalente de nodo final en el eje de la barra


    reaccion_de_empotramiento_rotado_base: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(12))         #Reaccion total de las barras en la base de la barra
    reaccion_nudo_i_equivalenete_rotado_base: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))         #Reaccion equivalente de nodo inicial en la base de la barra
    reaccion_nudo_f_equivalenete_rotado_base: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))         #Reaccion equivalente de nodo final en la base de la barra
    
    reaccion_de_empotramiento_global: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(12))           #Reaccion total de las barras GLOBAL
    reaccion_nudo_i_equivalente_global: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))          #Reaccion equivalente de nodo inicial GLOBAL
    reaccion_nudo_f_equivalente_global: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))          #Reaccion equivalente de nodo final GLOBAL
    
    k_eje_dat : Optional[np.ndarray] = None  # Matriz de rigidez en el eje de la barra (12x12)
    k_altura_dat : Optional[np.ndarray] = None  # Matriz de rigidez en la altura de la barra (12x12)
    k_global_dat : Optional[np.ndarray] = None  # Matriz de rigidez global (12x12)
    

    def p_eje(self):
        alpha = np.radians(self.tita or 0.0)
        #print(" (alpha):", alpha)
        A = self.matriz_A(alpha)
        A = self.bloque_diagonal_4x3(A)  # Convertir a bloque diagonal 4x3
        #print("A para rotación:", A)
        #print("Rotacion de A traspuesta:", A.T)
        self.reaccion_de_empotramiento_rotado_eje = A.T @ self.reaccion_de_empotramiento_local_total
        print("Reacción de empotramiento rotado en eje:", self.reaccion_de_empotramiento_rotado_eje)
        self.reaccion_nudo_i_equivalente_rotado_eje = -(self.reaccion_de_empotramiento_rotado_eje[:6])
        print(f"Reacción de nudo {self.nodo_i} rotado en eje:", self.reaccion_nudo_i_equivalente_rotado_eje)
        self.reaccion_nudo_f_equivalente_rotado_eje = -(self.reaccion_de_empotramiento_rotado_eje[6:])
        print(f"Reacción de nudo {self.nodo_f} rotado en eje:", self.reaccion_nudo_f_equivalente_rotado_eje)
        return self.reaccion_de_empotramiento_rotado_eje, self.reaccion_nudo_i_equivalente_rotado_eje, self.reaccion_nudo_f_equivalente_rotado_eje
    
    def p_base(self):
        coord_i = self.nodo_i_obj.get_coord()
        coord_f = self.nodo_f_obj.get_coord()
        #print("Coordenadas de los nodos:", coord_i, coord_f)
        beta, gamma = self.calcular_angulos_barra(coord_i, coord_f)
        #print("Beta:", beta)
        B = self.matriz_B(beta)
        B = self.bloque_diagonal_4x3(B)  # Convertir a bloque diagonal 4x3
        self.reaccion_de_empotramiento_rotado_base = B.T @ self.reaccion_de_empotramiento_rotado_eje
        #print("Reacción de empotramiento rotado en base: ", self.reaccion_de_empotramiento_rotado_base)
        self.reaccion_nudo_i_equivalenete_rotado_base = -(self.reaccion_de_empotramiento_rotado_base[:6])
        #print(f"Reacción de nudo {self.nodo_i} rotado en base:", self.reaccion_nudo_i_equivalenete_rotado_base)
        self.reaccion_nudo_f_equivalenete_rotado_base = -(self.reaccion_de_empotramiento_rotado_base[6:])
        #print(f"Reacción de nudo {self.nodo_f} rotado en base:", self.reaccion_nudo_f_equivalenete_rotado_base)
        return self.reaccion_de_empotramiento_rotado_base, self.reaccion_nudo_i_equivalenete_rotado_base, self.reaccion_nudo_f_equivalenete_rotado_base
    
    def p_global(self):
        coord_i = self.nodo_i_obj.get_coord()
        coord_f = self.nodo_f_obj.get_coord()
        #print("Coordenadas de los nodos:", coord_i, coord_f)
        beta, gamma = self.calcular_angulos_barra(coord_i, coord_f)
        #print("gamma:", gamma)
        C = self.matriz_C(gamma)
        C = self.bloque_diagonal_4x3(C)  # Convertir a bloque diagonal 4x3
        self.reaccion_de_empotramiento_global = C.T @ self.reaccion_de_empotramiento_rotado_base
        #print("Reacción de empotramiento rotado en global:", self.reaccion_de_empotramiento_global)
        self.reaccion_nudo_i_equivalente_global = -(self.reaccion_de_empotramiento_global[:6])
        #print(f"Reacción de nudo {self.nodo_i} rotado en global:", self.reaccion_nudo_i_equivalente_global)
        self.reaccion_nudo_f_equivalente_global = -(self.reaccion_de_empotramiento_global[6:])
        #print(f"Reacción de nudo {self.nodo_f} rotado en global:", self.reaccion_nudo_f_equivalente_global)
        return self.reaccion_de_empotramiento_global, self.reaccion_nudo_i_equivalente_global, self.reaccion_nudo_f_equivalente_global
    
    def actualizar_reacciones_global(self):
        self.p_eje()
        self.p_base()
        self.p_global()



    #def añadirCarga(self, carga):
        #"""
        #Añade una carga a la barra.
        #La carga debe ser un objeto que tenga los atributos necesarios para transformarla a local.
        #"""
        #self.reacciones_de_empotramiento_carga_puntual(carga)               # Mejora 
        #self.cargas = np.append(self.cargas, carga)   #ESTO ES DEL MATIU VER BIEN
    
    #def resetear_reacciones(self): #ESTO LO AGREGUE YO
        #"""Limpia las reacciones acumuladas (útil antes de recalcular todo el ensamble)"""
        #self.reaccion_de_empotramiento_local_total = np.zeros(12)
        #self.reaccion_de_empotramiento_i_local = np.zeros(6)
        #self.reaccion_de_empotramiento_f_local = np.zeros(6)

    def añadirCarga(self, carga): #ESTO LO AGREGUE YO
        """
        Añade una carga a la barra (y suma sus reacciones equivalentes).
        Este método asegura el ACUMULADO.
        """
        f_empotramiento = self.reacciones_de_empotramiento_carga_puntual(carga)
        self.cargas = np.append(self.cargas, carga)
        # NO hace falta volver a sumar, ya se sumó dentro de la función
        return f_empotramiento
    
    def calcular_longitud_y_bases(self, debug=0):
        coord_i = self.nodo_i_obj.get_coord()
        coord_f = self.nodo_f_obj.get_coord()
        atol = 1e-6

        # 1. Xlocal: SIEMPRE del menor al mayor
        x_local = coord_f - coord_i
        self.L = np.linalg.norm(x_local)
        self.x_local = x_local / self.L

        # 2. "Up": SIEMPRE vertical global (+Z)
        up = np.array([0, 0, 1])
        # Si la barra es vertical, cambiá up por Xglobal
        if np.abs(np.dot(self.x_local, up)) > 1 - atol:
            up = np.array([1, 0, 0])

        # 3. Zlocal = x_local X up --> Zlocal queda a la DERECHA (-Yglobal)
        y_local = np.cross(up, self.x_local)
        if np.linalg.norm(y_local) < atol:
            up = np.array([1, 0, 0])  # si justo era vertical
            y_local = np.cross(up, self.x_local)
        y_local = y_local / np.linalg.norm(y_local)
        self.y_local = y_local
        print("Xlocal:", self.x_local)
        print("Ylocal:", self.y_local)
        # 4. Ylocal: SIEMPRE ARRIBA, base derecha (z_local X x_local)
        self.z_local = np.cross(self.x_local, self.y_local)
        print("Zlocal:", self.z_local)
        self.z_local = self.z_local / np.linalg.norm(self.z_local)

        # 6. Debug
        if debug:
            self.debug_bases()



    def debug_bases(self):
        print("x_local:", self.x_local)
        print("y_local:", self.y_local)
        print("z_local:", self.z_local)
        print("Normas:", np.linalg.norm(self.x_local), np.linalg.norm(self.y_local), np.linalg.norm(self.z_local))
        print("Ortogonalidad x·y:", np.dot(self.x_local, self.y_local))
        print("Ortogonalidad x·z:", np.dot(self.x_local, self.z_local))
        print("Ortogonalidad y·z:", np.dot(self.y_local, self.z_local))
        print("Determinante base (debe ser +1):", np.linalg.det(np.column_stack([self.x_local, self.y_local, self.z_local])))



    def reacciones_de_empotramiento_carga_puntual(self, carga: "CargaPuntual"):
        """
        Calcula las reacciones equivalentes en los extremos de la barra
        debidas a una carga puntual en cualquier parte de la barra, usando sistema local.
        Convención:
        - Xlocal = longitud de barra (de nodo_i a nodo_f)
        - Zlocal = "horizontal" (Yglobal si barra es Xglobal)
        - Ylocal = "vertical" (Zglobal si barra es Xglobal)
        Retorna un vector de fuerzas nodales equivalentes (12) en local.
        """
        # 1. Asegura la base local correcta siempre
        self.calcular_longitud_y_bases()

        # 2. Proyecta la carga en el sistema local de la barra
        modulo = carga.q
        alpha_x = np.radians(carga.alpha_x)
        alpha_y = np.radians(carga.alpha_y)
        alpha_z = np.radians(carga.alpha_z)
        v_carga_global = modulo * np.array([np.cos(alpha_x), np.cos(alpha_y), np.cos(alpha_z)])
        print("v_carga_global:", v_carga_global)
        r_base = np.vstack([self.x_local, self.y_local, self.z_local])
        print("r_base:", r_base)
        f_local = r_base @ v_carga_global  # [Fx, Fy, Fz]
        print("v_carga_global:", v_carga_global)
        print("f_local:", f_local)  #RE BIEN

        # 3. Posición relativa de la carga
        nodo_i = self.nodo_i_obj.get_coord()
        pos_carga = np.array([carga.x, carga.y, carga.z])
        vec_ic = pos_carga - nodo_i
        print("Vector desde nodo_i a carga:", vec_ic)
        li = np.dot(vec_ic, self.x_local)  # Proyectado sobre Xlocal (longitud)
        lj = self.L - li #bien

        # Axial (esto siempre igual)
        N = f_local[0]
        Ni = N * (lj / self.L)
        Nj = N * (li / self.L)

        # Cortantes locales
        Qy = f_local[1]
        print("Qy:", Qy)
        Qz = f_local[2]
        print("Qz:", Qz)

        # -------- FLEXIÓN POR Qy (Momento en Z_local) ----------
        # Fuerza local en Y
        fuerza_y = np.array([0, Qy, 0])
        print("fuerza_y:", fuerza_y)
        momento_z_vec = np.cross(fuerza_y, self.x_local)
        print("momento_z_vec:", momento_z_vec)
        print("eje_z_local:", self.z_local)
        signo_mz = np.sign(np.dot(momento_z_vec, self.z_local)) or 1    
        print("signo_mz:", signo_mz)

        Qi_y = Qy * ((lj / self.L)**2) * (3 - 2 * (lj / self.L))
        Qj_y = Qy * ((li / self.L)**2) * (3 - 2 * (li / self.L))
        Mi_z = signo_mz * (abs(Qy) * li * ((lj / self.L)**2))
        print("Mi_z:", Mi_z)
        Mj_z = - signo_mz * (abs(Qy) * lj * ((li / self.L)**2))
        print("Mj_z:", Mj_z)

        # -------- FLEXIÓN POR Qz (Momento en Y_local) ----------
        fuerza_z = np.array([0, 0, Qz])
        print("fuerza_z:", fuerza_z)
        momento_y_vec = np.cross(fuerza_z, self.x_local)
        print("momento_y_vec:", momento_y_vec)
        signo_my = np.sign(np.dot(momento_y_vec, self.y_local)) or 1
        print("signo_my:", signo_my)

        Qi_z = Qz * ((lj / self.L)**2) * (3 - 2 * (lj / self.L))
        Qj_z = Qz * ((li / self.L)**2) * (3 - 2 * (li / self.L))
        Mi_y = signo_my * (abs(Qz) * li * ((lj / self.L)**2))
        print("Mi_y:", Mi_y)
        Mj_y = - signo_my * (abs(Qz) * lj * ((li / self.L)**2))
        print("Mj_y:", Mj_y)

        # 5. Vector de fuerzas nodales equivalentes (12) - tu convención
        f_empotramiento = np.zeros(12)
        # Nodo inicial (i)
        f_empotramiento[0] = -Ni        # Axial (X_local)
        f_empotramiento[1] = -Qi_y      # Cortante (Y_local)
        f_empotramiento[2] = -Qi_z      # Cortante (Z_local)
        f_empotramiento[4] =  Mi_y      # Momento flexor en Y_local
        f_empotramiento[5] =  Mi_z      # Momento flexor en Z_local

        # Nodo final (j)
        f_empotramiento[6] = -Nj
        f_empotramiento[7] = -Qj_y
        f_empotramiento[8] = -Qj_z
        f_empotramiento[10] = Mj_y
        f_empotramiento[11] = Mj_z

        # (Si tenés que sumar torsión o momento puntual, agregar f_emp[3] y f_emp[9])

        # SUMA a la reacción total
        self.reaccion_de_empotramiento_local_total += f_empotramiento
        print("Reacción de empotramiento TOTAL:", self.reaccion_de_empotramiento_local_total) #RE BIEN VERIFICADISIMO
        self.reaccion_de_empotramiento_i_local += f_empotramiento[:6]
        print("Reacción de empotramiento del nudo i:", self.reaccion_de_empotramiento_i_local) #RE BIEN VERIFICADISIMO
        self.reaccion_de_empotramiento_f_local += f_empotramiento[6:]
        print("Reacción de empotramiento del nudo f:", self.reaccion_de_empotramiento_f_local) #RE BIEN VERIFICADISIMO
        return self.reaccion_de_empotramiento_local_total


    def KlocXD(self):
        # Asegura que la longitud y las bases están listas
        self.calcular_longitud_y_bases()
        L = self.L
        E = self.E
        # Calcula el área de la sección transversal usando los datos del objeto
        A = self.A
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
        
        return Kloc
    

    def bloque_diagonal_4x3(self, M):
        res = np.zeros((12, 12))
        for i in range(4):
            res[i*3:(i+1)*3, i*3:(i+1)*3] = M
        return res

    def matriz_A(self, alpha):
        return np.array([
            [1, 0, 0],
            [0,  np.cos(alpha),  np.sin(alpha)],
            [0, -np.sin(alpha),  np.cos(alpha)]
        ])

    def matriz_B(self, beta):
        return np.array([
            [ np.cos(beta), 0, -np.sin(beta)],
            [0,            1,      0      ],
            [ np.sin(beta), 0,  np.cos(beta)]
        ])

    def matriz_C(self, gamma):
        return np.array([
            [ np.cos(gamma), np.sin(gamma), 0],
            [-np.sin(gamma), np.cos(gamma), 0],
            [      0,              0,       1]
        ])

    def calcular_angulos_barra(self, coord_i, coord_f):
        vec = coord_f - coord_i
        #print("Vector de la barra:", vec)
        L = np.linalg.norm(vec)
        x1, y1, z1 = vec / L
        #print("Coordenadas normalizadas:", x1, y1, z1)
        beta = np.arcsin(z1)             # elevación (con respecto a XY)
        gamma = np.arctan2(y1, x1)        # azimut (en XY)
        #print("Beta:", beta)
        #print("gamma:", gamma)
        return beta, gamma


    def k_eje(self):
        alpha = np.radians(self.tita or 0.0)
        A = self.matriz_A(alpha)
        A = self.bloque_diagonal_4x3(A)  # Convertir a bloque diagonal 4x3
        #print(A)
        XD = self.KlocXD()
        #print(XD)
        self.k_eje_dat = (A.T @ XD) @ A
        return self.k_eje_dat
    
    def k_altura(self):
        coord_i = self.nodo_i_obj.get_coord()
        coord_f = self.nodo_f_obj.get_coord()
        beta, gamma = self.calcular_angulos_barra(coord_i, coord_f)
        #print("Beta:", beta)
        B = self.matriz_B(beta)
        B = self.bloque_diagonal_4x3(B)  # Convertir a bloque diagonal 4x3
        XD = self.k_eje()
        self.k_altura_dat = (B.T @ XD) @ B
        return self.k_altura_dat

    def Kglobal(self):
        coord_i = self.nodo_i_obj.get_coord()
        coord_f = self.nodo_f_obj.get_coord()
        beta, gamma = self.calcular_angulos_barra(coord_i, coord_f)
        #print("gamma:", gamma)
        C = self.matriz_C(gamma)
        C = self.bloque_diagonal_4x3(C)  # Convertir a bloque diagonal 4x3
        #print("C:", C  )
        XD = self.k_altura()
        self.k_global_dat = (C.T @ XD) @ C
        return self.k_global_dat
