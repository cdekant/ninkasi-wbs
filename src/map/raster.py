"""
Raster-Kartengenerator fuer Battle Ninkasi.

Teilt die Karte in ein gleichmaessiges Raster aus Zellen.
In jeder Zelle wird ein Raum zentriert platziert.
Benachbarte Raeume werden mit Korridoren verbunden.
"""

import random


class _Rect:
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


def generiere_karte(grammatik, breite, hoehe, seed=None):
    """
    Erzeugt eine Raster-Karte als Liste von Strings.

    grammatik: dict aus levels.json
    breite, hoehe: Kartengroesse in Kacheln
    """
    if seed is not None:
        random.seed(seed)

    spalten  = grammatik.get("raster_spalten",  3)
    zeilen   = grammatik.get("raster_zeilen",   2)
    belegung = grammatik.get("raster_belegung", 1.0)
    korr_b   = grammatik.get("korridor_breite", 1)

    kacheln  = grammatik["kacheln"]
    wand     = kacheln["wand"]
    boden    = kacheln["boden"]

    karte = [[wand] * breite for _ in range(hoehe)]

    zell_b = breite // spalten
    zell_h = hoehe  // zeilen

    # Gitter aufbauen: gitter[z][s] = _Rect oder None
    gitter = []
    for z in range(zeilen):
        reihe = []
        for s in range(spalten):
            if random.random() > belegung:
                reihe.append(None)
            else:
                reihe.append(_raum_in_zelle(s, z, zell_b, zell_h, grammatik, breite, hoehe, karte, boden))
        gitter.append(reihe)

    # Mindestzahl Raeume sicherstellen: leere Zellen nachfuellen bis raeume_min erreicht
    raeume_min = grammatik.get("raeume_min", 1)
    alle_raeume = [r for reihe in gitter for r in reihe if r is not None]
    if len(alle_raeume) < raeume_min:
        leere = [(z, s) for z in range(zeilen) for s in range(spalten) if gitter[z][s] is None]
        random.shuffle(leere)
        for z, s in leere:
            if len(alle_raeume) >= raeume_min:
                break
            raum = _raum_in_zelle(s, z, zell_b, zell_h, grammatik, breite, hoehe, karte, boden)
            if raum:
                gitter[z][s] = raum
                alle_raeume.append(raum)

    # Korridore: rechten und unteren Nachbar verbinden
    for z in range(zeilen):
        for s in range(spalten):
            raum = gitter[z][s]
            if raum is None:
                continue
            if s + 1 < spalten and gitter[z][s + 1]:
                _korridor(karte, boden, hoehe, breite,
                          raum.mitte_x, raum.mitte_y,
                          gitter[z][s + 1].mitte_x, gitter[z][s + 1].mitte_y,
                          korr_b)
            if z + 1 < zeilen and gitter[z + 1][s]:
                _korridor(karte, boden, hoehe, breite,
                          raum.mitte_x, raum.mitte_y,
                          gitter[z + 1][s].mitte_x, gitter[z + 1][s].mitte_y,
                          korr_b)

    # Objekte platzieren
    interaktive_objekte = []
    for obj_def in grammatik.get("objekte", []):
        obj_typ   = obj_def["typ"]
        obj_char  = kacheln.get(f"objekt_{obj_typ}", "?")
        abstand   = obj_def.get("abstand_wand", 0)
        position  = obj_def.get("position", "zufall")
        loot_pool = obj_def.get("loot_pool")

        for raum in alle_raeume:
            anzahl   = random.randint(obj_def["min"], obj_def["max"])
            gesetzt  = 0
            versuche = 0
            while gesetzt < anzahl and versuche < 30:
                versuche += 1
                if position == "mitte":
                    ox = raum.mitte_x + random.randint(-1, 1)
                    oy = raum.mitte_y + random.randint(-1, 1)
                else:
                    x1 = raum.x1 + abstand
                    x2 = raum.x2 - 1 - abstand
                    y1 = raum.y1 + abstand
                    y2 = raum.y2 - 1 - abstand
                    if x1 > x2 or y1 > y2:
                        break
                    ox = random.randint(x1, x2)
                    oy = random.randint(y1, y2)
                if (0 <= oy < hoehe and 0 <= ox < breite
                        and karte[oy][ox] == boden):
                    karte[oy][ox] = obj_char
                    if loot_pool is not None:
                        interaktive_objekte.append({
                            "x": ox, "y": oy,
                            "typ": obj_typ,
                            "loot_pool": loot_pool,
                        })
                    gesetzt += 1

    # Fenster in Wandsegmente einsetzen
    _platziere_fenster(karte, hoehe, breite, wand, boden,
                       grammatik.get("fenster", []))

    return ["".join(zeile) for zeile in karte], interaktive_objekte


def _platziere_fenster(karte, hoehe, breite, wand, boden, fenster_defs):
    """Fuellt alle horizontalen Raumperimeter-Wandsegmente mit Fenster-Tiles.

    Wandsegment: zusammenhaengender Lauf von Wand-Kacheln in einer Zeile,
    bei denen mindestens eine Kachel direkt an Boden angrenzt.
    Jedes Segment wird von innen (1px Rand freihalten) vollstaendig belegt —
    zufaellige Mischung aus den uebergebenen Fenster-Typen nach Gruppengroesse.
    """
    if not fenster_defs:
        return

    def fuelle_segment(positionen, setze):
        """Fuelle eine Liste von Positionen mit zufaelligen Fenster-Gruppen.
        1px Rand an beiden Enden bleibt Wand."""
        pos  = 1                        # 1px Rand links/oben freihalten
        ende = len(positionen) - 1      # 1px Rand rechts/unten freihalten
        while pos < ende:
            restplatz = ende - pos
            moeglich = [f for f in fenster_defs
                        if restplatz >= f.get("gruppe_min", 1)]
            if not moeglich:
                break
            fdef  = random.choice(moeglich)
            g_len = random.randint(fdef.get("gruppe_min", 1),
                                   min(fdef.get("gruppe_max", 2), restplatz))
            for i in range(g_len):
                setze(positionen[pos + i], fdef["typ"])
            pos += g_len

    # Horizontale Segmente (Wand mit Boden oben oder unten)
    for r in range(1, hoehe - 1):
        start = None
        for c in range(0, breite + 1):
            in_seg = (c < breite and karte[r][c] == wand
                      and (karte[r - 1][c] == boden or karte[r + 1][c] == boden))
            if in_seg:
                if start is None:
                    start = c
            else:
                if start is not None:
                    cols = list(range(start, c))
                    def setze_h(col, ch, _r=r):
                        karte[_r][col] = ch
                    fuelle_segment(cols, setze_h)
                    start = None

    # Vertikale Segmente (Wand mit Boden links oder rechts)
    for c in range(1, breite - 1):
        start = None
        for r in range(0, hoehe + 1):
            in_seg = (r < hoehe and karte[r][c] == wand
                      and (karte[r][c - 1] == boden or karte[r][c + 1] == boden))
            if in_seg:
                if start is None:
                    start = r
            else:
                if start is not None:
                    rows = list(range(start, r))
                    def setze_v(row, ch, _c=c):
                        karte[row][_c] = ch
                    fuelle_segment(rows, setze_v)
                    start = None

    # Cleanup: Ecken und Segment-Enden ersetzen.
    # Jede verbleibende Wand-Kachel die an Boden oder ein Fenster-Tile angrenzt
    # wird durch das kleinste verfuegbare Fenster-Tile ersetzt.
    fenster_chars = {fdef["typ"] for fdef in fenster_defs}
    einzel = min(fenster_defs, key=lambda f: f.get("gruppe_min", 1))["typ"]
    geaendert = True
    while geaendert:
        geaendert = False
        for r in range(1, hoehe - 1):
            for c in range(1, breite - 1):
                if karte[r][c] != wand:
                    continue
                nachbarn = [karte[r-1][c], karte[r+1][c],
                            karte[r][c-1], karte[r][c+1]]
                if any(n == boden or n in fenster_chars for n in nachbarn):
                    karte[r][c] = einzel
                    geaendert = True


def _raum_in_zelle(s, z, zell_b, zell_h, grammatik, breite, hoehe, karte, boden):
    """Platziert einen Raum in Gitterzelle (z, s). Gibt _Rect zurueck oder None wenn zu eng."""
    ox = s * zell_b
    oy = z * zell_h
    rb_max = min(grammatik["raum_breite_max"], zell_b - 2)
    rh_max = min(grammatik["raum_hoehe_max"],  zell_h - 2)
    rb_min = grammatik["raum_breite_min"]
    rh_min = grammatik["raum_hoehe_min"]
    if rb_max < rb_min or rh_max < rh_min:
        return None
    rb = random.randint(rb_min, rb_max)
    rh = random.randint(rh_min, rh_max)
    rx = ox + (zell_b - rb) // 2
    ry = oy + (zell_h - rh) // 2
    rx = max(1, min(rx, breite - rb - 1))
    ry = max(1, min(ry, hoehe  - rh - 1))
    raum = _Rect(rx, ry, rb, rh)
    for y in range(raum.y1, raum.y2):
        for x in range(raum.x1, raum.x2):
            karte[y][x] = boden
    return raum


def _korridor(karte, boden, h, w, x1, y1, x2, y2, breite):
    """L-foermiger Korridor mit konfigurierbarer Breite.

    Fuer jede Breitenstufe (offset) wird ein eigener 1-breiter
    Korridor gezeichnet — einmal horizontal, einmal vertikal versetzt.
    """
    for offset in range(breite):
        # Horizontales Stueck bei y1+offset
        for x in range(min(x1, x2), max(x1, x2) + 1):
            ny = y1 + offset
            if 0 <= ny < h and 0 <= x < w:
                karte[ny][x] = boden
        # Vertikales Stueck bei x2+offset
        for y in range(min(y1, y2), max(y1, y2) + 1):
            nx = x2 + offset
            if 0 <= y < h and 0 <= nx < w:
                karte[y][nx] = boden
