# Ukuran layar
lebar = 10
tinggi = 5

# Posisi titik
x = 3
y = 2

# Gambar layar
for baris in range(tinggi):
    for kolom in range(lebar):
        if kolom == x and baris == y:
            print("X", end=" ")
        else:
            print(".", end=" ")
    print()
