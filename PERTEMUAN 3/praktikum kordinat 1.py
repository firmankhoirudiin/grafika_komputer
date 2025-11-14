import math

# Input koordinat titik pertama
x1 = float(input("Masukkan x1: "))
y1 = float(input("Masukkan y1: "))

# Input koordinat titik kedua
x2 = float(input("Masukkan x2: "))
y2 = float(input("Masukkan y2: "))

# Hitung jarak antara dua titik
jarak = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Tentukan kuadran titik pertama
if x1 > 0 and y1 > 0:
    kuadran = "Kuadran I"
elif x1 < 0 and y1 > 0:
    kuadran = "Kuadran II"
elif x1 < 0 and y1 < 0:
    kuadran = "Kuadran III"
elif x1 > 0 and y1 < 0:
    kuadran = "Kuadran IV"
else:
    kuadran = "Berada di sumbu"

# Tampilkan hasil perhitungan
print("\n=== HASIL ===")
print(f"Titik pertama: ({x1}, {y1})")
print(f"Titik kedua  : ({x2}, {y2})")
print(f"Jarak antar titik: {jarak:.2f}")
print(f"Titik pertama berada di: {kuadran}")

