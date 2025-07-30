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