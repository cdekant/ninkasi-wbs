"""Erzeugt assets/tiles/pflanze.png — 16x16 RGBA Pixel-Art-Sprite."""
import struct, zlib, os

def schreibe_png(pfad, breite, hoehe, pixel):
    def chunk(name, daten):
        c = name + daten
        return struct.pack(">I", len(daten)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
    ihdr = struct.pack(">II", breite, hoehe) + bytes([8, 6, 0, 0, 0])
    roh = b""
    for y in range(hoehe):
        roh += b"\x00"
        for x in range(breite):
            roh += bytes(pixel[y * breite + x])
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(roh))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, "wb") as f:
        f.write(png)

# Farbpalette (R, G, B, A)
T = (  0,   0,   0,   0)   # transparent
A = ( 12,  40,   5, 255)   # sehr dunkles Gruen
B = ( 30,  75,  12, 255)   # dunkles Gruen
C = ( 50, 105,  22, 255)   # mittel-dunkel
D = ( 72, 138,  32, 255)   # mittel
E = ( 95, 162,  42, 255)   # mittel-hell
F = (125, 188,  52, 255)   # hell
G = (160, 210,  65, 255)   # helles Gruen
H = (198, 230,  95, 255)   # sehr hell
I = (228, 244, 155, 255)   # Highlight

#  Pixel-Karte 16x16 (Zeile 0 = oben)
karte = [
    # 0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15
    [ T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T],  # 0
    [ T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T],  # 1
    [ T,  T,  T,  T,  T,  B,  C,  D,  D,  C,  B,  T,  T,  T,  T,  T],  # 2
    [ T,  T,  T,  B,  C,  E,  F,  G,  H,  G,  F,  E,  C,  B,  T,  T],  # 3
    [ T,  T,  B,  C,  E,  G,  H,  I,  H,  I,  H,  G,  E,  C,  B,  T],  # 4
    [ T,  T,  C,  D,  F,  H,  I,  H,  I,  H,  I,  F,  D,  C,  T,  T],  # 5
    [ T,  B,  C,  E,  G,  F,  H,  G,  H,  I,  G,  H,  E,  C,  B,  T],  # 6
    [ T,  B,  D,  E,  F,  H,  G,  F,  G,  H,  G,  F,  E,  D,  B,  T],  # 7
    [ T,  B,  C,  D,  G,  F,  H,  G,  F,  G,  H,  E,  D,  C,  B,  T],  # 8
    [ T,  B,  A,  C,  E,  G,  F,  H,  G,  F,  E,  D,  C,  A,  B,  T],  # 9
    [ T,  T,  B,  C,  D,  E,  G,  F,  E,  G,  D,  C,  B,  T,  T,  T],  # 10
    [ T,  T,  B,  A,  C,  D,  E,  E,  D,  E,  C,  A,  B,  T,  T,  T],  # 11
    [ T,  T,  T,  B,  A,  B,  C,  D,  C,  B,  A,  B,  T,  T,  T,  T],  # 12
    [ T,  T,  T,  T,  B,  A,  A,  B,  A,  A,  B,  T,  T,  T,  T,  T],  # 13
    [ T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T],  # 14
    [ T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T,  T],  # 15
]

pixel = [farbe for zeile in karte for farbe in zeile]
pfad = os.path.join(os.path.dirname(__file__), "..", "assets", "tiles", "pflanze.png")
schreibe_png(os.path.normpath(pfad), 16, 16, pixel)
print("Gespeichert:", os.path.normpath(pfad))
