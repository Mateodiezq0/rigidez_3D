from dataclasses import dataclass, field
import numpy as np
from typing import List

class CargaPuntual:
    id: int

    x: float  # Posición de inicio de la carga 
    y: float  # Posición de inicio de la carga 
    z: float  # Posición de inicio de la carga 

    q: float  # Magnitud de la carga (fuerza o momento) (En KN, teniendo en cuenta que si el numero es positivo, la carga es hacia arriba, y si es negativo, hacia abajo) 

    alpha_x: float  # Ángulo respecto al eje X
    alpha_y: float  # Ángulo respecto al eje Y
    alpha_z: float  # Ángulo respecto al eje Z


    def __init__(self, id: int, x: float, y: float, z: float, q: float, alpha_x: float = 0.0, alpha_y: float = 0.0, alpha_z: float = 0.0):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.q = q
        self.alpha_x = alpha_x
        self.alpha_y = alpha_y
        self.alpha_z = alpha_z


    
    def reacciones_de_empotramiento(self, barra):
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
        barra.calcular_longitud_y_bases()

        # 2. Proyecta la carga en el sistema local de la barra
        modulo = self.q
        alpha_x = np.radians(self.alpha_x)
        alpha_y = np.radians(self.alpha_y)
        alpha_z = np.radians(self.alpha_z)
        v_carga_global = modulo * np.array([np.cos(alpha_x), np.cos(alpha_y), np.cos(alpha_z)])
        print("v_carga_global:", v_carga_global)
        r_base = np.vstack([barra.x_local, barra.y_local, barra.z_local])
        print("r_base:", r_base)
        f_local = r_base @ v_carga_global  # [Fx, Fy, Fz]
        print("v_carga_global:", v_carga_global)
        print("f_local:", f_local)  #RE BIEN

        # 3. Posición relativa de la carga
        nodo_i = barra.nodo_i_obj.get_coord()
        pos_carga = np.array([self.x, self.y, self.z])
        vec_ic = pos_carga - nodo_i
        #print("Vector desde nodo_i a carga:", vec_ic)
        li = np.dot(vec_ic, barra.x_local)  # Proyectado sobre Xlocal (longitud)
        lj = barra.L - li #bien

        # Axial (esto siempre igual)
        N = f_local[0]
        Ni = N * (lj / barra.L)
        Nj = N * (li / barra.L)

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

        reaccion_momento_global = np.cross(barra.x_local, v_reaccion_global)
        reaccion_momento_global_unitario = reaccion_momento_global / np.linalg.norm(reaccion_momento_global)
        signo_mz = np.sign(np.dot(reaccion_momento_global_unitario, barra.z_local)) or 1

        Qi_y = Qy * ((lj / barra.L)**2) * (3 - 2 * (lj / barra.L))
        Qj_y = Qy * ((li / barra.L)**2) * (3 - 2 * (li / barra.L))
        Mi_z = signo_mz * (abs(Qy) * li * ((lj / barra.L)**2))
        #print("Mi_z:", Mi_z)
        Mj_z = - signo_mz * (abs(Qy) * lj * ((li / barra.L)**2))
        #print("Mj_z:", Mj_z)

        # -------- FLEXIÓN POR Qz (Momento en Y_local) ----------
        
        #fuerza_z= -fz_prueba
        #fuerza_z = np.array([0, 0, Qz])
        
        
        #print("fuerza_z:", fuerza_z)
        #momento_y_vec = np.cross(self.x_local, fuerza_z)
        #print("momento_y_vec:", momento_y_vec)
        #signo_my = np.sign(np.dot(momento_y_vec, self.y_local)) or 1
        #print("signo_my:", signo_my)

        signo_my = np.sign(np.dot(reaccion_momento_global_unitario, barra.y_local)) or 1

        Qi_z = Qz * ((lj / barra.L)**2) * (3 - 2 * (lj / barra.L))
        Qj_z = Qz * ((li / barra.L)**2) * (3 - 2 * (li / barra.L))
        Mi_y = signo_my * (abs(Qz) * li * ((lj / barra.L)**2))
        #print("Mi_y:", Mi_y)
        Mj_y = - signo_my * (abs(Qz) * lj * ((li / barra.L)**2))
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
        print(f"Reacciones de empotramiento de la carga {self.id} en barra {barra.id}:")
        barra.reaccion_de_empotramiento_local_total += f_empotramiento
        print("Reacción de empotramiento TOTAL:", barra.reaccion_de_empotramiento_local_total) #RE BIEN VERIFICADISIMO
        barra.reaccion_de_empotramiento_i_local += f_empotramiento[:6]
        print("Reacción de empotramiento del nudo i:", barra.reaccion_de_empotramiento_i_local) #RE BIEN VERIFICADISIMO
        barra.reaccion_de_empotramiento_f_local += f_empotramiento[6:]
        print("Reacción de empotramiento del nudo f:", barra.reaccion_de_empotramiento_f_local) #RE BIEN VERIFICADISIMO
        #print()
        #print()
        return barra.reaccion_de_empotramiento_local_total

