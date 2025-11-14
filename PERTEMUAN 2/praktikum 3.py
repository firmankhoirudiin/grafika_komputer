x = int(input("Masukkan nilai x: "))

if x > 0:
    print("Titik di kanan layar.")
elif x < 0:
    print("Titik di kiri layar.")
else:
    print("Titik di tengah.")


print("Menampilkan 5 titik:")
for i in range(1, 6):
    print(f"Titik ke-{i}")
