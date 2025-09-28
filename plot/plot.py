import sys
import os
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # Usar backend que mantiene ventana abierta
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import pandas as pd

# Asegurarse que se puede importar core.*
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.nodos import Nodo
from core.barra import Barra
from core.carga_nodal import CargaNodal
from core.carga_puntual import CargaPuntual
from core.estructura import Estructura

def leer_datos_excel(archivo_excel='data/Datos_template.xlsx'):
    """Lee los datos de nodos y barras desde un archivo Excel"""
    try:
        # Leer las hojas del Excel
        df_nodos = pd.read_excel(archivo_excel, sheet_name='Nodo')
        df_barras = pd.read_excel(archivo_excel, sheet_name='Barra')
        
        # Crear diccionario de nodos
        nodos = {}
        for _, row in df_nodos.iterrows():
            nodo_id = int(row['id'])
            nodo = Nodo(nodo_id, row['x'], row['y'], row['z'])
            
            # Configurar restricciones
            restricciones = [
                row['restriccion_UX'], row['restriccion_UY'], row['restriccion_UZ'],
                row['restriccion_RX'], row['restriccion_RY'], row['restriccion_RZ']
            ]
            nodo.restricciones = restricciones
            
            # Configurar valores prescritos
            valores_prescritos = [
                row['valor_prescrito_UX'], row['valor_prescrito_UY'], row['valor_prescrito_UZ'],
                row['valor_prescrito_RX'], row['valor_prescrito_RY'], row['valor_prescrito_RZ']
            ]
            nodo.valores_prescritos = valores_prescritos
            
            # Agregar deformaciones como atributo adicional
            nodo.deformaciones = [
                row['deformacion_UX'], row['deformacion_UY'], row['deformacion_UZ'],
                row['deformacion_RX'], row['deformacion_RY'], row['deformacion_RZ']
            ]
            
            nodos[nodo_id] = nodo
        
        # Crear lista de barras
        barras = []
        for _, row in df_barras.iterrows():
            barra = Barra(
                id=int(row['id']),
                nodo_i=int(row['Nodo_inicial']),
                nodo_f=int(row['Nodo_Final']),
                E=row['E [Módulo de elasticidad] [t/cm2]'],
                A=row['A [área]'],
                I_y=row['Inercia en Y [cm4]'],
                I_z=row['Inercia en X [cm4]'],
                G=row['G [Módulo de elasticidad transversal] [t/cm2]'],
                J=row['J [Módulo de Torsión] [cm3]'],
                tita=row['Tita [grados]'],
                nodo_i_obj=nodos[int(row['Nodo_inicial'])],
                nodo_f_obj=nodos[int(row['Nodo_Final'])]
            )
            barras.append(barra)
        
        return nodos, barras
        
    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}")
        return crear_estructura_ejemplo()

def crear_estructura_con_cargas():
    """Crea una estructura con cargas siguiendo el flujo de Prueba_1.py"""
# --- Crear nodos ---
    nodo_i = Nodo(id=1, x=0, y=0, z=0, restricciones=[True, True, True, True, True, True])
    nodo_j = Nodo(id=2, x=0, y=500, z=0, restricciones=[False, False, False, False, False, False])
    nodo_k = Nodo(id=3, x=1000, y=500, z=0, restricciones=[False, False, False, False, False, False])
    nodo_l = Nodo(id=4, x=1000, y=0, z=0, restricciones=[True, True, True, True, True, True])
    
    nodos = {1: nodo_i, 2: nodo_j, 3: nodo_k, 4: nodo_l}
    
    # --- Crear barras ---
    barra1 = Barra(
        id=1, nodo_i=1, nodo_f=2, E=10, I_y=120000, I_z=1000, G=80.77, J=2,
        A=1, tita=0, nodo_i_obj=nodo_i, nodo_f_obj=nodo_j
    )
    barra2 = Barra(
        id=2, nodo_i=2, nodo_f=3, E=10, I_y=120000, I_z=1000, G=80.77, J=2,
        A=1, tita=90, nodo_i_obj=nodo_j, nodo_f_obj=nodo_k
    )
    barra3 = Barra(
        id=3, nodo_i=3, nodo_f=4, E=10, I_y=12000, I_z=10000, G=80.77, J=2,
        A=1, tita=0, nodo_i_obj=nodo_k, nodo_f_obj=nodo_l
    )
    
    barras = [barra1, barra2, barra3]
    
    # --- Crear cargas ---
    carga1 = CargaPuntual(id=1, x=0, y=300, z=0, q=0.707, alpha_x=45, alpha_y=-45, alpha_z=90)
    carga2 = CargaPuntual(id=2, x=200, y=500, z=0, q=-1.0, alpha_x=60, alpha_y=-30, alpha_z=90)
    carga3 = CargaPuntual(id=3, x=500, y=500, z=0, q=-0.8, alpha_x=90, alpha_y=0, alpha_z=90)
    carga4 = CargaPuntual(id=4, x=900, y=500, z=0, q=1.0, alpha_x=60, alpha_y=-30, alpha_z=90)
    carga5 = CargaPuntual(id=5, x=1000, y=100, z=0, q=0.707, alpha_x=45, alpha_y=-45, alpha_z=90)
    cargaNodal1 = CargaNodal(nodo_id=2, fx=0, fy=0, fz=0, mx=0, my=0, mz=100)
    
    # --- Aplicar cargas a barras ---
    barra1.añadirCarga(carga1)
    barra2.añadirCarga(carga2)
    barra2.añadirCarga(carga3)
    barra2.añadirCarga(carga4)
    barra3.añadirCarga(carga5)
    
    # --- Crear estructura y calcular deformaciones ---
    estructura = Estructura()
    estructura.agregar_barra(barra1)
    estructura.agregar_barra(barra2)
    estructura.agregar_barra(barra3)
    estructura.agregar_nodo(nodo_i)
    estructura.agregar_nodo(nodo_j)
    estructura.agregar_nodo(nodo_k)
    estructura.agregar_nodo(nodo_l)
    estructura.agregar_carga_nodal(cargaNodal1)
    
    # --- Calcular deformaciones reales ---
    try:
        D = estructura.resolver_desplazamientos()
        print("Deformaciones calculadas exitosamente")
        print(f"Vector de desplazamientos: {D.flatten()}")
        
        # Asignar deformaciones a los nodos
        for i, nodo in enumerate(nodos.values()):
            if i * 6 + 5 < len(D):
                deformaciones = D[i*6:(i+1)*6].flatten()
                nodo.deformaciones = deformaciones.tolist()
                print(f"Nodo {nodo.id} deformaciones: {deformaciones}")
            else:
                nodo.deformaciones = [0.0] * 6
        
        # Calcular deformaciones de barras (esfuerzos internos)
        print("\n--- DEFORMACIONES DE BARRAS ---")
        for barra in barras:
            try:
                # Obtener desplazamientos de los nodos de la barra
                nodo_i_idx = list(nodos.keys()).index(barra.nodo_i)
                nodo_f_idx = list(nodos.keys()).index(barra.nodo_f)
                
                # Desplazamientos en coordenadas globales
                u_global = np.zeros(12)
                u_global[:6] = D[nodo_i_idx*6:(nodo_i_idx+1)*6]
                u_global[6:] = D[nodo_f_idx*6:(nodo_f_idx+1)*6]
                
                # Calcular esfuerzos internos usando la matriz de rigidez global
                K_global = barra.Kglobal()
                f_global = K_global @ u_global
                
                # Extraer esfuerzos significativos (valores en nodo inicial)
                esfuerzos = {
                    'axial_i': f_global[0],      # Fuerza axial en nodo inicial
                    'cortante_y_i': f_global[1], # Cortante Y en nodo inicial
                    'cortante_z_i': f_global[2], # Cortante Z en nodo inicial
                    'momento_x_i': f_global[3],  # Momento X en nodo inicial
                    'momento_y_i': f_global[4],  # Momento Y en nodo inicial
                    'momento_z_i': f_global[5],  # Momento Z en nodo inicial
                    'axial_f': f_global[6],      # Fuerza axial en nodo final
                    'cortante_y_f': f_global[7], # Cortante Y en nodo final
                    'cortante_z_f': f_global[8], # Cortante Z en nodo final
                    'momento_x_f': f_global[9],  # Momento X en nodo final
                    'momento_y_f': f_global[10], # Momento Y en nodo final
                    'momento_z_f': f_global[11]  # Momento Z en nodo final
                }
                
                # Asignar esfuerzos a la barra
                barra.esfuerzos = esfuerzos
                
                print(f"Barra {barra.id} (Nodo {barra.nodo_i} → Nodo {barra.nodo_f}):")
                print(f"  Fuerza Axial: {esfuerzos['axial_i']:.2f} t")
                print(f"  Cortante Y: {esfuerzos['cortante_y_i']:.2f} t")
                print(f"  Cortante Z: {esfuerzos['cortante_z_i']:.2f} t")
                print(f"  Momento X: {esfuerzos['momento_x_i']:.2f} t·cm")
                print(f"  Momento Y: {esfuerzos['momento_y_i']:.2f} t·cm")
                print(f"  Momento Z: {esfuerzos['momento_z_i']:.2f} t·cm")
                print()
                
            except Exception as e:
                print(f"Error al calcular esfuerzos de barra {barra.id}: {e}")
                # Asignar esfuerzos de ejemplo para visualización
                barra.esfuerzos = {
                    'axial_i': 10.0, 'cortante_y_i': 5.0, 'cortante_z_i': 0.0,
                    'momento_x_i': 0.0, 'momento_y_i': 0.0, 'momento_z_i': 50.0,
                    'axial_f': -10.0, 'cortante_y_f': -5.0, 'cortante_z_f': 0.0,
                    'momento_x_f': 0.0, 'momento_y_f': 0.0, 'momento_z_f': -50.0
                }
                
    except Exception as e:
        print(f"Error al calcular deformaciones: {e}")
        # Asignar deformaciones de ejemplo si falla el cálculo
        for nodo in nodos.values():
            nodo.deformaciones = [0.0] * 6
        for barra in barras:
            barra.esfuerzos = {}
    
    return nodos, barras, estructura

# Función crear_estructura_ejemplo() eliminada - no se usa

def graficar_estructura(nodos, barras, mostrar_gdl=True, mostrar_info=True, mostrar_deformaciones=True, factor_amplificacion=10):
    """
    Grafica la estructura 3D con nodos y barras, opcionalmente con deformaciones
    Optimizado para mejor rendimiento
    
    Args:
        nodos: Diccionario de nodos
        barras: Lista de barras
        mostrar_gdl: Si mostrar información de grados de libertad
        mostrar_info: Si mostrar información adicional
        mostrar_deformaciones: Si mostrar las deformaciones
        factor_amplificacion: Factor para amplificar las deformaciones visualmente
    """
    # Configurar matplotlib para mejor rendimiento
    plt.ion()  # Modo interactivo
    fig = plt.figure(figsize=(15, 10))
    
    if mostrar_deformaciones:
        # Crear subplots para comparar estructura original vs deformada
        ax1 = fig.add_subplot(121, projection='3d')
        ax2 = fig.add_subplot(122, projection='3d')
        axes = [ax1, ax2]
        titulos = ['Estructura Original', 'Estructura Deformada']
    else:
        ax = fig.add_subplot(111, projection='3d')
        axes = [ax]
        titulos = ['Estructura 3D - Nodos y Barras']
    
    # Pre-calcular coordenadas para optimización
    coords_originales = np.array([nodo.get_coord() for nodo in nodos.values()])
    coords_deformadas = np.array([nodo.get_coord() + np.array(nodo.deformaciones[:3]) * factor_amplificacion 
                                 for nodo in nodos.values()])
    
    for idx, ax in enumerate(axes):
        # Configurar ejes para mejor rendimiento
        ax.grid(False)  # Desactivar grid para mejor rendimiento
        ax.set_facecolor('white')
        
        # --- Dibujar barras de forma optimizada ---
        lineas = []
        colores_barras = []
        
        for barra in barras:
            if idx == 0:  # Estructura original
                p1 = coords_originales[list(nodos.keys()).index(barra.nodo_i)]
                p2 = coords_originales[list(nodos.keys()).index(barra.nodo_f)]
                color = 'blue'
            else:  # Estructura deformada
                p1 = coords_deformadas[list(nodos.keys()).index(barra.nodo_i)]
                p2 = coords_deformadas[list(nodos.keys()).index(barra.nodo_f)]
                color = 'red'
            
            lineas.append([p1, p2])
            colores_barras.append(color)
        
        if lineas:
            lc = Line3DCollection(lineas, colors=colores_barras, linewidths=2, alpha=0.8)
            ax.add_collection3d(lc)
        
        # --- Dibujar nodos de forma optimizada ---
        coords_actuales = coords_originales if idx == 0 else coords_deformadas
        colores_nodos = []
        tamanos_nodos = []
        
        for i, nodo in enumerate(nodos.values()):
            if any(nodo.restricciones):
                colores_nodos.append('red')
                tamanos_nodos.append(80)
            else:
                colores_nodos.append('green')
                tamanos_nodos.append(60)
        
        # Dibujar todos los nodos de una vez
        ax.scatter(coords_actuales[:, 0], coords_actuales[:, 1], coords_actuales[:, 2], 
                  c=colores_nodos, s=tamanos_nodos, alpha=0.8)
        
        # --- Etiquetas de nodos (solo si es necesario) ---
        if len(nodos) <= 10:  # Solo mostrar etiquetas si hay pocos nodos
            for i, nodo in enumerate(nodos.values()):
                coord = coords_actuales[i]
                ax.text(coord[0], coord[1], coord[2] + 50, f'N{nodo.id}', 
                       fontsize=8, ha='center', va='bottom')
        
        # --- Mostrar información de GDL (solo en estructura original) ---
        if mostrar_gdl and idx == 0 and len(nodos) <= 6:
            gdl_nombres = ['UX', 'UY', 'UZ', 'RX', 'RY', 'RZ']
            for i, nodo in enumerate(nodos.values()):
                coord = coords_actuales[i]
                gdl_info = []
                
                for j, (restr, valor) in enumerate(zip(nodo.restricciones, nodo.valores_prescritos)):
                    if restr:
                        gdl_info.append(f"{gdl_nombres[j]}={valor}")
                
                if gdl_info:
                    info_text = f"Restr: {', '.join(gdl_info[:2])}"  # Solo 2 para no saturar
                    ax.text(coord[0], coord[1], coord[2] - 100, info_text, 
                           fontsize=7, ha='center', va='top', 
                           bbox=dict(boxstyle="round,pad=0.2", facecolor='yellow', alpha=0.7))
        
        # --- Configurar ejes ---
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel('Z (mm)')
        ax.set_title(titulos[idx], fontsize=11, fontweight='bold')
        
        # Ajustar límites de los ejes de forma optimizada
        margin = max(100, np.max(coords_actuales) * 0.1)
        ax.set_xlim(coords_actuales[:, 0].min() - margin, coords_actuales[:, 0].max() + margin)
        ax.set_ylim(coords_actuales[:, 1].min() - margin, coords_actuales[:, 1].max() + margin)
        ax.set_zlim(coords_actuales[:, 2].min() - margin, coords_actuales[:, 2].max() + margin)

        # --- Leyenda simplificada ---
        from matplotlib.patches import Patch
        if idx == 0:
            legend_elements = [
                Patch(facecolor='green', label='Nodo Libre'),
                Patch(facecolor='red', label='Nodo Restringido'),
                Patch(facecolor='blue', label='Barra Original')
            ]
        else:
            legend_elements = [
                Patch(facecolor='green', label='Nodo Libre'),
                Patch(facecolor='red', label='Nodo Restringido'),
                Patch(facecolor='red', label='Barra Deformada')
            ]
        ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1), fontsize=8)

    # --- Información adicional ---
    if mostrar_info:
        info_text = f"""Nodos: {len(nodos)} | Barras: {len(barras)} | Amplificación: {factor_amplificacion}x"""
        ax.text2D(0.02, 0.02, info_text, transform=ax.transAxes, 
                 fontsize=9, verticalalignment='bottom',
                 bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.show(block=True)  # Mostrar y mantener abierta la ventana

def dibujar_diagrama_cortante(ax, base_start, base_end, barra, factor_escala=0.1, direccion=None):
    """Dibuja el diagrama de cortante (DFC) en una barra con amplitud sobre un eje fijo."""
    if not hasattr(barra, 'esfuerzos') or not barra.esfuerzos:
        print(f"  Barra {barra.id}: No tiene esfuerzos")
        return None

    cortante_i = barra.esfuerzos.get('cortante_y_i', 0.0)
    cortante_f = barra.esfuerzos.get('cortante_y_f', 0.0)

    print(f"  DFC Barra {barra.id}: {cortante_i:.3f} -> {cortante_f:.3f}")

    if abs(cortante_i) < 0.001 and abs(cortante_f) < 0.001:
        print(f"  DFC Barra {barra.id}: Esfuerzos muy pequeños, no se dibuja")
        return None

    base_start = np.asarray(base_start, dtype=float)
    base_end = np.asarray(base_end, dtype=float)

    if direccion is None:
        direccion = np.array([0.0, 0.0, 1.0])
    direccion = np.asarray(direccion, dtype=float)
    if np.linalg.norm(direccion) < 1e-6:
        direccion = np.array([0.0, 0.0, 1.0])
    direccion = direccion / np.linalg.norm(direccion)

    punto_i = base_start + direccion * cortante_i * factor_escala
    punto_f = base_end + direccion * cortante_f * factor_escala

    lineas = []
    linea_base, = ax.plot([base_start[0], base_end[0]], [base_start[1], base_end[1]], [base_start[2], base_end[2]],
                          color='r', linestyle='--', linewidth=1, alpha=0.3)
    lineas.append(linea_base)

    linea_principal, = ax.plot([punto_i[0], punto_f[0]], [punto_i[1], punto_f[1]], [punto_i[2], punto_f[2]],
                                'r-', linewidth=3, alpha=0.8)
    lineas.append(linea_principal)

    conector_i, = ax.plot([base_start[0], punto_i[0]], [base_start[1], punto_i[1]], [base_start[2], punto_i[2]],
                          'r-', linewidth=1, alpha=0.6)
    conector_f, = ax.plot([base_end[0], punto_f[0]], [base_end[1], punto_f[1]], [base_end[2], punto_f[2]],
                          'r-', linewidth=1, alpha=0.6)
    lineas.extend([conector_i, conector_f])
    return lineas


def dibujar_diagrama_momento(ax, base_start, base_end, barra, factor_escala=0.01, direccion=None):
    """Dibuja el diagrama de momento flector (DMF) en una barra con amplitud sobre un eje fijo."""
    if not hasattr(barra, 'esfuerzos') or not barra.esfuerzos:
        print(f"  Barra {barra.id}: No tiene esfuerzos")
        return None

    momento_i = barra.esfuerzos.get('momento_z_i', 0.0)
    momento_f = barra.esfuerzos.get('momento_z_f', 0.0)

    print(f"  DMF Barra {barra.id}: {momento_i:.3f} -> {momento_f:.3f}")

    if abs(momento_i) < 0.1 and abs(momento_f) < 0.1:
        print(f"  DMF Barra {barra.id}: Momentos muy pequeños, no se dibuja")
        return None

    base_start = np.asarray(base_start, dtype=float)
    base_end = np.asarray(base_end, dtype=float)

    if direccion is None:
        direccion = np.array([0.0, 0.0, 1.0])
    direccion = np.asarray(direccion, dtype=float)
    if np.linalg.norm(direccion) < 1e-6:
        direccion = np.array([0.0, 0.0, 1.0])
    direccion = direccion / np.linalg.norm(direccion)

    punto_i = base_start + direccion * momento_i * factor_escala
    punto_f = base_end + direccion * momento_f * factor_escala

    lineas = []
    linea_base, = ax.plot([base_start[0], base_end[0]], [base_start[1], base_end[1]], [base_start[2], base_end[2]],
                          color='b', linestyle='--', linewidth=1, alpha=0.3)
    lineas.append(linea_base)

    linea_principal, = ax.plot([punto_i[0], punto_f[0]], [punto_i[1], punto_f[1]], [punto_i[2], punto_f[2]],
                                'b-', linewidth=3, alpha=0.8)
    lineas.append(linea_principal)

    conector_i, = ax.plot([base_start[0], punto_i[0]], [base_start[1], punto_i[1]], [base_start[2], punto_i[2]],
                          'b-', linewidth=1, alpha=0.6)
    conector_f, = ax.plot([base_end[0], punto_f[0]], [base_end[1], punto_f[1]], [base_end[2], punto_f[2]],
                          'b-', linewidth=1, alpha=0.6)
    lineas.extend([conector_i, conector_f])
    return lineas

def trazar_barras(ax, barras, nodos, color='tab:blue', linewidth=3, alpha=0.9, etiqueta=None):
    """Dibuja la estructura (barras) en 3D usando las coordenadas originales."""
    artistas = []
    for barra in barras:
        p1 = barra.nodo_i_obj.get_coord()
        p2 = barra.nodo_f_obj.get_coord()
        (linea,) = ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]],
                           color=color, linewidth=linewidth, alpha=alpha, label=etiqueta)
        artistas.append(linea)
        etiqueta = None  # Solo mostrar una entrada en la leyenda
    return artistas

def trazar_nodos(ax, nodos, color_restringido='firebrick', color_libre='darkgreen'):
    """Dibuja nodos con colores según restricción."""
    artistas = []
    for nodo in nodos.values():
        x, y, z = nodo.get_coord()
        color = color_restringido if any(nodo.restricciones) else color_libre
        punto = ax.scatter(x, y, z, s=80, color=color)
        etiqueta = ax.text(x, y, z + 50, f"N{nodo.id}", va='bottom', ha='center', fontsize=9)
        artistas.append((punto, etiqueta))
    return artistas

def calcular_offset_superior(barras, nodos):
    """Devuelve un vector perpendicular promedio para posicionar diagramas sobre la estructura."""
    acumulado = np.zeros(3, dtype=float)
    cuenta = 0
    longitudes = []

    for barra in barras:
        p1 = np.asarray(barra.nodo_i_obj.get_coord(), dtype=float)
        p2 = np.asarray(barra.nodo_f_obj.get_coord(), dtype=float)
        direccion = p2 - p1
        norma = np.linalg.norm(direccion)
        if norma < 1e-6:
            continue
        direccion = direccion / norma
        longitudes.append(norma)

        up = np.array([0.0, 0.0, 1.0])
        perpendicular = np.cross(direccion, up)
        norma_perp = np.linalg.norm(perpendicular)
        if norma_perp < 1e-6:
            perpendicular = np.cross(direccion, np.array([0.0, 1.0, 0.0]))
            norma_perp = np.linalg.norm(perpendicular)
        if norma_perp < 1e-6:
            continue
        perpendicular = perpendicular / norma_perp
        acumulado += perpendicular
        cuenta += 1

    if cuenta == 0 or not longitudes:
        return np.zeros(3)

    vector_promedio = acumulado / cuenta
    longitud_ref = max(longitudes)
    factor_altura = 0.2 * longitud_ref
    return vector_promedio * factor_altura

def graficar_diagramas_3d(nodos, barras, factor_cortante=200.0, factor_momento=5.0, mostrar=True):
    """Grafica la estructura y los diagramas de cortante/momento en el espacio 3D."""
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')

    barras_artistas = trazar_barras(ax, barras, nodos, color='tab:blue', linewidth=2.5, alpha=0.7, etiqueta='Barra')
    nodos_artistas = trazar_nodos(ax, nodos)

    diagramas_cortante = []
    diagramas_momento = []

    for barra in barras:
        p1_base = np.asarray(barra.nodo_i_obj.get_coord(), dtype=float)
        p2_base = np.asarray(barra.nodo_f_obj.get_coord(), dtype=float)
        direccion = p2_base - p1_base
        longitud = np.linalg.norm(direccion)
        if longitud < 1e-6:
            continue
        direccion_unitaria = direccion / longitud

        up = np.array([0.0, 0.0, 1.0])
        perpendicular = np.cross(direccion_unitaria, up)
        norma_perp = np.linalg.norm(perpendicular)
        if norma_perp < 1e-6:
            perpendicular = np.cross(direccion_unitaria, np.array([0.0, 1.0, 0.0]))
            norma_perp = np.linalg.norm(perpendicular)
        if norma_perp < 1e-6:
            perpendicular = np.array([0.0, 0.0, 1.0])
            norma_perp = 1.0
        perpendicular = perpendicular / norma_perp

        offset_barra = perpendicular * (0.1 * longitud)
        base_shift = p1_base + offset_barra
        base_shift_end = p2_base + offset_barra

        direccion_cortante = perpendicular
        direccion_momento = np.cross(direccion_unitaria, direccion_cortante)
        if np.linalg.norm(direccion_momento) < 1e-6:
            direccion_momento = np.array([0.0, 0.0, 1.0])
        direccion_momento = direccion_momento / np.linalg.norm(direccion_momento)

        cortante_i = barra.esfuerzos.get('cortante_y_i', 0.0)
        cortante_f = barra.esfuerzos.get('cortante_y_f', 0.0)
        if not (abs(cortante_i) < 1e-6 and abs(cortante_f) < 1e-6):
            artistas_c = dibujar_diagrama_cortante(ax, base_shift, base_shift_end, barra,
                                                   factor_escala=factor_cortante,
                                                   direccion=direccion_cortante)
            if artistas_c is not None:
                diagramas_cortante.extend(artistas_c)

        base_momento_start = p1_base + offset_barra
        base_momento_end = p2_base + offset_barra
        momento_i = barra.esfuerzos.get('momento_z_i', 0.0)
        momento_f = barra.esfuerzos.get('momento_z_f', 0.0)
        if not (abs(momento_i) < 1e-6 and abs(momento_f) < 1e-6):
            artistas_m = dibujar_diagrama_momento(ax, base_momento_start, base_momento_end, barra,
                                                  factor_escala=factor_momento,
                                                  direccion=direccion_momento)
            if artistas_m is not None:
                diagramas_momento.extend(artistas_m)

    ax.set_xlabel('X [mm]')
    ax.set_ylabel('Y [mm]')
    ax.set_zlabel('Z [mm]')
    ax.set_title('Estructura y diagramas de cortante/momento en 3D (1:estructura, 2:nodos, 3:cortante, 4:momento)')
    ax.grid(True, linestyle='--', alpha=0.2)

    todos = np.array([nodo.get_coord() for nodo in nodos.values()])
    margin = 200.0
    ax.set_xlim(todos[:, 0].min() - margin, todos[:, 0].max() + margin)
    ax.set_ylim(todos[:, 1].min() - margin, todos[:, 1].max() + margin)
    ax.set_zlim(todos[:, 2].min() - margin, todos[:, 2].max() + margin)

    ax.legend(loc='upper left')

    controles = {
        'fig': fig,
        'ax': ax,
        'barras': barras_artistas,
        'nodos': nodos_artistas,
        'cortante': diagramas_cortante,
        'momento': diagramas_momento,
    }

    if mostrar:
        configurar_controles_teclado(fig, controles)
        plt.tight_layout()
        plt.show()

    return fig, ax

def configurar_controles_teclado(fig, controles):
    """Configura atajos de teclado para alternar capas (1 a 4)."""
    capas = {
        '1': ('Estructura', controles['barras']),
        '2': ('Nodos', [elem for par in controles['nodos'] for elem in (par if isinstance(par, (tuple, list)) else [par])]),
        '3': ('Cortante', controles['cortante']),
        '4': ('Momento', controles['momento']),
    }

    # Estado inicial
    estado = {clave: True for clave in capas}

    def set_visible(items, visibilidad):
        for item in items:
            if item is None:
                continue
            if isinstance(item, (tuple, list)):
                set_visible(item, visibilidad)
            elif hasattr(item, 'set_visible'):
                item.set_visible(visibilidad)

    def on_key(event):
        if event.key not in capas:
            return
        nombre, items = capas[event.key]
        estado[event.key] = not estado[event.key]
        set_visible(items, estado[event.key])
        fig.canvas.draw_idle()
        print(f"[{event.key}] {nombre}: {'visible' if estado[event.key] else 'oculto'}")

    fig.canvas.mpl_connect('key_press_event', on_key)

def graficar_resultados_prueba1(nodos, barras, factor_cortante=1.0, factor_momento=0.02):
    """Genera una vista 2D con la estructura y los diagramas de cortante y momento."""
    barras_ordenadas = sorted(barras, key=lambda b: b.id)

    posiciones = {}
    secciones = []
    longitud_total = 0.0

    for barra in barras_ordenadas:
        if barra.nodo_i not in posiciones:
            posiciones[barra.nodo_i] = longitud_total
        inicio = posiciones[barra.nodo_i]

        p1 = np.array(barra.nodo_i_obj.get_coord())
        p2 = np.array(barra.nodo_f_obj.get_coord())
        longitud_barra = np.linalg.norm(p2 - p1)

        fin = inicio + longitud_barra
        posiciones[barra.nodo_f] = fin
        secciones.append((inicio, fin, barra))
        longitud_total = fin

    fig, (ax_struct, ax_cortante, ax_momento) = plt.subplots(
        3, 1, figsize=(10, 12), constrained_layout=True
    )

    # --- Vista de la estructura (proyección XY) ---
    for barra in barras_ordenadas:
        xi, yi, _ = barra.nodo_i_obj.get_coord()
        xf, yf, _ = barra.nodo_f_obj.get_coord()
        ax_struct.plot([xi, xf], [yi, yf], color='steelblue', linewidth=3)

    for nodo in nodos.values():
        x, y, _ = nodo.get_coord()
        color = 'firebrick' if any(nodo.restricciones) else 'darkgreen'
        ax_struct.scatter(x, y, s=90, color=color, zorder=5)
        ax_struct.text(x, y + 40, f"N{nodo.id}", ha='center', va='bottom', fontsize=10)

    ax_struct.set_title("Estructura (vista en planta)")
    ax_struct.set_xlabel("X [mm]")
    ax_struct.set_ylabel("Y [mm]")
    ax_struct.set_aspect('equal', 'box')
    ax_struct.grid(True, linestyle='--', alpha=0.3)

    # --- Diagrama de Cortante ---
    ax_cortante.set_title("Diagrama de Cortante (DFC)")
    ax_cortante.axhline(0, color='black', linewidth=1)

    for inicio, fin, barra in secciones:
        si = barra.esfuerzos.get('cortante_y_i', 0.0)
        sf = barra.esfuerzos.get('cortante_y_f', 0.0)
        xs = [inicio, fin]
        ys = [si * factor_cortante, sf * factor_cortante]
        ax_cortante.plot(xs, ys, color='crimson', linewidth=3)
        ax_cortante.fill_between(xs, ys, 0, color='crimson', alpha=0.2)
        ax_cortante.text(inicio, ys[0], f"{si:.2f}", fontsize=9, va='bottom', ha='left', color='crimson')
        ax_cortante.text(fin, ys[1], f"{sf:.2f}", fontsize=9, va='bottom', ha='right', color='crimson')

    ax_cortante.set_ylabel(f"Cortante [t] (esc. x{factor_cortante})")
    ax_cortante.grid(True, linestyle='--', alpha=0.3)

    # --- Diagrama de Momento Flector ---
    ax_momento.set_title("Diagrama de Momento Flector (DMF)")
    ax_momento.axhline(0, color='black', linewidth=1)

    for inicio, fin, barra in secciones:
        mi = barra.esfuerzos.get('momento_z_i', 0.0)
        mf = barra.esfuerzos.get('momento_z_f', 0.0)
        xs = [inicio, fin]
        ys = [mi * factor_momento, mf * factor_momento]
        ax_momento.plot(xs, ys, color='royalblue', linewidth=3)
        ax_momento.fill_between(xs, ys, 0, color='royalblue', alpha=0.2)
        ax_momento.text(inicio, ys[0], f"{mi:.2f}", fontsize=9, va='bottom', ha='left', color='royalblue')
        ax_momento.text(fin, ys[1], f"{mf:.2f}", fontsize=9, va='bottom', ha='right', color='royalblue')

    ax_momento.set_ylabel(f"Momento [t·cm] (esc. x{factor_momento})")
    ax_momento.set_xlabel("Longitud acumulada [mm]")
    ax_momento.grid(True, linestyle='--', alpha=0.3)

    # Limites coherentes para diagramas
    ax_cortante.set_xlim(0, longitud_total)
    ax_momento.set_xlim(0, longitud_total)

    plt.show()

def imprimir_informacion_estructura(nodos, barras):
    """Imprime información detallada de la estructura"""
    print("="*60)
    print("INFORMACIÓN DE LA ESTRUCTURA")
    print("="*60)
    
    print("\n--- NODOS ---")
    for nodo in nodos.values():
        print(f"Nodo {nodo.id}: ({nodo.x}, {nodo.y}, {nodo.z})")
        print(f"  Restricciones: {nodo.restricciones}")
        print(f"  Valores prescritos: {nodo.valores_prescritos}")
        if hasattr(nodo, 'deformaciones'):
            print(f"  Deformaciones: {[f'{d:.4f}' for d in nodo.deformaciones]}")
        print()
    
    print("\n--- BARRAS ---")
    for barra in barras:
        print(f"Barra {barra.id}: Nodo {barra.nodo_i} → Nodo {barra.nodo_f}")
        print(f"  E = {barra.E}, G = {barra.G}, J = {barra.J}")
        print(f"  A = {barra.A}, I_y = {barra.I_y}, I_z = {barra.I_z}")
        
        # Mostrar esfuerzos si están disponibles
        if hasattr(barra, 'esfuerzos') and barra.esfuerzos:
            print(f"  Esfuerzos internos:")
            print(f"    Fuerza Axial: {barra.esfuerzos.get('axial_i', 0):.2f} t")
            print(f"    Cortante Y: {barra.esfuerzos.get('cortante_y_i', 0):.2f} t")
            print(f"    Cortante Z: {barra.esfuerzos.get('cortante_z_i', 0):.2f} t")
            print(f"    Momento X: {barra.esfuerzos.get('momento_x_i', 0):.2f} t·cm")
            print(f"    Momento Y: {barra.esfuerzos.get('momento_y_i', 0):.2f} t·cm")
            print(f"    Momento Z: {barra.esfuerzos.get('momento_z_i', 0):.2f} t·cm")
        print()

def imprimir_deformaciones(nodos):
    """Imprime un resumen de las deformaciones"""
    print("="*60)
    print("RESUMEN DE DEFORMACIONES")
    print("="*60)
    
    gdl_nombres = ['UX', 'UY', 'UZ', 'RX', 'RY', 'RZ']
    
    for nodo in nodos.values():
        if hasattr(nodo, 'deformaciones'):
            print(f"\nNodo {nodo.id}:")
            for i, (nombre, def_val) in enumerate(zip(gdl_nombres, nodo.deformaciones)):
                if abs(def_val) > 1e-6:  # Solo mostrar deformaciones significativas
                    print(f"  {nombre}: {def_val:.6f}")

if __name__ == "__main__":
    print("="*60)
    print("ANÁLISIS ESTRUCTURAL CON DEFORMACIONES REALES")
    print("="*60)
    
    # Crear estructura con cargas y calcular deformaciones reales
    print("\n1. Creando estructura con cargas...")
    nodos, barras, estructura = crear_estructura_con_cargas()
    
    # Imprimir información
    print("\n2. Información de la estructura:")
    imprimir_informacion_estructura(nodos, barras)
    imprimir_deformaciones(nodos)
    
    # Solo visualización 3D con controles interactivos por teclado
    print("\n3. Visualización 3D interactiva (usa teclas 1-4 para alternar capas)...")
    graficar_diagramas_3d(nodos, barras, factor_cortante=200.0, factor_momento=5.0)
    
    print("\n4. Visualización completada!")
    print("   - Estructura y diagramas de cortante/momento en 3D")
    print("   - Controles con teclado: 1=estructura, 2=nodos, 3=cortante, 4=momento")
    print("\n   Cierra la ventana para terminar.")
    
    try:
        input("\nPresiona Enter para cerrar el programa...")
    except KeyboardInterrupt:
        print("\nPrograma terminado por el usuario.")