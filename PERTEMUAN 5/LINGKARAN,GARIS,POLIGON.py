# turtle_raster_shapes.py
# Menggambar garis (Bresenham), lingkaran (Midpoint Circle), dan poligon
# Menggunakan Python + turtle (tidak memakai library grafis lain)

import turtle
import math

# ---------------------------
# Konfigurasi tampilan Turtle
# ---------------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PIXEL_SIZE = 4      # ukuran dot yang dipakai untuk "pixel"
SCALE = 1           # skala koordinat (1 = 1 unit = 1 pixel)
OFFSET_X = 0        # offset untuk memindahkan origin
OFFSET_Y = 0

screen = turtle.Screen()
screen.setup(SCREEN_WIDTH, SCREEN_HEIGHT)
screen.title("Garis (Bresenham), Lingkaran (Midpoint) dan Poligon - Turtle")
screen.tracer(0, 0)  # non-animasi untuk menggambar cepat

pen = turtle.Turtle()
pen.hideturtle()
pen.penup()
pen.speed(0)

# ---------------------------
# Util: plot "pixel"
# ---------------------------
def set_pixel(x, y, color="black"):
    """
    Gambar satu 'pixel' pada koordinat (x, y) menggunakan turtle.dot.
    Koordinat dianggap dalam satuan integer grid; fungsi akan mentransform
    ke koordinat layar sesuai SCALE dan OFFSET.
    """
    sx = x * SCALE + OFFSET_X
    sy = y * SCALE + OFFSET_Y
    pen.goto(sx, sy)
    pen.dot(PIXEL_SIZE, color)

# ---------------------------
# Bresenham line algorithm
# ---------------------------
def draw_line_bresenham(x0, y0, x1, y1, color="black"):
    """
    Gambar garis dari (x0,y0) ke (x1,y1) menggunakan algoritma Bresenham.
    Koordinat yang dipakai diasumsikan integer (tapi bisa float, akan dibulatkan).
    """
    x0 = int(round(x0))
    y0 = int(round(y0))
    x1 = int(round(x1))
    y1 = int(round(y1))

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        set_pixel(x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = err * 2
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

# ---------------------------
# Midpoint Circle algorithm
# ---------------------------
def draw_circle_midpoint(cx, cy, radius, color="black"):
    """
    Gambar lingkaran dengan algoritma Midpoint Circle.
    cx, cy : pusat (integer)
    radius : jari-jari (integer >= 0)
    """
    x = 0
    y = int(round(radius))
    d = 1 - y

    def plot_circle_points(cx, cy, x, y, color):
        # plot 8 simetri titik
        set_pixel(cx + x, cy + y, color)
        set_pixel(cx - x, cy + y, color)
        set_pixel(cx + x, cy - y, color)
        set_pixel(cx - x, cy - y, color)
        set_pixel(cx + y, cy + x, color)
        set_pixel(cx - y, cy + x, color)
        set_pixel(cx + y, cy - x, color)
        set_pixel(cx - y, cy - x, color)

    plot_circle_points(cx, cy, x, y, color)
    while x < y:
        x += 1
        if d < 0:
            d = d + 2 * x + 1
        else:
            y -= 1
            d = d + 2 * (x - y) + 1
        plot_circle_points(cx, cy, x, y, color)

# ---------------------------
# Poligon (menggunakan Bresenham)
# ---------------------------
def draw_polygon(points, color="black", close=True):
    """
    Gambar poligon dengan daftar titik 'points' = [(x0,y0), (x1,y1), ...].
    Jika close=True, sambungkan titik terakhir ke titik pertama.
    """
    n = len(points)
    if n < 2:
        return
    for i in range(n - 1):
        x0, y0 = points[i]
        x1, y1 = points[i+1]
        draw_line_bresenham(x0, y0, x1, y1, color)
    if close:
        x0, y0 = points[-1]
        x1, y1 = points[0]
        draw_line_bresenham(x0, y0, x1, y1, color)

# ---------------------------
# Contoh penggunaan
# ---------------------------
def example_draw():
    # bersihkan area
    pen.clear()

    # contoh 1: beberapa garis dengan Bresenham
    draw_line_bresenham(-150, 200, 150, 200, color="blue")   # horizontal
    draw_line_bresenham(-150, 180, 150, 100, color="green")  # diagonal
    draw_line_bresenham(0, 250, 0, 50, color="red")          # vertikal

    # contoh 2: lingkaran di tengah
    draw_circle_midpoint(0, 0, 80, color="black")

    # contoh 3: poligon (segilima)
    pentagon = [(200, -50), (260, 0), (230, 60), (170, 60), (140, 0)]
    draw_polygon(pentagon, color="purple")

    # contoh 4: poligon besar dan garis acak
    hexagon = [(-300, -100), (-240, -40), (-270, 30), (-330, 30), (-360, -40), (-300, -100)]
    draw_polygon(hexagon, color="orange", close=True)

    screen.update()

# Jalankan contoh
if __name__ == "__main__":
    example_draw()
    print("Gambar selesai. Klik jendela untuk menutup.")
    screen.exitonclick()
