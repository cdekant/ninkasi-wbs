"""Hub-Karte: kreisrunder Raum um die Bildschirmmitte."""

from src.tiles import BRAUKESSEL

HUB_RADIUS = 7


def generiere_hub(breite, hoehe):
    """Kreisrunder Raum (Radius 7) um die Mitte. Rest: Wand.

    Gibt zurueck: (karte, start_x, start_y, ausgang_objekt)
    - karte: Liste von Strings, nur '.' und '#'
    - start_x/y: Spieler-Startposition (westlich des Ausgangs)
    - ausgang_objekt: Dict mit Symbol, Position und Typ
    """
    cx = breite // 2
    cy = hoehe  // 2

    karte = []
    for y in range(hoehe):
        zeile = ""
        for x in range(breite):
            if (x - cx) ** 2 + (y - cy) ** 2 <= HUB_RADIUS ** 2:
                zeile += "."
            else:
                zeile += "#"
        karte.append(zeile)

    # Ausgang als separates Objekt — '.' bleibt im Karten-String,
    # damit FOV / Transparenz korrekt funktionieren.
    ausgang = {
        "symbol": BRAUKESSEL,          # eigenes Tile (U+E000)
        "x":      cx,
        "y":      cy,
        "typ":    "ausgang",
        "farbe":  (255, 255, 255),   # Weiss = originale PNG-Farben ungefaerbt
        "name":   "Braukessel (Ausgang)",
    }

    return karte, cx - 2, cy, ausgang
