from data.entrada.cargarBarra import *
from data.entrada.cargarCargaPuntual import *
from data.entrada.cargarNodo import *
from core.estructura import Estructura

nodos = leer_nodos()

barras = leer_barras()

cargas = leer_cargas()

estructura = Estructura() 

estructura.cargar_estructura(nodos,barras,cargas)

print("Nodos: ",nodos)
print()
print("Barras: ",barras)
print()
print("Cargas: ",cargas)