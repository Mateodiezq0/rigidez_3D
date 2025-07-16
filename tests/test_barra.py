# tests/test_barra.py

import pytest
from core.nodos import Nodo
from core.barra import Barra

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
        beta_x=None,
        beta_y=None,
        beta_z=None
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
    assert barra.beta_x is None
    assert barra.beta_y is None
    assert barra.beta_z is None


def test_calcular_longitud_y_angulos():
    n1 = Nodo(id=1, x=0, y=0, z=0)
    n2 = Nodo(id=2, x=3, y=4, z=12)

    barra = Barra(
        id=2, nodo_i=1, nodo_f=2, E=21000, I_x=10, I_y=20, I_z=30,
        G=7000, J=5, nodo_i_obj=n1, nodo_f_obj=n2
    )
    # Calcular longitud y ángulos
    barra.calcular_longitud_y_angulos()

    # Distancia 3D: sqrt(3^2 + 4^2 + 12^2) = 13
    assert barra.L == pytest.approx(13.0)

    # Ángulo en XY: atan2(4,3) ≈ 53.13°
    #assert barra.tita == pytest.approx(53.13, rel=1e-2)

    # Beta_x: atan2(12, 5) ≈ 67.38°
    assert barra.beta_x == pytest.approx(76.66, rel=1e-2)

    # Beta_y: atan2(3, sqrt(4^2+12^2)) ≈ 13.89°
    assert barra.beta_y == pytest.approx(72.07, rel=1e-2)

    # Beta_z: atan2(4, sqrt(3^2+12^2)) ≈ 18.43°
    assert barra.beta_z == pytest.approx(22.62, rel=1e-2)