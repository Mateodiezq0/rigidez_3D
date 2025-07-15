from dataclasses import dataclass, field
import numpy as np
from typing import List

@dataclass
class Nodo:
    id: int
    x: float
    y: float
    z: float
    restricciones: List[bool] = field(default_factory=lambda: [False]*6)
    valores_prescritos: List[float] = field(default_factory=lambda: [0.0]*6)

    def get_coord(self):
        return np.array([self.x, self.y, self.z])

    def __repr__(self):
        return (f"Nodo(id={self.id}, x={self.x}, y={self.y}, z={self.z}, "
                f"restricciones={self.restricciones}, valores_prescritos={self.valores_prescritos})")
