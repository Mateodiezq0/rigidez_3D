import pytest
from core.carga_puntual import CargaPuntual

def test_carga_constructor_basico():
    carga = CargaPuntual(1, 0, 0, 0, 10)
    assert carga.id == 1
    assert carga.x == 0
    assert carga.y == 0
    assert carga.z == 0
    assert carga.q == 10
    assert carga.alpha_x == 0.0
    assert carga.alpha_y == 0.0
    assert carga.alpha_z == 0.0

def test_carga_coordenadas_positivas():
    carga = CargaPuntual(2, 1.5, 2.5, 3.5, -5)
    assert carga.x == 1.5
    assert carga.y == 2.5
    assert carga.z == 3.5
    assert carga.q == -5  # sentido negativo

def test_carga_angulos():
    carga = CargaPuntual(3, 2, 2, 2, 15, alpha_x=30, alpha_y=60, alpha_z=90)
    assert carga.alpha_x == 30
    assert carga.alpha_y == 60
    assert carga.alpha_z == 90

def test_carga_direccion_pura_x():
    carga = CargaPuntual(4, 0, 0, 0, 12, alpha_x=0, alpha_y=90, alpha_z=90)
    assert carga.alpha_x == 0  # Apunta sobre eje X

def test_carga_direccion_pura_y():
    carga = CargaPuntual(5, 0, 0, 0, 13, alpha_x=90, alpha_y=0, alpha_z=90)
    assert carga.alpha_y == 0  # Apunta sobre eje Y

def test_carga_direccion_pura_z():
    carga = CargaPuntual(6, 0, 0, 0, 14, alpha_x=90, alpha_y=90, alpha_z=0)
    assert carga.alpha_z == 0  # Apunta sobre eje Z

def test_carga_sentido_positivo_negativo():
    carga_up = CargaPuntual(7, 0, 0, 0, 10)
    carga_down = CargaPuntual(8, 0, 0, 0, -10)
    assert carga_up.q > 0
    assert carga_down.q < 0

def test_carga_varios_parametros():
    carga = CargaPuntual(9, 5, -3, 2.2, 20, alpha_x=45, alpha_y=45, alpha_z=0)
    assert carga.x == 5
    assert carga.y == -3
    assert carga.z == 2.2
    assert carga.q == 20
    assert carga.alpha_x == 45
    assert carga.alpha_y == 45
    assert carga.alpha_z == 0

# Opcional: test para errores o valores por defecto
def test_carga_por_defecto_angulos():
    carga = CargaPuntual(10, 0, 0, 0, 1)
    assert carga.alpha_x == 0.0
    assert carga.alpha_y == 0.0
    assert carga.alpha_z == 0.0

