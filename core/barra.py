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

    reaccion_de_empotramiento_global: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(12))           #Reaccion total de las barras GLOBAL
    reaccion_nudo_i_equivalente_global: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))          #Reaccion equivalente de nodo inicial GLOBAL
    reaccion_nudo_f_equivalente_global: Optional[np.ndarray] = field(default_factory=lambda: np.zeros(6))          #Reaccion equivalente de nodo final GLOBAL
    
    k_global_dat : Optional[np.ndarray] = None  # Matriz de rigidez global (12x12)
    
    
    def p_global(self):
        sm = self.calcular_submatriz_de_rotacion()
        T = self.bloque_diagonal_4x3(sm)
        self.reaccion_de_empotramiento_global = T.T @ self.reaccion_de_empotramiento_local_total
        #print()
        #print("ID de la barra:", self.id)
        #print("Reacción de empotramiento rotado en global:", self.reaccion_de_empotramiento_global)
        #print()
        self.reaccion_nudo_i_equivalente_global = -(self.reaccion_de_empotramiento_global[:6])
        #print(f"Reacción de nudo {self.nodo_i} rotado en global:", self.reaccion_nudo_i_equivalente_global)
        self.reaccion_nudo_f_equivalente_global = -(self.reaccion_de_empotramiento_global[6:])
        #print(f"Reacción de nudo {self.nodo_f} rotado en global:", self.reaccion_nudo_f_equivalente_global)
        return self.reaccion_de_empotramiento_global, self.reaccion_nudo_i_equivalente_global, self.reaccion_nudo_f_equivalente_global
    
    def actualizar_reacciones_global(self):
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
        atol = 1e-3

        print(f"\n--- [Barra {self.id}] Calculo de bases ---")
        print(f"Nodo i: {coord_i}, Nodo f: {coord_f}")

        # 1. Xlocal: SIEMPRE del menor al mayor
        x_local = coord_f - coord_i
        self.L = np.linalg.norm(x_local)
        self.x_local = x_local / self.L
        print(f"[Barra {self.id}] Xlocal: {self.x_local}, L = {self.L:.4f}")

        # 2. "Up": SIEMPRE vertical global (+Y)
        up = np.array([0, 1, 0])
        if np.abs(np.dot(self.x_local, up)) > 1 - atol:
            up = np.array([0, 0, 1])
            print(f"[Barra {self.id}] Caso especial: barra ~ vertical, up cambiado a {up}")
            y_local = np.cross(up, self.x_local)
            self.y_local = y_local / np.linalg.norm(y_local)
            print(f"[Barra {self.id}] y_local corregido: {self.y_local}")
            print(f"[Barra {self.id}] x_local: {self.x_local}")
            z_local = np.cross(self.x_local, self.y_local)
            self.z_local = z_local / np.linalg.norm(z_local)
            print(f"[Barra {self.id}] z_local corregido: {self.z_local}")

        else:
            z_local = np.cross(self.x_local, up)
            z_local = z_local / np.linalg.norm(z_local)
            self.z_local = z_local
            self.y_local = np.cross(self.z_local, self.x_local)
            self.y_local = self.y_local / np.linalg.norm(self.y_local)

        print(f"[Barra {self.id}] Ylocal: {self.y_local}")
        print(f"[Barra {self.id}] Zlocal: {self.z_local}")

        # 5. Rotación antihoraria respecto del eje Xlocal (tita en grados)
        theta = np.radians(self.tita or 0.0)
        print(f"[Barra {self.id}] θ (rads): {theta}")
        if abs(theta) > 1e-8:
            print(f"[Barra {self.id}] y_local antes de rotar: {self.y_local}")
            print(f"[Barra {self.id}] z_local antes de rotar: {self.z_local}")
            base_yz = np.column_stack((self.y_local, self.z_local))
            print(f"[Barra {self.id}] Base YZ antes de rotar:\n{base_yz}")
            rot_2d = np.array([
                [np.cos(theta), -np.sin(theta)],
                [np.sin(theta),  np.cos(theta)]
            ])
            print(f"[Barra {self.id}] Matriz de rotación 2D:\n{rot_2d}")
            yz_rotados = base_yz @ rot_2d
            print(f"[Barra {self.id}] Base YZ rotada:\n{yz_rotados}")
            self.y_local = yz_rotados[:, 0]
            self.z_local = yz_rotados[:, 1]
            print(f"[Barra {self.id}] Ylocal rotado: {self.y_local}")
            print(f"[Barra {self.id}] Zlocal rotado: {self.z_local}")

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
        #print("Vector desde nodo_i a carga:", vec_ic)
        li = np.dot(vec_ic, self.x_local)  # Proyectado sobre Xlocal (longitud)
        lj = self.L - li #bien

        # Axial (esto siempre igual)
        N = f_local[0]
        Ni = N * (lj / self.L)
        Nj = N * (li / self.L)

        # Cortantes locales
        Qy = f_local[1]
        #print("Qy:", Qy)
        Qz = f_local[2]
        #print("Qz:", Qz)

        # -------- FLEXIÓN POR Qy (Momento en Z_local) ----------
        # Fuerza local en Y

        #fy_prueba = f_local * self.y_local
        #fz_prueba = f_local * self.z_local
        #print("Proyección de la fuerza local en Yglobal:", fy_prueba)
        #print("Proyección de la fuerza local en Zglobal:", fz_prueba)  RE MAL

        #fuerza_y = -fy_prueba
        #fuerza_y = np.array([0, Qy, 0])
        
        
        #print("fuerza_y:", fuerza_y)
        #momento_z_vec = np.cross(self.x_local,fuerza_y)
        #print("momento_z_vec:", momento_z_vec)
        #print("eje_z_local:", self.z_local)
        #signo_mz = np.sign(np.dot(momento_z_vec, self.z_local)) or 1    
        #print("signo_mz:", signo_mz)
        """ voy a hacer una prueba con lo que dije"""
        v_reaccion_global = - v_carga_global

        reaccion_momento_global = np.cross(self.x_local, v_reaccion_global)
        reaccion_momento_global_unitario = reaccion_momento_global / np.linalg.norm(reaccion_momento_global)
        signo_mz = np.sign(np.dot(reaccion_momento_global_unitario, self.z_local)) or 1

        Qi_y = Qy * ((lj / self.L)**2) * (3 - 2 * (lj / self.L))
        Qj_y = Qy * ((li / self.L)**2) * (3 - 2 * (li / self.L))
        Mi_z = signo_mz * (abs(Qy) * li * ((lj / self.L)**2))
        #print("Mi_z:", Mi_z)
        Mj_z = - signo_mz * (abs(Qy) * lj * ((li / self.L)**2))
        #print("Mj_z:", Mj_z)

        # -------- FLEXIÓN POR Qz (Momento en Y_local) ----------
        
        #fuerza_z= -fz_prueba
        #fuerza_z = np.array([0, 0, Qz])
        
        
        #print("fuerza_z:", fuerza_z)
        #momento_y_vec = np.cross(self.x_local, fuerza_z)
        #print("momento_y_vec:", momento_y_vec)
        #signo_my = np.sign(np.dot(momento_y_vec, self.y_local)) or 1
        #print("signo_my:", signo_my)

        signo_my = np.sign(np.dot(reaccion_momento_global_unitario, self.y_local)) or 1

        Qi_z = Qz * ((lj / self.L)**2) * (3 - 2 * (lj / self.L))
        Qj_z = Qz * ((li / self.L)**2) * (3 - 2 * (li / self.L))
        Mi_y = signo_my * (abs(Qz) * li * ((lj / self.L)**2))
        #print("Mi_y:", Mi_y)
        Mj_y = - signo_my * (abs(Qz) * lj * ((li / self.L)**2))
        #print("Mj_y:", Mj_y)

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
        #print()
        #print()
        print(f"Reacciones de empotramiento de la carga {carga.id} en barra {self.id}:")
        self.reaccion_de_empotramiento_local_total += f_empotramiento
        print("Reacción de empotramiento TOTAL:", self.reaccion_de_empotramiento_local_total) #RE BIEN VERIFICADISIMO
        self.reaccion_de_empotramiento_i_local += f_empotramiento[:6]
        print("Reacción de empotramiento del nudo i:", self.reaccion_de_empotramiento_i_local) #RE BIEN VERIFICADISIMO
        self.reaccion_de_empotramiento_f_local += f_empotramiento[6:]
        print("Reacción de empotramiento del nudo f:", self.reaccion_de_empotramiento_f_local) #RE BIEN VERIFICADISIMO
        #print()
        #print()
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


    def calcular_submatriz_de_rotacion(self):

        self.calcular_longitud_y_bases()
        if (self.x_local == np.array([0,0,1])).all():
                T = np.array([
                    [0, 0, 1],
                    [0, 1 , 0],
                    [-1, 0, 0]
                ])
                return T
        if (self.x_local == np.array([0,0,-1])).all():
                T = np.array([
                    [0, 0, -1],
                    [0, 1 , 0],
                    [1, 0, 0]
                ])
                return T
        l = self.x_local[0]
        m = self.x_local[1]
        n = self.x_local[2]
        d = (l**2+m**2)**0.5
        cxx = l
        cyx = m
        czx = n
        cxy = -m/d
        cyy = l/d
        czy = 0
        cxz = -l*n/d
        cyz = -m*n/d
        czz = d
        T = np.array([
            [cxx, cyx, czx],
            [cxy, cyy ,  czy],
            [cxz, cyz,  czz]
        ])
        print("T aggg xddd =", T)
        return T

    def Kglobal(self):
        sm = self.calcular_submatriz_de_rotacion()
        T = self.bloque_diagonal_4x3(sm)
        k_local_p_glob = self.KlocXD()
        k_global_transformado = (T.T @ k_local_p_glob) @ T
        return k_global_transformado
