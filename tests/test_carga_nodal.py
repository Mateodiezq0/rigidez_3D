# tests/test_carga_nodal.py

import numpy as np
import pytest
from core import carga_nodal
from core.carga_nodal import CargaNodal

def test_constructor_por_defecto():
    carga = CargaNodal(nodo_id=1)
    assert carga.nodo_id == 1
    assert carga.fx == 0.0
    assert carga.fy == 0.0
    assert carga.fz == 0.0
    assert carga.mx == 0.0
    assert carga.my == 0.0
    assert carga.mz == 0.0

def test_constructor_valores_personalizados():
    carga = CargaNodal(
        nodo_id=5,
        fx=10.0,
        fy=-2.5,
        fz=7.0,
        mx=0.1,
        my=0.2,
        mz=0.3
    )
    assert carga.nodo_id == 5
    assert carga.fx == 10.0
    assert carga.fy == -2.5
    assert carga.fz == 7.0
    assert carga.mx == 0.1
    assert carga.my == 0.2
    assert carga.mz == 0.3

def test_vector_devuelve_np_array_correcto():
    carga = CargaNodal(2, fx=1, fy=2, fz=3, mx=4, my=5, mz=6)
    vec = carga.vector()
    assert isinstance(vec, np.ndarray)
    assert np.allclose(vec, [1, 2, 3, 4, 5, 6])


def test_modificacion_componentes():
    carga = CargaNodal(9)
    carga.fz = -42.0
    carga.mx = 3.14
    assert carga.fz == -42.0
    assert carga.mx == 3.14

