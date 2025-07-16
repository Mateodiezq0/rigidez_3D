from core.nodos import Nodo
from core.barra import Barra
import numpy as np

n1 = Nodo(1, 1, 1, 0)
n2 = Nodo(2, 6, 9.66, 0)
barra = Barra(id=1, nodo_i=1, nodo_f=2, E=1, I_x=1, I_y=1, I_z=1, G=1, J=1, nodo_i_obj=n1, nodo_f_obj=n2, tita=70)
barra.calcular_longitud_y_bases()
# Sin giro, x_local=[0,1,0] y y_local=[0,0,1]
# Con tita=90°, x_local debe coincidir con y_local original y viceversa, pero con signo
#assert np.allclose(barra.z_local, [1,0,0])
#assert np.allclose(barra.x_local, [0,0,1], atol=1e-8)  # Ahora el Xlocal apunta a Z
#assert np.allclose(barra.y_local, [0,-1,0], atol=1e-8)  # Ylocal apunta a -Y

print("Tita:", barra.tita)
print("Lambda X:", barra.lambda_x)
print("Lambda Y:", barra.lambda_y)
print("Lambda Z:", barra.lambda_z)
print("X Local:", barra.x_local)
print("Y Local:", barra.y_local)
print("Z Local:", barra.z_local)
