import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D

# 1. Definisi Objek Kubus (Titik-titik sudut)
def get_cube():
    return np.array([
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
    ])

# Koneksi antar titik untuk membentuk rusuk kubus
edges = [
    [0, 1], [1, 2], [2, 3], [3, 0],
    [4, 5], [5, 6], [6, 7], [7, 4],
    [0, 4], [1, 5], [2, 6], [3, 7]
]

# 2. Fungsi Matriks Transformasi
def translate(points, dx, dy, dz):
    matrix = np.eye(4)
    matrix[:3, 3] = [dx, dy, dz]
    return transform(points, matrix)

def scale(points, sx, sy, sz):
    matrix = np.diag([sx, sy, sz, 1])
    return transform(points, matrix)

def rotate_z(points, angle):
    rad = np.radians(angle)
    matrix = np.array([
        [np.cos(rad), -np.sin(rad), 0, 0],
        [np.sin(rad), np.cos(rad), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    return transform(points, matrix)

def reflect_xy(points):
    matrix = np.diag([1, 1, -1, 1]) # Membalik sumbu Z
    return transform(points, matrix)

def transform(points, matrix):
    # Menambah kolom 1 untuk koordinat homogen
    points_homo = np.hstack([points, np.ones((points.shape[0], 1))])
    transformed = points_homo @ matrix.T
    return transformed[:, :3]

# 3. Setup Plot
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')
cube = get_cube()

def update(frame):
    ax.clear()
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5); ax.set_zlim(-5, 5)
    ax.set_title("Animasi Grafkom: Fiko")
    
    data = get_cube()
    label = ""

    # Logika Sekuensial Animasi
    if frame < 30: # Translasi
        label = "Translasi (Bergeser)"
        data = translate(data, frame/10, frame/15, 0)
    elif frame < 60: # Skala
        label = "Skala (Membesar)"
        s = 1 + (frame-30)/30
        data = scale(data, s, s, s)
    elif frame < 90: # Rotasi
        label = "Rotasi Sumbu Z"
        data = rotate_z(data, (frame-60)*4)
    else: # Refleksi
        label = "Refleksi terhadap Bidang XY"
        data = reflect_xy(data)
    
    ax.text2D(0.05, 0.95, label, transform=ax.transAxes, color='red', fontsize=12)
    
    # Gambar Rusuk Kubus
    for edge in edges:
        ax.plot3D(*zip(data[edge[0]], data[edge[1]]), color="blue")

ani = FuncAnimation(fig, update, frames=120, interval=50)
plt.show()