"""Hub-Karte (Mannis Pilsstube): kreisrunder Raum um die Bildschirmmitte."""

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
        "symbol": "\u03a9",          # Ω  (CP437 234)
        "x":      cx,
        "y":      cy,
        "typ":    "ausgang",
        "farbe":  (255, 140, 0),     # Orange wie Feuer / Braukessel
        "name":   "Braukessel (Ausgang)",
    }

    return karte, cx - 2, cy, ausgang
