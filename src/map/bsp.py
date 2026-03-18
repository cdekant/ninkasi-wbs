"""
BSP-Kartengenerator fuer Battle Ninkasi.

Erzeugt eine Karte als 2D-Liste von Zeichen (Strings).
Algorithmus: Binary Space Partitioning (BSP)
  1. Teile den verfuegbaren Bereich rekursiv in zwei Haelften
  2. Platziere in jedem Blatt-Bereich einen Raum
  3. Verbinde benachbarte Raeume mit Korridoren
  4. Platziere Objekte zufaellig in Raeumen
"""

import random
import json


# ---------------------------------------------------------------------------
# Hilfsdatenstruktur: Rechteck
# ---------------------------------------------------------------------------

class Rect:
    """Ein Rechteck auf der Karte — beschreibt einen Bereich oder Raum."""

    def __init__(self, x, y, breite, hoehe):
        self.x1 = x
        self.y1 = y
        self.x2 = x + breite
        self.y2 = y + hoehe

    @property
    def mitte_x(self):
        return (self.x1 + self.x2) // 2

    @property
    def mitte_y(self):
        return (self.y1 + self.y2) // 2

    @property
    def breite(self):
        return self.x2 - self.x1

    @property
    def hoehe(self):
        return self.y2 - self.y1


# ---------------------------------------------------------------------------
# BSP-Knoten
# ---------------------------------------------------------------------------

class BSPKnoten:
    """
    Ein Knoten im BSP-Baum.
    Jeder Knoten beschreibt einen rechteckigen Bereich der Karte.
    Blatt-Knoten (keine Kinder) bekommen einen Raum.
    """

    def __init__(self, bereich: Rect):
        self.bereich = bereich
        self.kind_a = None
        self.kind_b = None
        self.raum = None        # nur gesetzt wenn Blatt-Knoten

    def ist_blatt(self):
        return self.kind_a is None and self.kind_b is None

    def teile(self, min_groesse: int):
        """
        Teilt diesen Knoten zufaellig horizontal oder vertikal.
        Gibt False zurueck wenn der Bereich zu klein zum Teilen ist.
        """
        # Zu klein zum Teilen?
        if self.bereich.breite < min_groesse * 2 + 1:
            if self.bereich.hoehe < min_groesse * 2 + 1:
                return False

        # Welche Richtungen sind moeglich?
        kann_horizontal = self.bereich.hoehe >= min_groesse * 2 + 1
        kann_vertikal   = self.bereich.breite >= min_groesse * 2 + 1

        if kann_horizontal and kann_vertikal:
            horizontal = random.choice([True, False])
        else:
            horizontal = kann_horizontal

        if horizontal:
            # Schneide horizontal: obere und untere Haelfte
            schnitt = random.randint(
                self.bereich.y1 + min_groesse,
                self.bereich.y2 - min_groesse
            )
            self.kind_a = BSPKnoten(Rect(
                self.bereich.x1, self.bereich.y1,
                self.bereich.breite,
                schnitt - self.bereich.y1
            ))
            self.kind_b = BSPKnoten(Rect(
                self.bereich.x1, schnitt,
                self.bereich.breite,
                self.bereich.y2 - schnitt
            ))
        else:
            # Schneide vertikal: linke und rechte Haelfte
            schnitt = random.randint(
                self.bereich.x1 + min_groesse,
                self.bereich.x2 - min_groesse
            )
            self.kind_a = BSPKnoten(Rect(
                self.bereich.x1, self.bereich.y1,
                schnitt - self.bereich.x1,
                self.bereich.hoehe
            ))
            self.kind_b = BSPKnoten(Rect(
                schnitt, self.bereich.y1,
                self.bereich.x2 - schnitt,
                self.bereich.hoehe
            ))

        return True

    def baue_baum(self, min_groesse: int, tiefe: int):
        """Teilt rekursiv bis zur gewuenschten Tiefe oder bis zu klein."""
        if tiefe <= 0:
            return
        if self.teile(min_groesse):
            self.kind_a.baue_baum(min_groesse, tiefe - 1)
            self.kind_b.baue_baum(min_groesse, tiefe - 1)

    def alle_blaetter(self):
        """Gibt alle Blatt-Knoten zurueck (als Liste)."""
        if self.ist_blatt():
            return [self]
        blaetter = []
        if self.kind_a:
            blaetter += self.kind_a.alle_blaetter()
        if self.kind_b:
            blaetter += self.kind_b.alle_blaetter()
        return blaetter

    def raum_holen(self):
        """
        Gibt den Raum dieses Knotens zurueck.
        Fuer innere Knoten: gibt einen Raum aus den Kindern zurueck.
        """
        if self.raum:
            return self.raum
        raum_a = self.kind_a.raum_holen() if self.kind_a else None
        raum_b = self.kind_b.raum_holen() if self.kind_b else None
        if raum_a and raum_b:
            return random.choice([raum_a, raum_b])
        return raum_a or raum_b


# ---------------------------------------------------------------------------
# Karte generieren
# ---------------------------------------------------------------------------

def generiere_karte(grammatik: dict, breite: int, hoehe: int, seed=None) -> list:
    """
    Erzeugt eine Karte als 2D-Liste von Zeichen.
    Gibt eine Liste von Strings zurueck (eine pro Zeile).

    grammatik: dict aus levels.json fuer das gewuenschte Level
    breite, hoehe: Groesse der Karte in Kacheln
    seed: optionaler Zufalls-Seed (None = zufaellig)
    """

    if seed is not None:
        random.seed(seed)

    kacheln = grammatik["kacheln"]
    wand    = kacheln["wand"]
    boden   = kacheln["boden"]

    # Karte mit Waenden fuellen
    karte = [[wand] * breite for _ in range(hoehe)]

    # --- BSP-Baum aufbauen ---
    min_raum = max(grammatik["raum_breite_min"], grammatik["raum_hoehe_min"])

    wurzel = BSPKnoten(Rect(0, 0, breite, hoehe))

    # Tiefe so waehlen dass Raumanzahl im gewuenschten Bereich landet
    # Bei Tiefe t entstehen maximal 2^t Blaetter
    raeume_max = grammatik["raeume_max"]
    tiefe = 1
    while (2 ** tiefe) < raeume_max:
        tiefe += 1

    wurzel.baue_baum(min_raum, tiefe)

    # --- Raeume in Blaetter platzieren ---
    blaetter = wurzel.alle_blaetter()

    # Auf gewuenschte Raumanzahl begrenzen
    raeume_min = grammatik["raeume_min"]
    anzahl = random.randint(raeume_min, raeume_max)
    anzahl = min(anzahl, len(blaetter))
    blaetter = random.sample(blaetter, anzahl)

    raeume = []
    for blatt in blaetter:
        b = blatt.bereich
        max_raumbreite = min(grammatik["raum_breite_max"], b.breite - 2)
        max_raumhoehe  = min(grammatik["raum_hoehe_max"],  b.hoehe  - 2)
        min_raumbreite = grammatik["raum_breite_min"]
        min_raumhoehe  = grammatik["raum_hoehe_min"]

        if max_raumbreite < min_raumbreite or max_raumhoehe < min_raumhoehe:
            continue

        raumbreite = random.randint(min_raumbreite, max_raumbreite)
        raumhoehe  = random.randint(min_raumhoehe,  max_raumhoehe)

        rx = random.randint(b.x1 + 1, b.x2 - raumbreite - 1)
        ry = random.randint(b.y1 + 1, b.y2 - raumhoehe  - 1)

        raum = Rect(rx, ry, raumbreite, raumhoehe)
        blatt.raum = raum
        raeume.append(raum)

        # Raum in Karte graben
        for y in range(raum.y1, raum.y2):
            for x in range(raum.x1, raum.x2):
                karte[y][x] = boden

    # --- Raeume mit Korridoren verbinden ---
    # Verbinde benachbarte Blatt-Paare ueber ihren gemeinsamen Elternknoten
    _verbinde_knoten(wurzel, karte, boden)

    # --- Objekte platzieren ---
    for obj_def in grammatik.get("objekte", []):
        obj_typ  = obj_def["typ"]
        obj_char = kacheln.get(f"objekt_{obj_typ}", "?")
        for raum in raeume:
            anzahl_obj = random.randint(obj_def["min"], obj_def["max"])
            platziert  = 0
            versuche   = 0
            while platziert < anzahl_obj and versuche < 20:
                ox = random.randint(raum.x1, raum.x2 - 1)
                oy = random.randint(raum.y1, raum.y2 - 1)
                if karte[oy][ox] == boden:
                    karte[oy][ox] = obj_char
                    platziert += 1
                versuche += 1

    # 2D-Liste in Liste von Strings umwandeln
    return ["".join(zeile) for zeile in karte]


# ---------------------------------------------------------------------------
# Korridore
# ---------------------------------------------------------------------------

def _verbinde_knoten(knoten: BSPKnoten, karte: list, boden: str):
    """Verbindet rekursiv alle Raum-Paare im BSP-Baum mit Korridoren."""
    if knoten.ist_blatt():
        return

    _verbinde_knoten(knoten.kind_a, karte, boden)
    _verbinde_knoten(knoten.kind_b, karte, boden)

    raum_a = knoten.kind_a.raum_holen()
    raum_b = knoten.kind_b.raum_holen()

    if raum_a and raum_b:
        _grabe_korridor(karte, boden,
                        raum_a.mitte_x, raum_a.mitte_y,
                        raum_b.mitte_x, raum_b.mitte_y)


def _grabe_korridor(karte, boden, x1, y1, x2, y2):
    """Grabt einen L-foermigen Korridor von (x1,y1) nach (x2,y2)."""
    # Zufaellig: erst horizontal dann vertikal, oder umgekehrt
    if random.choice([True, False]):
        _grabe_h(karte, boden, x1, x2, y1)
        _grabe_v(karte, boden, y1, y2, x2)
    else:
        _grabe_v(karte, boden, y1, y2, x1)
        _grabe_h(karte, boden, x1, x2, y2)


def _grabe_h(karte, boden, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        if 0 <= y < len(karte) and 0 <= x < len(karte[y]):
            karte[y][x] = boden


def _grabe_v(karte, boden, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        if 0 <= y < len(karte) and 0 <= x < len(karte[y]):
            karte[y][x] = boden
