"""Gegner-KI: Bewegung und Verhalten auf der Karte.

Wird nach jedem Spielerzug aufgerufen (ki_tick).
Jeder lebende Gegner bekommt eine Aktion gemaess seinem verhalten-Feld:

    statisch    — bewegt sich nie
    territorial — verfolgt nur solange Spieler im sicht_radius
    verfolgen   — verfolgt dauerhaft sobald Spieler einmal gesehen
    flucht      — weicht dem Spieler immer aus

flucht_hp_pct: optionaler Schwellwert (0-100). Faellt der Gegner darunter,
               wechselt er unabhaengig vom verhalten-Feld in Fluchtmodus.

geschwindigkeit: Werte < 1.0 bedeuten, der Gegner bewegt sich nicht jeden Zug.
    1.0  = bewegt sich jeden Spielerzug
    0.5  = bewegt sich jeden zweiten Spielerzug
    2.0  = bewegt sich zweimal pro Spielerzug (noch nicht implementiert, >= 1 = 1)

Gibt (nah_liste, fern_liste) zurueck:
    nah_liste  — Eintraege deren Gegner das Spielerfeld betreten hat (Nahkampf)
    fern_liste — Eintraege deren Gegner den Spieler aus der Ferne angreift
"""

import math
import src.systems.sichtfeld as sichtfeld


def _kann_fernkampf(eintrag, spieler_x, spieler_y, transparenz):
    """True wenn der Gegner den Spieler aus der Ferne angreifen kann.

    Prueft: Fernkampf-Angriffe vorhanden, Spieler in Reichweite, Sichtlinie frei.
    """
    if transparenz is None:
        return False
    g = eintrag["gegner"]
    fern_angriffe = [a for a in g.angriffe if a.get("reichweite", 1) > 1]
    if not fern_angriffe:
        return False
    max_reichweite = max(a["reichweite"] for a in fern_angriffe)
    dist = math.sqrt(
        (eintrag["x"] - spieler_x) ** 2 +
        (eintrag["y"] - spieler_y) ** 2
    )
    if dist > max_reichweite:
        return False
    return sichtfeld.sichtlinie_frei(
        transparenz, eintrag["x"], eintrag["y"], spieler_x, spieler_y
    )


def ki_tick(gegner_auf_karte, spieler_x, spieler_y, karte, transparenz=None):
    """Bewegt alle lebenden Gegner einmal gemaess ihrem Verhalten.

    Gibt (nah_liste, fern_liste) zurueck:
        nah_liste  — Eintraege deren Gegner das Spielerfeld betreten hat (Nahkampf)
        fern_liste — Eintraege deren Gegner den Spieler aus der Ferne angreift
    """
    nah_liste  = []
    fern_liste = []
    for eintrag in gegner_auf_karte:
        g = eintrag["gegner"]
        if not g.lebt:
            continue

        # Aktives Verhalten bestimmen (flucht_hp_pct kann es ueberschreiben)
        verhalten = g.verhalten
        if g.flucht_hp_pct is not None:
            if g.hp < g.hp_max * (g.flucht_hp_pct / 100):
                verhalten = "flucht"

        if verhalten == "statisch":
            continue

        # Geschwindigkeit: Zaehler akkumulieren, nur bewegen wenn >= 1.0
        g.bewegungs_zaehler += g.geschwindigkeit
        if g.bewegungs_zaehler < 1.0:
            continue
        g.bewegungs_zaehler -= 1.0

        # Fernkampf-Check: Gegner mit reichweite > 1 koennen aus der Distanz angreifen
        dist_chebyshev = max(abs(eintrag["x"] - spieler_x), abs(eintrag["y"] - spieler_y))
        if verhalten != "flucht" and dist_chebyshev > 1:
            if _kann_fernkampf(eintrag, spieler_x, spieler_y, transparenz):
                fern_liste.append(eintrag)
                continue

        # Distanz zum Spieler (euklidisch fuer Radiuscheck)
        distanz = math.sqrt(
            (eintrag["x"] - spieler_x) ** 2 +
            (eintrag["y"] - spieler_y) ** 2
        )

        # Richtung berechnen
        if verhalten == "territorial":
            if distanz > g.sicht_radius:
                g.ki_zustand = "idle"
                continue
            g.ki_zustand = "aktiv"
            dx, dy = _schritt_zu(
                eintrag["x"], eintrag["y"],
                spieler_x, spieler_y,
                karte, gegner_auf_karte, eintrag,
            )

        elif verhalten == "verfolgen":
            # Aktivieren wenn Spieler im sicht_radius; deaktivieren wenn Abstand zu gross
            if distanz > g.sicht_radius:
                g.ki_zustand = "idle"
                continue
            g.ki_zustand = "aktiv"
            dx, dy = _schritt_zu(
                eintrag["x"], eintrag["y"],
                spieler_x, spieler_y,
                karte, gegner_auf_karte, eintrag,
            )

        elif verhalten == "flucht":
            dx, dy = _schritt_weg(
                eintrag["x"], eintrag["y"],
                spieler_x, spieler_y,
                karte, gegner_auf_karte, eintrag,
            )

        else:
            continue

        if dx == 0 and dy == 0:
            continue

        nx, ny = eintrag["x"] + dx, eintrag["y"] + dy

        # Spielerfeld erreicht -> als Nahkaempfer vormerken, nicht bewegen
        if nx == spieler_x and ny == spieler_y:
            nah_liste.append(eintrag)
            continue

        eintrag["x"] = nx
        eintrag["y"] = ny

    return nah_liste, fern_liste


# ---------------------------------------------------------------------------
# Bewegungs-Hilfsfunktionen
# ---------------------------------------------------------------------------

def _ist_frei(x, y, karte, gegner_auf_karte, ausgenommen):
    """True wenn (x, y) ein begehbarer Boden ist und kein anderer Gegner dort steht."""
    if y < 0 or y >= len(karte):
        return False
    if x < 0 or x >= len(karte[y]):
        return False
    if karte[y][x] != ".":
        return False
    for e in gegner_auf_karte:
        if e is ausgenommen:
            continue
        if e["x"] == x and e["y"] == y and e["gegner"].lebt:
            return False
    return True


def _schritt_zu(gx, gy, zx, zy, karte, gegner_auf_karte, ausgenommen):
    """Gibt (dx, dy) zurueck, der (gx,gy) am naechsten an (zx,zy) bringt.

    Das Zielfeld selbst (Spielerposition) wird als erreichbar behandelt
    auch wenn es nicht 'frei' ist — Betreten loest Kampf aus.
    """
    bester = (0, 0)
    beste_dist = float("inf")

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = gx + dx, gy + dy
            # Spielerfeld ist explizit erlaubt
            zielfeld = (nx == zx and ny == zy)
            if not zielfeld and not _ist_frei(nx, ny, karte, gegner_auf_karte, ausgenommen):
                continue
            dist = (nx - zx) ** 2 + (ny - zy) ** 2
            if dist < beste_dist:
                beste_dist = dist
                bester = (dx, dy)

    return bester


def _schritt_weg(gx, gy, fx, fy, karte, gegner_auf_karte, ausgenommen):
    """Gibt (dx, dy) zurueck, der (gx,gy) am weitesten von (fx,fy) entfernt."""
    bester = (0, 0)
    beste_dist = -1

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = gx + dx, gy + dy
            if not _ist_frei(nx, ny, karte, gegner_auf_karte, ausgenommen):
                continue
            dist = (nx - fx) ** 2 + (ny - fy) ** 2
            if dist > beste_dist:
                beste_dist = dist
                bester = (dx, dy)

    return bester
