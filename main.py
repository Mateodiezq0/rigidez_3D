from data.entrada.cargarBarra import *
from data.entrada.cargarCargaPuntual import *
from data.entrada.cargarNodo import *

nodos = leer_nodos()

barras = leer_barras()

cargas = leer_cargas()

unir_barras_nodos(barras,nodos)

print("Nodos: ",nodos)
print()
print("Barras: ",barras)
print()
print("Cargas: ",cargas)