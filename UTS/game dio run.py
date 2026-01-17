import tkinter as tk
import math
import random

class DinoRunManual:
    def __init__(self, root):
        self.root = root
        self.root.title("Tugas Grafika: Dino Run Manual")
        
        self.width = 800
        self.height = 400
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white")
        self.canvas.pack()
        
        # Buffer gambar untuk manipulasi pixel manual
        self.img = tk.PhotoImage(width=self.width, height=self.height)
        self.canvas.create_image((self.width//2, self.height//2), image=self.img)

        # Variabel Game
        self.dino_y = 300
        self.dino_v_y = 0
        self.is_jumping = False
        self.cactus_x = 800
        self.score = 0
        self.game_over = False
        self.scale_val = 1.0  # Materi Skala
        self.scale_dir = 0.01

        # Bind Input
        self.root.bind("<space>", lambda e: self.jump())
        
        self.run_game()

    # --- 1. ALGORITMA GARIS BRESENHAM ---
    def draw_line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0); dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            if 0 <= x0 < self.width and 0 <= y0 < self.height:
                self.img.put(color, (int(x0), int(y0)))
            if x0 == x1 and y0 == y1: break
            e2 = 2 * err
            if e2 > -dy: err -= dy; x0 += sx
            if e2 < dx: err += dx; y0 += sy

    # --- 2. ALGORITMA LINGKARAN MIDPOINT ---
    def draw_circle(self, xc, yc, r, color):
        x = 0; y = r; d = 1 - r
        while x <= y:
            for dx, dy in [(x,y), (y,x), (-x,y), (-y,x), (-x,-y), (-y,-x), (x,-y), (y,-x)]:
                px, py = xc + dx, yc + dy
                if 0 <= px < self.width and 0 <= py < self.height:
                    self.img.put(color, (int(px), int(py)))
            if d < 0: d += 2 * x + 3
            else: d += 2 * (x - y) + 5; y -= 1
            x += 1

    # --- 3 & 4. POLIGON & TRANSFORMASI (Translasi & Skala) ---
    def draw_dino(self, ox, oy):
        # Poligon dasar Dino (koordinat lokal)
        points = [(-20, -20), (20, -20), (20, 20), (-20, 20)]
        transformed = []
        
        # Animasi Skala sederhana (Materi 4)
        self.scale_val += self.scale_dir
        if self.scale_val > 1.1 or self.scale_val < 0.9:
            self.scale_dir *= -1

        for x, y in points:
            # Skala
            sx = x * self.scale_val
            sy = y * self.scale_val
            # Translasi (Materi 4)
            transformed.append((sx + ox, sy + oy))

        # Gambar Poligon (Materi 3)
        for i in range(len(transformed)):
            p1, p2 = transformed[i], transformed[(i+1)%len(transformed)]
            self.draw_line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), "green")
        
        # Mata Dino (Materi 2: Lingkaran)
        self.draw_circle(int(ox + 10), int(oy - 10), 3, "black")

    def draw_cactus(self, x):
        # Kaktus digambar dengan poligon sederhana
        h = 40
        w = 15
        p = [(x, 320), (x+w, 320), (x+w, 320-h), (x, 320-h)]
        for i in range(len(p)):
            p1, p2 = p[i], p[(i+1)%4]
            self.draw_line(int(p1[0]), int(p1[1]), int(p2[0]), int(p2[1]), "red")

    def jump(self):
        if not self.is_jumping:
            self.v_y = -15
            self.is_jumping = True

    def run_game(self):
        if self.game_over:
            return

        # Clear Buffer (Putih)
        self.img.put("#ffffff", to=(0, 0, self.width, self.height))

        # Update Posisi Dino (Gravitas)
        if self.is_jumping:
            self.dino_y += self.v_y
            self.v_y += 1 # Gravitas
            if self.dino_y >= 300:
                self.dino_y = 300
                self.is_jumping = False

        # Update Kaktus
        self.cactus_x -= 10
        if self.cactus_x < -20:
            self.cactus_x = 800
            self.score += 1

        # Gambar Lantai (Bresenham)
        self.draw_line(0, 320, 800, 320, "black")
        
        # Gambar Matahari (Midpoint Circle)
        self.draw_circle(700, 50, 30, "orange")

        # Gambar Objek Utama
        self.draw_dino(100, self.dino_y)
        self.draw_cactus(self.cactus_x)

        # Cek Tabrakan (Sederhana)
        if abs(100 - self.cactus_x) < 30 and self.dino_y > 270:
            print(f"GAME OVER! Skor Anda: {self.score}")
            self.game_over = True

        self.root.after(30, self.run_game)

root = tk.Tk()
game = DinoRunManual(root)
root.mainloop()