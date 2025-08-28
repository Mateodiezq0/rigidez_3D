from dataclasses import dataclass, field
from core.carga_puntual import CargaPuntual
import numpy as np
from typing import List

class CargaDistribuida(CargaPuntual):
    
    id: int

    x: float  # Posición de inicio de la carga 
    y: float  # Posición de inicio de la carga 
    z: float  # Posición de inicio de la carga 

    q: float  # Magnitud de la carga (fuerza o momento) (En KN, teniendo en cuenta que si el numero es positivo, la carga es hacia arriba, y si es negativo, hacia abajo) 
    q_f: float  # Magnitud final de la carga (fuerza o momento) (En KN, teniendo en cuenta que si el numero es positivo, la carga es hacia arriba, y si es negativo, hacia abajo)

    alpha_x: float  # Ángulo respecto al eje X
    alpha_y: float  # Ángulo respecto al eje Y
    alpha_z: float  # Ángulo respecto al eje Z


    x_f: float  # Posición de final de la carga 
    y_f: float  # Posición de final de la carga
    z_f: float  # Posición de final de la carga

    
    def reacciones_de_empotramiento(self, barra):
       if self.q == self.q_f:
           # Caso de carga uniforme
           carga_equivalente = CargaPuntual(
               id=self.id,
               x=(self.x + self.x_f) / 2,
               y=(self.y + self.y_f) / 2,
               z=(self.z + self.z_f) / 2,
               q=self.q * np.linalg.norm(np.array([self.x_f, self.y_f, self.z_f]) - np.array([self.x, self.y, self.z])),  # Magnitud total de la carga
               alpha_x=self.alpha_x,
               alpha_y=self.alpha_y,
               alpha_z=self.alpha_z
           )
           return carga_equivalente.reacciones_de_empotramiento(barra)
       




    def __init__(self, id: int, x: float, y: float, z: float, q: float,x_f: float, y_f: float, z_f: float, q_f: float, alpha_x: float = 0.0, alpha_y: float = 0.0, alpha_z: float = 0.0):
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.q = q
        self.x_f = x_f
        self.y_f = y_f
        self.z_f = z_f
        self.q_f = q_f
        self.alpha_x = alpha_x
        self.alpha_y = alpha_y
        self.alpha_z = alpha_z