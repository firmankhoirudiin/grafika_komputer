import tkinter as tk
import math

class PacmanFinalProject:
    
    
    def __init__(self, root):
        self.root = root
        self.root.title("Proyek Grafika: Pac-Man Lengkap (Manual)")
        
        self.width = 600
        self.height = 500
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="black")
        self.canvas.pack()
        
        self.img = tk.PhotoImage(width=self.width, height=self.height)
        self.canvas.create_image((self.width//2, self.height//2), image=self.img)

        # Variabel Game
        self.px, self.py = 40, 45 
        self.angle = 0
        self.score = 0
        self.game_over = False
        self.anim_frame = 0 # Digunakan untuk Skala & Animasi Mulut

        # Dinding Labirin (Materi 1: Bresenham)
        self.walls = [
            (10, 10, 590, 10), (10, 10, 10, 480), (590, 10, 590, 480), (10, 480, 590, 480),
            (100, 80, 250, 80), (100, 80, 100, 200), (350, 80, 500, 80), (500, 80, 500, 200),
            (100, 300, 100, 400), (100, 400, 250, 400), (350, 400, 500, 400), (500, 300, 500, 400),
            (250, 200, 350, 200), (250, 280, 350, 280)
        ]

        # Makanan (Materi 2: Midpoint Circle)
        self.dots = [{"x": x, "y": y, "active": True} for x in range(60, 550, 60) for y in range(60, 450, 60)]

        # Hantu (Materi 3 & 4: Poligon & Refleksi)
        self.ghosts = [
            {"x": 540, "y": 45, "dir": "down", "color": "red"},
            {"x": 40, "y": 440, "dir": "up", "color": "pink"}
        ]

        self.root.bind("<Left>", lambda e: self.set_dir(math.pi))
        self.root.bind("<Right>", lambda e: self.set_dir(0))
        self.root.bind("<Up>", lambda e: self.set_dir(-math.pi/2))
        self.root.bind("<Down>", lambda e: self.set_dir(math.pi/2))
        
        self.update_game()

    # --- 1. ALGORITMA GARIS BRESENHAM ---
    def draw_line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1-x0), abs(y1-y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx - dy
        while True:
            if 0 <= x0 < self.width and 0 <= y0 < self.height:
                self.img.put(color, (int(x0), int(y0)))
            if x0 == x1 and y0 == y1: break
            e2 = 2*err
            if e2 > -dy: err -= dy; x0 += sx
            if e2 < dx: err += dx; y0 += sy

    # --- 2 & 4. LINGKARAN MIDPOINT + SKALA + ROTASI ---
    def draw_pacman(self, xc, yc, r, color):
        # TRANSFORMASI SKALA: Membuat badan berdenyut
        scale_factor = 1 + (math.sin(self.anim_frame * 0.5) * 0.1)
        r_scaled = int(r * scale_factor)
        
        # ANIMASI MULUT: Besarnya celah
        mouth_gap = abs(math.sin(self.anim_frame)) * 0.8
        
        x, y, d = 0, r_scaled, 1 - r_scaled
        while x <= y:
            pts = [(x,y), (y,x), (-x,y), (-y,x), (-x,-y), (-y,-x), (x,-y), (y,-x)]
            for px, py in pts:
                # TRANSFORMASI ROTASI: Menentukan arah mulut
                pixel_angle = math.atan2(py, px)
                diff = (pixel_angle - self.angle + math.pi) % (2*math.pi) - math.pi
                if abs(diff) > mouth_gap:
                    self.img.put(color, (int(xc+px), int(yc+py)))
            if d < 0: d += 2*x + 3
            else: d += 2*(x-y) + 5; y -= 1
            x += 1

    def draw_dot(self, xc, yc, r, color):
        x, y, d = 0, r, 1-r
        while x <= y:
            pts = [(x,y), (y,x), (-x,y), (-y,x), (-x,-y), (-y,-x), (x,-y), (y,-x)]
            for px, py in pts:
                self.img.put(color, (int(xc+px), int(yc+py)))
            if d < 0: d += 2*x + 3
            else: d += 2*(x-y) + 5; y -= 1
            x += 1

    # --- 3 & 4. POLIGON + REFLEKSI ---
    def draw_ghost(self, ox, oy, color):
        # Sisi Kanan Hantu
        right_side = [(0, -15), (12, -5), (12, 12), (4, 8), (0, 12)]
        # TRANSFORMASI REFLEKSI: Mencerminkan sisi kanan ke kiri
        left_side = [(-px, py) for px, py in reversed(right_side)]
        full_poly = right_side + left_side
        
        for i in range(len(full_poly)):
            p1, p2 = full_poly[i], full_poly[(i+1)%len(full_poly)]
            # Translasi ke posisi hantu
            self.draw_line(int(p1[0]+ox), int(p1[1]+oy), int(p2[0]+ox), int(p2[1]+oy), color)

    def is_wall(self, x, y):
        radius = 15
        for w in self.walls:
            if min(w[0], w[2])-radius <= x <= max(w[0], w[2])+radius and \
               min(w[1], w[3])-radius <= y <= max(w[1], w[3])+radius:
                return True
        return False

    def set_dir(self, r): self.angle = r

    def update_game(self):
        if self.game_over: return
        self.img.put("#000000", to=(0, 0, self.width, self.height))
        self.anim_frame += 0.2

        # 1. Pergerakan & Translasi Pacman
        nx = self.px + math.cos(self.angle) * 5
        ny = self.py + math.sin(self.angle) * 5
        if not self.is_wall(nx, ny):
            self.px, self.py = nx, ny

        # 2. Gambar Labirin & Skor (Bresenham)
        for w in self.walls: self.draw_line(w[0], w[1], w[2], w[3], "blue")
        for i in range(self.score): 
            self.draw_line(10 + i*5, 490, 12 + i*5, 490, "yellow")

        # 3. Makanan & Deteksi
        for d in self.dots:
            if d["active"]:
                self.draw_dot(d["x"], d["y"], 2, "white")
                if math.dist((self.px, self.py), (d["x"], d["y"])) < 15:
                    d["active"] = False; self.score += 1

        # 4. Hantu Patroli
        for g in self.ghosts:
            if g["dir"] == "down": g["y"] += 3
            elif g["dir"] == "up": g["y"] -= 3
            if g["y"] > 440: g["dir"] = "up"
            if g["y"] < 45: g["dir"] = "down"
            self.draw_ghost(g["x"], g["y"], g["color"])
            
            if math.dist((self.px, self.py), (g["x"], g["y"])) < 25:
                self.game_over = True
                print("GAME OVER! Skor:", self.score)
                return

        # 5. Render Pacman
        self.draw_pacman(self.px, self.py, 18, "yellow")

        self.root.after(30, self.update_game)

root = tk.Tk()
game = PacmanFinalProject(root)
root.mainloop()