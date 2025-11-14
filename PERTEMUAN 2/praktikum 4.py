import math

def hitung_jarak(x1, y1, x2, y2):
    jarak = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return jarak

hasil = hitung_jarak(0, 0, 3, 4)
print(f"Jarak antara dua titik: {hasil}")
