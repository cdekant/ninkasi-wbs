"""Algorithmus-Dispatcher fuer die Kartengenerierung.

Liest 'algorithmus' aus der Level-Grammatik und ruft den
passenden Generator auf. Neue Algorithmen hier eintragen.

Symbolische Tile-Namen (z.B. "PFLANZE") in der Grammatik werden
automatisch gegen src/tiles.py aufgeloest, bevor der Generator
aufgerufen wird — levels.json muss keine rohen Unicode-Codepoints kennen.
"""

import src.tiles as tiles
from src.map.bsp    import generiere_karte as _bsp
from src.map.raster import generiere_karte as _raster


def _kacheln_aufloesen(grammatik):
    """Ersetzt symbolische Tile-Namen in grammatik['kacheln'] durch echte Zeichen.

    Beispiel: "PFLANZE" -> tiles.PFLANZE ("\uE040")
    Unbekannte Namen und direkte Zeichen bleiben unveraendert.
    """
    kacheln = grammatik.get("kacheln", {})
    return {
        key: tiles.TILE_NAMEN.get(wert, wert)
        for key, wert in kacheln.items()
    }


def generiere_karte(grammatik, breite, hoehe, seed=None):
    grammatik = {**grammatik, "kacheln": _kacheln_aufloesen(grammatik)}
    algo = grammatik.get("algorithmus", "bsp")
    if algo == "raster":
        return _raster(grammatik, breite, hoehe, seed)
    return _bsp(grammatik, breite, hoehe, seed)
