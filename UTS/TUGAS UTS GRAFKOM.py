import tkinter as tk
import math
import random

class PacmanFinalProject:
    def __init__(self, root):
        self.root = root
        self.root.title("Proyek Grafika")
        
        self.width = 600
        self.height = 550 
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white")
        self.canvas.pack()
        
        self.img = tk.PhotoImage(width=self.width, height=self.height)
        self.canvas.create_image((self.width//2, self.height//2), image=self.img)

        # Variabel Karakter 
        self.px, self.py = 40, 95 
        self.angle = 0
        self.score = 0
        self.game_over = False
        self.anim_frame = 0 

        # Dinding Labirin digeser ke bawah
        self.offset_y = 60
        self.walls = [
            (10, 10+self.offset_y, 590, 10+self.offset_y), 
            (10, 10+self.offset_y, 10, 480+self.offset_y), 
            (590, 10+self.offset_y, 590, 480+self.offset_y), 
            (10, 480+self.offset_y, 590, 480+self.offset_y),
            (100, 80+self.offset_y, 250, 80+self.offset_y), 
            (100, 80+self.offset_y, 100, 200+self.offset_y), 
            (350, 80+self.offset_y, 500, 80+self.offset_y), 
            (500, 80+self.offset_y, 500, 200+self.offset_y),
            (100, 300+self.offset_y, 100, 400+self.offset_y), 
            (100, 400+self.offset_y, 250, 400+self.offset_y), 
            (350, 400+self.offset_y, 500, 400+self.offset_y), 
            (500, 300+self.offset_y, 500, 400+self.offset_y),
            (250, 200+self.offset_y, 350, 200+self.offset_y), 
            (250, 280+self.offset_y, 350, 280+self.offset_y)
        ]
#maka
        self.dots = [{"x": x, "y": y+self.offset_y, "active": True} for x in range(60, 550, 60) for y in range(60, 450, 60)]
#hantu
        self.ghosts = [
            {"x": 540, "y": 45+self.offset_y, "vx": -3, "vy": 0, "color": "red"},
            {"x": 40, "y": 440+self.offset_y, "vx": 3, "vy": 0, "color": "pink"},
            {"x": 300, "y": 240+self.offset_y, "vx": 0, "vy": 3, "color": "cyan"}
        ]

        self.root.bind("<Left>", lambda e: self.set_dir(math.pi))
        self.root.bind("<Right>", lambda e: self.set_dir(0))
        self.root.bind("<Up>", lambda e: self.set_dir(-math.pi/2))
        self.root.bind("<Down>", lambda e: self.set_dir(math.pi/2))
        
        self.update_game()

    # ALGORITMA GARIS BRESENHAM
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

    # TEKS MANUAL
    def draw_text_manual(self, text, start_x, start_y, size=1.5, color="white"):
        chars = {
            'S': [(1,0,0,0), (0,0,0,1), (0,1,1,1), (1,1,1,2), (1,2,0,2)],
            'C': [(1,0,0,0), (0,0,0,2), (0,2,1,2)],
            'O': [(0,0,1,0), (1,0,1,2), (1,2,0,2), (0,2,0,0)],
            'R': [(0,2,0,0), (0,0,1,0), (1,0,1,1), (0,1,1,1), (0.5,1,1,2)],
            'E': [(1,0,0,0), (0,0,0,2), (0,2,1,2), (0,1,1,1)],
            'G': [(1,0,0,0), (0,0,0,2), (0,2,1,2), (1,2,1,1), (1,1,0.5,1)],
            'A': [(0,2,0,0), (0,0,1,0), (1,0,1,2), (0,1,1,1)],
            'M': [(0,2,0,0), (0,0,0.5,1), (0.5,1,1,0), (1,0,1,2)],
            'V': [(0,0,0.5,2), (0.5,2,1,0)],
            ':': [(0.5,0.4,0.5,0.6), (0.5,1.4,0.5,1.6)],
            '0': [(0,0,1,0), (1,0,1,2), (1,2,0,2), (0,2,0,0)],
            '1': [(1,0,1,2)], '2': [(0,0,1,0), (1,0,1,1), (1,1,0,1), (0,1,0,2), (0,2,1,2)],
            '3': [(0,0,1,0), (1,0,1,2), (0,1,1,1), (0,2,1,2)], '4': [(0,0,0,1), (1,0,1,2), (0,1,1,1)],
            '5': [(1,0,0,0), (0,0,0,1), (0,1,1,1), (1,1,1,2), (1,2,0,2)],
            '6': [(1,0,0,0), (0,0,0,2), (0,1,1,1), (1,1,1,2), (1,2,0,2)],
            '7': [(0,0,1,0), (1,0,1,2)], '8': [(0,0,1,0), (1,0,1,2), (1,2,0,2), (0,2,0,0), (0,1,1,1)],
            '9': [(0,1,1,1), (0,1,0,0), (0,0,1,0), (1,0,1,2), (0,2,1,2)]
        }
        scale = 8 * size
        curr_x = start_x
        for char in text.upper():
            if char in chars:
                for x0, y0, x1, y1 in chars[char]:
                    self.draw_line(int(curr_x + x0*scale), int(start_y + y0*scale),
                                   int(curr_x + x1*scale), int(start_y + y1*scale), color)
            curr_x += scale * 1.4

    # LINGKARAN MIDPOINT
    def draw_circle_manual(self, xc, yc, r, color, is_pacman=False):
        r_s = int(r * (1 + (math.sin(self.anim_frame * 0.5) * 0.1))) if is_pacman else r
        mouth = abs(math.sin(self.anim_frame)) * 0.8 if is_pacman else 0
        x, y, d = 0, r_s, 1 - r_s
        while x <= y:
            pts = [(x,y), (y,x), (-x,y), (-y,x), (-x,-y), (-y,-x), (x,-y), (y,-x)]
            for px, py in pts:
                ang = math.atan2(py, px)
                diff = (ang - self.angle + math.pi) % (2*math.pi) - math.pi
                if not is_pacman or abs(diff) > mouth:
                    self.img.put(color, (int(xc+px), int(yc+py)))
            if d < 0: d += 2*x + 3
            else: d += 2*(x-y) + 5; y -= 1
            x += 1

    # POLIGON + REFLEKSI
    def draw_ghost(self, ox, oy, color):
        r_side = [(0, -15), (12, -5), (12, 12), (4, 8), (0, 12)]
        full_p = r_side + [(-px, py) for px, py in reversed(r_side)]
        for i in range(len(full_p)):
            p1, p2 = full_p[i], full_p[(i+1)%len(full_p)]
            self.draw_line(int(p1[0]+ox), int(p1[1]+oy), int(p2[0]+ox), int(p2[1]+oy), color)

    def is_wall(self, x, y):
        radius = 12
        for w in self.walls:
            if min(w[0], w[2])-radius <= x <= max(w[0], w[2])+radius and \
               min(w[1], w[3])-radius <= y <= max(w[1], w[3])+radius:
                return True
        return False

    def set_dir(self, r): self.angle = r

    def update_game(self):
        if self.game_over:
            self.draw_text_manual("GAME OVER", 180, 220, size=3, color="red")
            self.draw_text_manual(f"SCORE: {self.score}", 220, 300, size=2, color="yellow")
            return
        #warna hitam    
        self.img.put("#000000", to=(0, 0, self.width, self.height))
        #mulut
        self.anim_frame += 0.2

        # 1. Papan Skor
        self.draw_text_manual("PAC-MAN fiko", 20, 20, size=1.2, color="white")
        self.draw_text_manual(f"SCORE: {self.score}", 440, 20, size=1.5, color="yellow")

        # 2. Labirin & Pacman
        for w in self.walls: self.draw_line(w[0], w[1], w[2], w[3], "blue")
        nx, ny = self.px + math.cos(self.angle)*5, self.py + math.sin(self.angle)*5
        if not self.is_wall(nx, ny): self.px, self.py = nx, ny
        self.draw_circle_manual(self.px, self.py, 18, "yellow", True)

        # 3. Makanan & Hantu
        for d in self.dots:
            if d["active"]:
                self.draw_circle_manual(d["x"], d["y"], 2, "white")
                if math.dist((self.px, self.py), (d["x"], d["y"])) < 15:
                    d["active"] = False; self.score += 1

        directions = [(3,0), (-3,0), (0,3), (0,-3)]
        for g in self.ghosts:
            if self.is_wall(g["x"] + g["vx"], g["y"] + g["vy"]) or random.random() < 0.02:
                g["vx"], g["vy"] = random.choice(directions)
            g["x"] += g["vx"]; g["y"] += g["vy"]
            self.draw_ghost(g["x"], g["y"], g["color"])
            if math.dist((self.px, self.py), (g["x"], g["y"])) < 25: self.game_over = True

        self.root.after(30, self.update_game)

root = tk.Tk()
game = PacmanFinalProject(root)
root.mainloop()