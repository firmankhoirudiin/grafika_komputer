# ===== DDA line drawing (versi final yang rapi) =====
x1, y1 = 0, 0
x2, y2 = 5, 3

koorx = []
koory = []

# 1) hitung selisih
dx = x2 - x1
dy = y2 - y1

# 2) jumlah langkah = nilai absolut terbesar antara dx dan dy
langkah = max(abs(dx), abs(dy))

# 3) kenaikan per langkah (floating point)
lx = dx / langkah
ly = dy / langkah

# 4) mulai dari titik awal, tambahkan kenaikan tiap langkah
x_titik = x1
y_titik = y1

for i in range(int(langkah) + 1):   # +1 supaya termasuk titik akhir
    koorx.append(round(x_titik))
    koory.append(round(y_titik))
    x_titik += lx
    y_titik += ly

# 5) buat set pasangan (x,y) untuk pengecekan cepat ketika menampilkan grid
points = set(zip(koorx, koory))

# 6) tampilkan grid (dari y tertinggi ke y terendah supaya orientasi 'matriks' benar)
#    kita tentukan batas grid (misal 0..10) agar terlihat
x_min, x_max = 0, 10
y_min, y_max = 0, 10

for y in range(y_max, y_min - 1, -1):
    for x in range(x_min, x_max + 1):
        if (x, y) in points:
            print("*", end=" ")
        else:
            print(".", end=" ")
    print()

print("\nkoorx:", koorx)
print("koory:", koory)