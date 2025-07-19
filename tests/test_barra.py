# tests/test_barra.py

import pytest
from core.nodos import Nodo
from core.barra import Barra
import numpy as np

def test_constructor_basico():
    barra = Barra(
        id=101,
        nodo_i=1,
        nodo_f=2,
        E=21000,
        I_x=12.3,
        I_y=45.6,
        I_z=78.9,
        G=8000,
        J=111.2,
        L=6.28,
        #tita=90,
        nodo_i_obj=None,
        nodo_f_obj=None,

    )
    assert barra.id == 101
    assert barra.nodo_i == 1
    assert barra.nodo_f == 2
    assert barra.E == 21000
    assert barra.I_x == 12.3
    assert barra.I_y == 45.6
    assert barra.I_z == 78.9
    assert barra.G == 8000
    assert barra.J == 111.2
    assert barra.L == 6.28
    #assert barra.tita == 90
    assert barra.nodo_i_obj is None
    assert barra.nodo_f_obj is None



def test_barra_horizontal_x():
    n1 = Nodo(1, 0, 0, 0)
    n2 = Nodo(2, 5, 0, 0)
    barra = Barra(id=1, nodo_i=1, nodo_f=2, E=1, I_x=1, I_y=1, I_z=1, G=1, J=1, nodo_i_obj=n1, nodo_f_obj=n2, tita=0)
    barra.calcular_longitud_y_bases()
    assert np.isclose(barra.L, 5)
    assert np.allclose(barra.z_local, [1, 0, 0])  # Va sobre X
    assert np.allclose(barra.x_local, [0, 1, 0])  # Xlocal apunta a Y
    assert np.allclose(barra.y_local, [0, 0, 1])  # Ylocal apunta a Z

def test_barra_vertical_z():
    n1 = Nodo(1, 0, 0, 0)
    n2 = Nodo(2, 0, 0, 7)
    barra = Barra(id=1, nodo_i=1, nodo_f=2, E=1, I_x=1, I_y=1, I_z=1, G=1, J=1, nodo_i_obj=n1, nodo_f_obj=n2, tita=0)
    barra.calcular_longitud_y_bases()
    assert np.isclose(barra.L, 7)
    assert np.allclose(barra.z_local, [0, 0, 1])  # Va sobre Z
    assert np.allclose(barra.x_local, [1, 0, 0])  # Xlocal apunta a X
    assert np.allclose(barra.y_local, [0, 1, 0])  # Ylocal apunta a Y

def test_barra_inclinada_y_tita_0():
    n1 = Nodo(1, 0, 0, 0)
    n2 = Nodo(2, 2, 2, 0)
    barra = Barra(id=1, nodo_i=1, nodo_f=2, E=1, I_x=1, I_y=1, I_z=1, G=1, J=1, nodo_i_obj=n1, nodo_f_obj=n2, tita=0)
    barra.calcular_longitud_y_bases()
    assert np.isclose(barra.L, np.sqrt(8))
    # z_local debe ser (1/sqrt(2), 1/sqrt(2), 0)
    assert np.allclose(barra.z_local, [1/np.sqrt(2), 1/np.sqrt(2), 0])
    # x_local y y_local deben ser ortogonales y unitarios
    assert np.isclose(np.dot(barra.x_local, barra.z_local), 0)
    assert np.isclose(np.dot(barra.y_local, barra.z_local), 0)
    assert np.isclose(np.linalg.norm(barra.x_local), 1)
    assert np.isclose(np.linalg.norm(barra.y_local), 1)


def test_barra_giro_tita_90():
    n1 = Nodo(1, 0, 0, 0)
    n2 = Nodo(2, 2, 0, 0)
    barra = Barra(id=1, nodo_i=1, nodo_f=2, E=1, I_x=1, I_y=1, I_z=1, G=1, J=1, nodo_i_obj=n1, nodo_f_obj=n2, tita=90)
    barra.calcular_longitud_y_bases()
    # Sin giro, x_local=[0,1,0] y y_local=[0,0,1]
    # Con tita=90°, x_local debe coincidir con y_local original y viceversa, pero con signo
    assert np.allclose(barra.z_local, [1,0,0])
    assert np.allclose(barra.x_local, [0,0,1], atol=1e-8)  # Ahora el Xlocal apunta a Z
    assert np.allclose(barra.y_local, [0,-1,0], atol=1e-8)  # Ylocal apunta a -Y



def test_barra_giro_tita_45():
    n1 = Nodo(1, 0, 0, 0)
    n2 = Nodo(2, 0, 5, 0)
    barra = Barra(id=1, nodo_i=1, nodo_f=2, E=1, I_x=1, I_y=1, I_z=1, G=1, J=1, nodo_i_obj=n1, nodo_f_obj=n2, tita=45)
    barra.calcular_longitud_y_bases()
    # x_local debería ser combinación de [1,0,0] y [0,0,1]
    # y_local = [0,1,0] debería rotar 45°
    assert np.isclose(barra.L, 5)
    assert np.allclose(barra.z_local, [0,1,0])
    # Verifica ortogonalidad y norma
    assert np.isclose(np.dot(barra.x_local, barra.z_local), 0)
    assert np.isclose(np.dot(barra.y_local, barra.z_local), 0)
    assert np.isclose(np.linalg.norm(barra.x_local), 1)
    assert np.isclose(np.linalg.norm(barra.y_local), 1)