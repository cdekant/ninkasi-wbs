# Tile-Konstanten und zugehoerige PNG-Dateien.
# Unicode Private Use Area U+E000–U+F8FF — kein Konflikt mit Cheepicus/CP437.
#
# Neues Tile hinzufuegen: Konstante + Eintrag in TILE_DATEIEN — fertig.

BRAUKESSEL = "\uE000"   # Hub-Ausgang

# Wird von main.py gelesen — ein Eintrag pro eigenem Tile.
TILE_DATEIEN = {
    ord(BRAUKESSEL): "assets/tiles/braukessel.png",
}
