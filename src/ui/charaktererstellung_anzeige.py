"""Rendering fuer Charaktererstellung und Eigenschaftspunkt-Vergabe."""

import tcod

# ---------------------------------------------------------------------------
# Eigenschafts-Metadaten
# ---------------------------------------------------------------------------

# Reihenfolge der Eigenschaften (muss mit player.py uebereinstimmen)
EIGENSCHAFTEN_REIHENFOLGE = [
    "koerperkraft",
    "geschicklichkeit",
    "wissen",
    "weisheit",
    "charisma",
    "geist",
]

_EIGENSCHAFT_ANZEIGE = {
    "koerperkraft":     "Körperkraft",
    "geschicklichkeit": "Geschicklichkeit",
    "wissen":           "Wissen",
    "weisheit":         "Weisheit",
    "charisma":         "Charisma",
    "geist":            "Geist",
}

_EIGENSCHAFT_BESCHREIBUNG = {
    "koerperkraft":     "Physische Ausdauer — erleichtert Skills in Lebenskraft und Tennentänzerei.",
    "geschicklichkeit": "Präzision und Kampftechnik — erleichtert Skills in Kesselzorn und Sudwall.",
    "wissen":           "Brauwissen und Naturkunde — erleichtert Skills in Natur-, Korn- und Braukunde.",
    "weisheit":         "Magisches Gespür — erleichtert Skills in Kessel-Magie und Meta-Braukunde.",
    "charisma":         "Soziale Kraft — erleichtert Skills in Marktschreierei und Nachschub.",
    "geist":            "Psi und Zahlenmystik — erleichtert Skills in Brennblasen-Psi und Zahlenkult.",
}

# ---------------------------------------------------------------------------
# Farbpalette
# ---------------------------------------------------------------------------

F_TITEL         = (255, 215,   0)   # Gold
F_NORMAL        = (200, 200, 200)
F_AUSGEWAEHLT   = (255, 255, 100)   # Gelb
F_GESPERRT      = ( 70,  70,  70)
F_PUNKTE_VOLL   = (100, 200, 120)   # Gruen (verbleibend = 0)
F_PUNKTE_OFFEN  = (200, 200, 200)
F_PUNKTE_LEER   = (180,  80,  80)   # Rot (noch Punkte uebrig beim ENTER)
F_BESCHREIBUNG  = (150, 150, 255)   # Hellblau
F_FOOTER        = ( 80,  80,  80)
F_FOOTER_GRAU   = ( 50,  50,  50)   # ENTER gesperrt-Hinweis

BG_DUNKEL       = ( 12,  12,  25)
BG_AUSGEWAEHLT  = ( 40,  40,  80)


# ---------------------------------------------------------------------------
# Charaktererstellungs-Bildschirm
# ---------------------------------------------------------------------------

def zeichne_charaktererstellung(console, eigenschaften, auswahl, verbleibend):
    """Zeichnet den Charaktererstellungs-Bildschirm.

    eigenschaften -- dict {"koerperkraft": 0, ...} mit aktuell verteilten Punkten
    auswahl       -- int: Index der markierten Eigenschaft (0–5)
    verbleibend   -- int: noch nicht verteilte Punkte
    """
    w = console.width
    h = console.height

    # Hintergrund
    console.draw_rect(0, 0, w, h, 32, bg=BG_DUNKEL)

    # Rahmen
    _rahmen(console, w, h)

    # Titel
    console.print(w // 2, 1, "CHARAKTERERSTELLUNG", fg=F_TITEL, alignment=tcod.CENTER)

    # Verbleibende Punkte
    farbe_punkte = F_PUNKTE_VOLL if verbleibend == 0 else F_PUNKTE_OFFEN
    console.print(2, 3, f"Verbleibende Punkte: {verbleibend}", fg=farbe_punkte)

    # Eigenschaften-Liste
    y = 5
    for i, key in enumerate(EIGENSCHAFTEN_REIHENFOLGE):
        punkte = eigenschaften.get(key, 0)
        balken = "\u25cf" * punkte + "\u25cb" * max(0, 10 - punkte)
        name   = _EIGENSCHAFT_ANZEIGE[key]

        if i == auswahl:
            console.draw_rect(1, y, w - 2, 1, 32, bg=BG_AUSGEWAEHLT)
            marker = "\u25ba"  # ►
            farbe  = F_AUSGEWAEHLT
        else:
            marker = " "
            farbe  = F_NORMAL

        zeile = f"  {marker} {name:<18} [{balken}]  {punkte:>2}"
        console.print(1, y, zeile, fg=farbe)
        y += 1

    # Beschreibung der gewaehlten Eigenschaft
    key_sel = EIGENSCHAFTEN_REIHENFOLGE[auswahl]
    beschreibung = _EIGENSCHAFT_BESCHREIBUNG.get(key_sel, "")
    console.print(2, y + 1, beschreibung[: w - 4], fg=F_BESCHREIBUNG)

    # Footer
    footer_enter = "[ENTER] bestätigen" if verbleibend == 0 else "[ENTER] — erst alle Punkte vergeben"
    farbe_enter  = F_FOOTER if verbleibend == 0 else F_FOOTER_GRAU
    footer_nav   = "[↑↓] wählen   [←→] Punkte vergeben / zurücknehmen"
    console.print(2, h - 3, footer_nav[:  w - 4], fg=F_FOOTER)
    console.print(2, h - 2, footer_enter[: w - 4], fg=farbe_enter)


# ---------------------------------------------------------------------------
# Eigenschaftspunkt-Auswahl-Overlay (beim Benutzen eines Items)
# ---------------------------------------------------------------------------

def zeichne_eigenschaft_auswahl(console, spieler, auswahl_index):
    """Zeichnet ein kleines Overlay zum Vergeben eines Eigenschaftspunkts per Item.

    spieler      -- Spieler-Objekt (fuer aktuelle Punktzahlen)
    auswahl_index -- int: Index der markierten Eigenschaft (0–5)
    """
    w = console.width
    h = console.height

    # Box in der Mitte: 44 breit, 12 hoch
    box_b = 44
    box_h = 12
    bx = (w - box_b) // 2
    by = (h - box_h) // 2

    # Hintergrund der Box
    console.draw_rect(bx, by, box_b, box_h, 32, bg=(20, 20, 40))
    _rahmen_box(console, bx, by, box_b, box_h)

    # Titel
    console.print(bx + box_b // 2, by + 1, "Eigenschaftspunkt vergeben",
                  fg=F_TITEL, alignment=tcod.CENTER)

    # Eigenschaften
    y = by + 3
    for i, key in enumerate(EIGENSCHAFTEN_REIHENFOLGE):
        punkte = spieler.eigenschaften.get(key, 0)
        name   = _EIGENSCHAFT_ANZEIGE[key]

        if i == auswahl_index:
            console.draw_rect(bx + 1, y, box_b - 2, 1, 32, bg=BG_AUSGEWAEHLT)
            marker = "\u25ba"
            farbe  = F_AUSGEWAEHLT
        else:
            marker = " "
            farbe  = F_NORMAL

        zeile = f" {marker} {name:<18} {punkte:>2}"
        console.print(bx + 1, y, zeile, fg=farbe)
        y += 1

    # Footer
    footer = "[↑↓] wählen   [ENTER] vergeben   [ESC] abbrechen"
    console.print(bx + 2, by + box_h - 2, footer[: box_b - 4], fg=F_FOOTER)


# ---------------------------------------------------------------------------
# Zeichenhilfen
# ---------------------------------------------------------------------------

def _rahmen(console, w, h):
    """Doppelter Rahmen ueber den ganzen Bildschirm."""
    console.print(0,     0,     "\u2554", fg=(100, 100, 180))
    console.print(w - 1, 0,     "\u2557", fg=(100, 100, 180))
    console.print(0,     h - 1, "\u255a", fg=(100, 100, 180))
    console.print(w - 1, h - 1, "\u255d", fg=(100, 100, 180))
    for i in range(1, w - 1):
        console.print(i, 0,     "\u2550", fg=(100, 100, 180))
        console.print(i, h - 1, "\u2550", fg=(100, 100, 180))
    for j in range(1, h - 1):
        console.print(0,     j, "\u2551", fg=(100, 100, 180))
        console.print(w - 1, j, "\u2551", fg=(100, 100, 180))


def _rahmen_box(console, x, y, w, h):
    """Einfacher Rahmen fuer ein kleines Overlay-Fenster."""
    console.print(x,         y,         "\u250c", fg=(100, 100, 180))
    console.print(x + w - 1, y,         "\u2510", fg=(100, 100, 180))
    console.print(x,         y + h - 1, "\u2514", fg=(100, 100, 180))
    console.print(x + w - 1, y + h - 1, "\u2518", fg=(100, 100, 180))
    for i in range(1, w - 1):
        console.print(x + i, y,         "\u2500", fg=(100, 100, 180))
        console.print(x + i, y + h - 1, "\u2500", fg=(100, 100, 180))
    for j in range(1, h - 1):
        console.print(x,         y + j, "\u2502", fg=(100, 100, 180))
        console.print(x + w - 1, y + j, "\u2502", fg=(100, 100, 180))
