from dataclasses import dataclass, field
import numpy as np
from core.carga_puntual import CargaPuntual
from core.barra import Barra
from core.carga_nodal import CargaNodal
from core.carga_puntual import CargaPuntual
from core.nodos import Nodo
from typing import List, Optional
from math import radians, cos, sin, pi

@dataclass
class Estructura:
    nodos: List[Nodo] = field(default_factory=list)
    barras: List[Barra] = field(default_factory=list)
    cargas_nodales: List[CargaNodal] = field(default_factory=list)
    cargas: List = field(default_factory=list)
    vector_nodal_equivalente: Optional[np.ndarray] = None
    desplazamientos: Optional[np.ndarray] = None
    K_global: Optional[np.ndarray] = None
    
    def agregar_nodo(self, nodo):
        self.nodos.append(nodo)

    def agregar_barra(self, barra):
        self.barras.append(barra)

    def agregar_carga_nodal(self, carga):
        self.cargas_nodales.append(carga)

    def agregar_carga(self, carga):
        self.cargas.append(carga)
    
    def ensamble_cargas_equivalentes(self):
        """
        Ensambla los vectores nodales equivalentes (ya en global) de TODAS las barras.
        Suma cada barra en su nodo inicial y final.
        """
        n_nodos = len(self.nodos)
        dof_por_nodo = 6

        # Vector global de fuerzas nodales equivalentes (inicialmente en ceros)
        vector_global = np.zeros(n_nodos * dof_por_nodo)

        for barra in self.barras:
            barra.conversion_local_global()
            # Suponiendo: barra.reaccion_total_global ya es vector 12, ya global
            #f_eq = barra.reaccion_total_global  # O el nombre que usás, pero ya GLOBAL

            # Ids de nodos
            idx_i = (barra.nodo_i - 1) * dof_por_nodo
            idx_j = (barra.nodo_f - 1) * dof_por_nodo

            # Sumo para cada nodo de la barra
            vector_global[idx_i:idx_i+6] += barra.reac_eq_i_global
            vector_global[idx_j:idx_j+6] += barra.reac_eq_f_global

        self.vector_nodal_equivalente = vector_global
        return vector_global
    
    def ensamble_matriz_global(self):
        """
        Ensambla la matriz global de rigidez K para toda la estructura.
        Devuelve la matriz K global (n_nodos*6 x n_nodos*6)
        """
        n_nodos = len(self.nodos)
        dof_por_nodo = 6
        size = n_nodos * dof_por_nodo
        K_global = np.zeros((size, size))

        for barra in self.barras:
            K_b = barra.matriz_rigidez_portico_3d()  # Matriz 12x12, ya en global
            idx_i = (barra.nodo_i - 1) * dof_por_nodo
            idx_j = (barra.nodo_f - 1) * dof_por_nodo

            # Mapear los 12 DOFs de la barra a los DOFs globales
            dofs = [
                idx_i + 0, idx_i + 1, idx_i + 2, idx_i + 3, idx_i + 4, idx_i + 5,
                idx_j + 0, idx_j + 1, idx_j + 2, idx_j + 3, idx_j + 4, idx_j + 5,
            ]

            # Ensamblado (sumar K_b en la K_global)
            for a in range(12):
                for b in range(12):
                    K_global[dofs[a], dofs[b]] += K_b[a, b]
            
            #print(K_b)
            #print()

        self.K_global = K_global
        #print("==========XDXDXD=========")
        #print(K_global)
        return K_global

    def resolver(self, debug=True):
        """
        Resuelve K*D=F eliminando ecuaciones (filas y columnas) con desplazamientos prescritos.
        ¡Debug incluido paso a paso!
        """
        # 1. Ensamblar matrices si hace falta
        if not hasattr(self, "K_global") or self.K_global is None:
            self.ensamble_matriz_global()
        if not hasattr(self, "vector_nodal_equivalente") or self.vector_nodal_equivalente is None:
            self.ensamble_cargas_equivalentes()
        
        K = self.K_global
        F = self.vector_nodal_equivalente.copy()
        ndofs = len(F)
        dof_por_nodo = 6

        # 2. Identificar DOFs fijos (prescritos) y libres
        prescripciones = np.full(ndofs, np.nan)
        for nodo in self.nodos:
            base = (nodo.id - 1) * dof_por_nodo
            if hasattr(nodo, "restricciones") and nodo.restricciones is not None:
                for i in range(dof_por_nodo):
                    if nodo.restricciones[i]:
                        prescripciones[base + i] = nodo.valores_prescritos[i]
        idx_fijos = np.where(~np.isnan(prescripciones))[0]
        idx_libres = np.where(np.isnan(prescripciones))[0]
        if debug:
            print("\n--- Debug de restricciones ---")
            print("Prescripciones:", prescripciones)
            print("Índices fijos:", idx_fijos)
            print("Índices libres:", idx_libres)

        # 3. Formar el sistema reducido: Kll * Dl = Fl
        Kll = K[np.ix_(idx_libres, idx_libres)]
        Fl = F[idx_libres]
        if debug:
            print("\n--- Sistema reducido ---")
            print("Kll:\n", Kll)
            print("Fl:\n", Fl)
            print("Shape de Kll:", Kll.shape)

        # 4. Resolver el sistema reducido
        Dl = np.linalg.solve(Kll, Fl)
        if debug:
            print("\n--- Solución de desplazamientos libres ---")
            print("Dl (libres):", Dl)

        # 5. Armar el vector de desplazamientos globales
        D = np.zeros(ndofs)
        D[idx_libres] = Dl
        D[idx_fijos] = prescripciones[idx_fijos]
        if debug:
            print("\n--- Vector de desplazamientos global D ---")
            print(D)

        self.desplazamientos = D
        return D

    def calcular_reacciones(self):
        """
        Calcula las reacciones en los grados de libertad restringidos de la estructura.
        Guarda el vector de reacciones en self.reacciones.
        """
        if self.desplazamientos is None:
            raise ValueError("Primero debés resolver el sistema (llamá a .resolver())")

        K = self.K_global
        F = self.vector_nodal_equivalente
        D = self.desplazamientos

        ndofs = len(D)
        dof_por_nodo = 6
        prescripciones = np.full(ndofs, np.nan)

        for nodo in self.nodos:
            base = (nodo.id - 1) * dof_por_nodo
            if hasattr(nodo, "restricciones") and nodo.restricciones is not None:
                for i in range(dof_por_nodo):
                    if nodo.restricciones[i]:
                        prescripciones[base + i] = nodo.valores_prescritos[i]

        idx_fijos = np.where(~np.isnan(prescripciones))[0]

        # Debug Prints
        print("==== DEBUG REACCIONES ====")
        print("Restricciones nodales (indices fijos):", idx_fijos)
        print("Prescripciones:", prescripciones)
        print("K_global:\n", K)
        print("Desplazamientos D:\n", D)
        print("F (vector nodal equivalente):\n", F)
        print("==========================")

        F_interna = K @ D

        print("K·D (fuerzas internas):\n", F_interna)

        reacciones = np.zeros_like(D)
        reacciones[idx_fijos] = F_interna[idx_fijos] - F[idx_fijos]

        print("Reacciones (solo fijos):\n", reacciones)
        print("==========================")

        self.reacciones = reacciones
        return reacciones