"""Sichtfeld-Berechnung (FOV) und Fog of War fuer Battle Ninkasi.

tcod.map.compute_fov() erwartet numpy-Arrays mit (row, col) = (y, x) Indexierung.
Das Ergebnis ist ein bool-Array: True = aktuell sichtbar.
ERKUNDET ist ein separates bool-Array: True = schon einmal gesehen.
"""

import numpy as np
import tcod.map
import tcod.constants

FOV_BASIS_RADIUS = 2   # Basis-Sichtweite ohne Skill-Boni; 0 waere unbegrenzt


def baue_transparenz(karte):
    """Erstellt das Transparenz-Array aus der Karte.

    True  = durchsichtig (Boden, Spieler kann hindurchsehen)
    False = undurchsichtig (Wand, blockiert Sichtlinie)
    """
    hoehe = len(karte)
    breite = len(karte[0]) if hoehe > 0 else 0
    t = np.zeros((hoehe, breite), dtype=bool)
    for y, zeile in enumerate(karte):
        for x, kachel in enumerate(zeile):
            t[y, x] = (kachel == ".")
    return t


def neues_erkundet(karte):
    """Erstellt ein leeres Erkundet-Array (alles unbekannt)."""
    hoehe = len(karte)
    breite = len(karte[0]) if hoehe > 0 else 0
    return np.zeros((hoehe, breite), dtype=bool)


def berechne_fov(transparenz, spieler_x, spieler_y, radius=FOV_BASIS_RADIUS):
    """Berechnet das aktuelle Sichtfeld ausgehend von der Spielerposition.

    radius: Sichtweite in Kacheln; 0 waere unbegrenzt.
    light_walls=True: Waende am Rand des Sichtfelds werden noch angezeigt.
    Gibt ein bool-Array zurueck: True = gerade sichtbar.
    """
    return tcod.map.compute_fov(
        transparenz,
        (spieler_y, spieler_x),          # tcod erwartet (row, col)
        radius=radius,
        light_walls=True,
        algorithm=tcod.constants.FOV_SYMMETRIC_SHADOWCAST,
    )


def aktualisiere_erkundet(erkundet, fov):
    """Markiert alle aktuell sichtbaren Felder dauerhaft als erkundet."""
    erkundet |= fov   # bitweises OR: alle True-Stellen in fov bleiben True
