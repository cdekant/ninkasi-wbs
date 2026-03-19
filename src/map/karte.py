"""Algorithmus-Dispatcher fuer die Kartengenerierung.

Liest 'algorithmus' aus der Level-Grammatik und ruft den
passenden Generator auf. Neue Algorithmen hier eintragen.
"""

from src.map.bsp    import generiere_karte as _bsp
from src.map.raster import generiere_karte as _raster


def generiere_karte(grammatik, breite, hoehe, seed=None):
    algo = grammatik.get("algorithmus", "bsp")
    if algo == "raster":
        return _raster(grammatik, breite, hoehe, seed)
    return _bsp(grammatik, breite, hoehe, seed)
