# tests/test_nodos.py

import numpy as np
import pytest
from core.nodos import Nodo

def test_nodo_constructor_basico():
    nodo = Nodo(id=1, x=1.0, y=2.0, z=3.0)
    assert nodo.id == 1
    assert nodo.x == 1.0
    assert nodo.y == 2.0
    assert nodo.z == 3.0
    # Restricciones por defecto: todos libres
    assert nodo.restricciones == [False, False, False, False, False, False]
    # Valores prescritos por defecto: ceros
    assert nodo.valores_prescritos == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

def test_get_coord_devuelve_np_array_correcto():
    nodo = Nodo(id=5, x=-5.2, y=10.0, z=42.0)
    coords = nodo.get_coord()
    assert isinstance(coords, np.ndarray)
    assert np.allclose(coords, [-5.2, 10.0, 42.0])

def test_restricciones_personalizadas():
    nodo = Nodo(
        id=9,
        x=0,
        y=0,
        z=0,
        restricciones=[True, True, False, False, True, False],
        valores_prescritos=[1, 2, 3, 4, 5, 6]
    )
    assert nodo.restricciones == [True, True, False, False, True, False]
    assert nodo.valores_prescritos == [1, 2, 3, 4, 5, 6]

def test_modificacion_valores_prescritos():
    nodo = Nodo(id=7, x=0, y=0, z=0)
    nodo.valores_prescritos[2] = 42.0
    assert nodo.valores_prescritos[2] == 42.0

def test_tamano_vectores_de_restricciones():
    # Asegurarse que sean siempre de largo 6 (3 trans, 3 rot)
    nodo = Nodo(id=123, x=0, y=0, z=0)
    assert len(nodo.restricciones) == 6
    assert len(nodo.valores_prescritos) == 6
