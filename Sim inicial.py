import simpy
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
import matplotlib.colors as mcolors

# Configurar estilo de matplotlib para mejor apariencia
plt.style.use('seaborn-v0_8')
plt.rcParams['figure.facecolor'] = '#f8f9fa'
plt.rcParams['axes.facecolor'] = '#ffffff'

# Parámetros simplificados
NUM_CICLISTAS = 20
DISTANCIA_A = 50
DISTANCIA_B = 30
DISTANCIA_C = 40

# Solo 3 rutas posibles
RUTAS_POSIBLES = ['A->B', 'A->C', 'B->A', 'C->A']
VELOCIDADES = [random.uniform(10, 15) for _ in range(NUM_CICLISTAS)]

# Datos de ciclistas
coordenadas = [(0, 0)] * NUM_CICLISTAS
rutas = ['A->B'] * NUM_CICLISTAS
colores = ['blue'] * NUM_CICLISTAS
trayectorias = [[] for _ in range(NUM_CICLISTAS)]

# Paleta de colores mejorada y moderna
color_map = {
    'A->B': '#2E86AB',  # Azul moderno
    'A->C': '#A23B72',  # Magenta elegante
    'B->A': '#F18F01',  # Naranja vibrante
    'C->A': '#C73E1D'   # Rojo intenso
}

for i in range(NUM_CICLISTAS):
    ruta = random.choice(RUTAS_POSIBLES)
    rutas[i] = ruta
    colores[i] = color_map.get(ruta, '#6C757D')

# Simulación con SimPy simplificada
def ciclista(env, id, velocidad):
    ruta = rutas[id]
    origen, destino = ruta.split('->')

    # Posición inicial
    if origen == 'A':
        x, y = 0, 0
    elif origen == 'B':
        x = DISTANCIA_A + DISTANCIA_B
        y = DISTANCIA_B * 0.5  # Desviación hacia arriba
    elif origen == 'C':
        x = DISTANCIA_A + DISTANCIA_C
        y = -DISTANCIA_C * 0.5  # Desviación hacia abajo

    coordenadas[id] = (x, y)
    trayectorias[id].append((x, y))

    # Movimiento hacia bifurcación (punto X)
    if origen in ['B', 'C']:
        distancia = 0
        tramo = DISTANCIA_B if origen == 'B' else DISTANCIA_C
        angulo = 0.5 if origen == 'B' else -0.5  # Pendiente para crear la Y
        
        while distancia < tramo:
            yield env.timeout(0.1)
            distancia += velocidad * 0.1
            x = DISTANCIA_A + (tramo - distancia)
            y = (tramo - distancia) * angulo
            coordenadas[id] = (x, y)
            trayectorias[id].append((x, y))

    # Movimiento desde A hacia bifurcación X
    if origen == 'A':
        distancia = 0
        while distancia < DISTANCIA_A:
            yield env.timeout(0.1)
            distancia += velocidad * 0.1
            x = distancia
            y = 0
            coordenadas[id] = (x, y)
            trayectorias[id].append((x, y))

    # Movimiento desde bifurcación X hacia destino
    if destino == 'B':
        distancia = 0
        while distancia < DISTANCIA_B:
            yield env.timeout(0.1)
            distancia += velocidad * 0.1
            x = DISTANCIA_A + distancia
            y = distancia * 0.5  # Desviación hacia arriba
            coordenadas[id] = (x, y)
            trayectorias[id].append((x, y))
    elif destino == 'C':
        distancia = 0
        while distancia < DISTANCIA_C:
            yield env.timeout(0.1)
            distancia += velocidad * 0.1
            x = DISTANCIA_A + distancia
            y = -distancia * 0.5  # Desviación hacia abajo
            coordenadas[id] = (x, y)
            trayectorias[id].append((x, y))
    elif destino == 'A':
        distancia = 0
        while distancia < DISTANCIA_A:
            yield env.timeout(0.1)
            distancia += velocidad * 0.1
            x = DISTANCIA_A - distancia
            y = 0
            coordenadas[id] = (x, y)
            trayectorias[id].append((x, y))

# Crear entorno
env = simpy.Environment()
for i in range(NUM_CICLISTAS):
    env.process(ciclista(env, i, VELOCIDADES[i]))

# Visualización mejorada con mejor paleta de colores
fig, ax = plt.subplots(figsize=(12, 8))
scat = ax.scatter([], [], s=80, alpha=0.8, edgecolors='white', linewidth=2)

# Fondo del plano con gradiente sutil
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('#ffffff')

# Dibujar carreteras en forma de Y con mejor diseño
# Tramo principal A->X
ax.plot([0, DISTANCIA_A], [0, 0], color='#495057', linewidth=6, alpha=0.9, 
        solid_capstyle='round', label='Tramo Principal A→X')

# Tramo X->B con sombra y mejor color
ax.plot([DISTANCIA_A, DISTANCIA_A + DISTANCIA_B], [0, DISTANCIA_B * 0.5], 
        color='#2E86AB', linewidth=6, alpha=0.9, solid_capstyle='round', 
        label='Tramo X→B')

# Tramo X->C con sombra y mejor color
ax.plot([DISTANCIA_A, DISTANCIA_A + DISTANCIA_C], [0, -DISTANCIA_C * 0.5], 
        color='#A23B72', linewidth=6, alpha=0.9, solid_capstyle='round', 
        label='Tramo X→C')

# Marcadores de puntos mejorados con círculos y etiquetas
# Punto A
circle_a = Circle((0, 0), 1.5, color='#212529', alpha=0.9, zorder=5)
ax.add_patch(circle_a)
ax.text(0, -2.5, 'PUNTO A', ha='center', va='top', fontsize=10, fontweight='bold', 
        color='#212529', bbox=dict(boxstyle="round,pad=0.2", facecolor='#ffffff', alpha=0.8))

# Punto X (Bifurcación)
circle_x = Circle((DISTANCIA_A, 0), 2, color='#6f42c1', alpha=0.9, zorder=5)
ax.add_patch(circle_x)
ax.text(DISTANCIA_A, -2.5, 'BIFURCACIÓN X', ha='center', va='top', fontsize=10, fontweight='bold', 
        color='#6f42c1', bbox=dict(boxstyle="round,pad=0.2", facecolor='#ffffff', alpha=0.8))

# Punto B
circle_b = Circle((DISTANCIA_A + DISTANCIA_B, DISTANCIA_B * 0.5), 1.5, color='#2E86AB', alpha=0.9, zorder=5)
ax.add_patch(circle_b)
ax.text(DISTANCIA_A + DISTANCIA_B, DISTANCIA_B * 0.5 - 2.5, 'PUNTO B', ha='center', va='top', fontsize=10, fontweight='bold', 
        color='#2E86AB', bbox=dict(boxstyle="round,pad=0.2", facecolor='#ffffff', alpha=0.8))

# Punto C
circle_c = Circle((DISTANCIA_A + DISTANCIA_C, -DISTANCIA_C * 0.5), 1.5, color='#A23B72', alpha=0.9, zorder=5)
ax.add_patch(circle_c)
ax.text(DISTANCIA_A + DISTANCIA_C, -DISTANCIA_C * 0.5 - 2.5, 'PUNTO C', ha='center', va='top', fontsize=10, fontweight='bold', 
        color='#A23B72', bbox=dict(boxstyle="round,pad=0.2", facecolor='#ffffff', alpha=0.8))

# Configuración del plano y ejes optimizada para pestaña
ax.set_xlim(-10, DISTANCIA_A + max(DISTANCIA_B, DISTANCIA_C) + 10)
ax.set_ylim(-max(DISTANCIA_C, DISTANCIA_B) - 8, max(DISTANCIA_C, DISTANCIA_B) + 8)

# Título y etiquetas optimizadas para pestaña
ax.set_title("🚴 CICLORRUTA EN FORMA DE Y 🚴", 
             fontsize=16, fontweight='bold', color='#212529', pad=15)
ax.set_xlabel("Distancia (metros)", fontsize=12, fontweight='bold', color='#495057')
ax.set_ylabel("Desviación (metros)", fontsize=12, fontweight='bold', color='#495057')

# Leyenda optimizada para pestaña
legend = ax.legend(loc='upper right', fontsize=10, frameon=True, 
                   fancybox=True, shadow=True, framealpha=0.9)
legend.get_frame().set_facecolor('#ffffff')
legend.get_frame().set_edgecolor('#dee2e6')

# Cuadrícula mejorada
ax.grid(True, alpha=0.3, color='#adb5bd', linestyle='-', linewidth=0.5)

# Ejes más elegantes
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color('#6c757d')
ax.spines['bottom'].set_color('#6c757d')
ax.spines['left'].set_linewidth(1.5)
ax.spines['bottom'].set_linewidth(1.5)

# Marcadores de escala en los ejes optimizados
ax.tick_params(axis='both', which='major', labelsize=9, colors='#495057')
ax.tick_params(axis='both', which='minor', labelsize=7, colors='#6c757d')

# Animación
def update(frame):
    env.step()
    x, y = zip(*coordenadas)
    scat.set_offsets(list(zip(x, y)))
    scat.set_color(colores)
    return scat,

ani = FuncAnimation(fig, update, frames=200, interval=50, blit=True)

# Layout optimizado para pestaña
plt.tight_layout(pad=1.5)
plt.show()
