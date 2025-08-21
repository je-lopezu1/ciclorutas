import simpy
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Parámetros
NUM_CICLISTAS = 40
DISTANCIA_A = 50
DISTANCIA_B = 30
DISTANCIA_C = 40
ORIGENES = ['A', 'X', 'B', 'C']
DESTINOS = ['B', 'C', 'A', 'X']
VELOCIDADES = [random.uniform(10, 15) for _ in range(NUM_CICLISTAS)]

# Datos de ciclistas
coordenadas = [(0, 0)] * NUM_CICLISTAS
rutas = ['A->B'] * NUM_CICLISTAS
colores = ['blue'] * NUM_CICLISTAS
trayectorias = [[] for _ in range(NUM_CICLISTAS)]

# Asignar rutas y colores
color_map = {
    'A->B': 'blue', 'A->C': 'red', 'X->B': 'green', 'X->C': 'orange',
    'B->A': 'purple', 'C->A': 'brown', 'B->X': 'cyan', 'C->X': 'magenta'
}
for i in range(NUM_CICLISTAS):
    origen = random.choice(ORIGENES)
    destino = random.choice([d for d in DESTINOS if d != origen])
    ruta = f"{origen}->{destino}"
    rutas[i] = ruta
    colores[i] = color_map.get(ruta, 'gray')

# Simulación con SimPy
def ciclista(env, id, velocidad):
    ruta = rutas[id]
    origen, destino = ruta.split('->')

    # Posición inicial
    if origen == 'A':
        x, y = 0, -1
    elif origen == 'X':
        x, y = -20, 1
    elif origen == 'B':
        x = DISTANCIA_A + DISTANCIA_B * np.cos(np.pi / 4)
        y = DISTANCIA_B * np.sin(np.pi / 4)
    elif origen == 'C':
        x = DISTANCIA_A + DISTANCIA_C * np.cos(-np.pi / 4)
        y = DISTANCIA_C * np.sin(-np.pi / 4)

    coordenadas[id] = (x, y)
    trayectorias[id].append((x, y))

    # Movimiento hacia bifurcación
    if origen == 'A':
        distancia = 0
        while distancia < DISTANCIA_A:
            yield env.timeout(0.1)
            distancia += velocidad * 0.1
            x = distancia
            y = -1
            coordenadas[id] = (x, y)
            trayectorias[id].append((x, y))
    elif origen == 'X':
        distancia = 0
        total = np.sqrt((DISTANCIA_A + 20)**2 + 2**2)
        while distancia < total:
            yield env.timeout(0.1)
            distancia += velocidad * 0.1
            frac = distancia / total
            x = -20 + frac * (DISTANCIA_A + 20)
            y = 1 - frac * 1
            coordenadas[id] = (x, y)
            trayectorias[id].append((x, y))
    elif origen in ['B', 'C']:
        distancia = 0
        tramo = DISTANCIA_B if origen == 'B' else DISTANCIA_C
        angulo = np.pi / 4 if origen == 'B' else -np.pi / 4
        while distancia < tramo:
            yield env.timeout(0.1)
            distancia += velocidad * 0.1
            x = DISTANCIA_A + (tramo - distancia) * np.cos(angulo)
            y = (tramo - distancia) * np.sin(angulo)
            coordenadas[id] = (x, y)
            trayectorias[id].append((x, y))

    # Movimiento hacia destino
    if destino == 'B':
        distancia = 0
        while distancia < DISTANCIA_B:
            yield env.timeout(0.1)
            distancia += velocidad * 0.1
            x = DISTANCIA_A + distancia * np.cos(np.pi / 4)
            y = distancia * np.sin(np.pi / 4)
            coordenadas[id] = (x, y)
            trayectorias[id].append((x, y))
    elif destino == 'C':
        distancia = 0
        while distancia < DISTANCIA_C:
            yield env.timeout(0.1)
            distancia += velocidad * 0.1
            x = DISTANCIA_A + distancia * np.cos(-np.pi / 4)
            y = distancia * np.sin(-np.pi / 4)
            coordenadas[id] = (x, y)
            trayectorias[id].append((x, y))
    elif destino == 'A':
        distancia = 0
        while distancia < DISTANCIA_A:
            yield env.timeout(0.1)
            distancia += velocidad * 0.1
            x = DISTANCIA_A - distancia
            y = 1
            coordenadas[id] = (x, y)
            trayectorias[id].append((x, y))
    elif destino == 'X':
        distancia = 0
        total = np.sqrt((DISTANCIA_A + 20)**2 + 2**2)
        while distancia < total:
            yield env.timeout(0.1)
            distancia += velocidad * 0.1
            frac = distancia / total
            x = DISTANCIA_A - frac * (DISTANCIA_A + 20)
            y = 0 + frac * 1
            coordenadas[id] = (x, y)
            trayectorias[id].append((x, y))

# Crear entorno
env = simpy.Environment()
for i in range(NUM_CICLISTAS):
    env.process(ciclista(env, i, VELOCIDADES[i]))

# Visualización
fig, ax = plt.subplots()
scat = ax.scatter([], [], s=60)

# Dibujar carreteras
ax.plot([0, DISTANCIA_A], [-1, -1], 'gray', linewidth=3)
ax.plot([0, DISTANCIA_A], [1, 1], 'gray', linewidth=3)
ax.plot([DISTANCIA_A, DISTANCIA_A + DISTANCIA_B * np.cos(np.pi / 4)],
        [0, DISTANCIA_B * np.sin(np.pi / 4)], 'gray', linewidth=3)
ax.plot([DISTANCIA_A, DISTANCIA_A + DISTANCIA_C * np.cos(-np.pi / 4)],
        [0, DISTANCIA_C * np.sin(-np.pi / 4)], 'gray', linewidth=3)
ax.plot([-20, 0], [1, 0], 'gray', linewidth=3)

ax.set_xlim(-30, DISTANCIA_A + max(DISTANCIA_B, DISTANCIA_C) + 10)
ax.set_ylim(-max(DISTANCIA_C, DISTANCIA_B) - 10, 20)
ax.set_title("Ciclorruta con doble sentido y múltiples rutas")
ax.set_xlabel("Distancia (m)")
ax.set_ylabel("Desviación (m)")

# Animación
def update(frame):
    env.step()
    x, y = zip(*coordenadas)
    scat.set_offsets(list(zip(x, y)))
    scat.set_color(colores)
    return scat,

ani = FuncAnimation(fig, update, frames=150, interval=50, blit=True)
plt.show()
