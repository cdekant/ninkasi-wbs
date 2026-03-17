import tcod

import src.systems.skills as skills_system
import src.systems.menus as menus_system
from src.entities.player import Spieler
from src.ui.menu_anzeige import zeichne_menue

# ---------------------------------------------------------------------------
# Initialisierung
# ---------------------------------------------------------------------------

alle_skills = skills_system.lade_skills()
spieler = Spieler()

# Spielmodus: "hub" = zwischen Runs (Menues verfuegbar)
#             "run" = aktives Level (Hub-Menues gesperrt)
modus = "hub"

# Menue-Zustand
aktives_menue = None    # None = kein Menue offen; sonst Menue-ID-String
menue_auswahl = 0       # Index in auswaehlbare Skill-Liste
status_meldung = ""     # Feedback nach Kauf ("!..." = Fehler)

# ---------------------------------------------------------------------------
# Testkarte
# ---------------------------------------------------------------------------

KARTE = [
    "##################################################",
    "#................................................#",
    "#................................................#",
    "#....#######.....................................#",
    "#....#.......#...................................#",
    "#....#.......#...................................#",
    "#....#########...................................#",
    "#................................................#",
    "#................................................#",
    "##################################################",
]

spieler_x = 2
spieler_y = 2


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def ist_betretbar(x, y):
    if y < 0 or y >= len(KARTE):
        return False
    if x < 0 or x >= len(KARTE[y]):
        return False
    return KARTE[y][x] == "."


# ---------------------------------------------------------------------------
# Zeichnen
# ---------------------------------------------------------------------------

def zeichne(console):
    console.clear()

    # Karte
    for y, zeile in enumerate(KARTE):
        for x, zeichen in enumerate(zeile):
            if zeichen == "#":
                console.print(x, y, zeichen, fg=(120, 120, 120))
            else:
                console.print(x, y, zeichen, fg=(60, 60, 60))

    # Spieler
    console.print(spieler_x, spieler_y, "@", fg=(255, 215, 0))

    # HUD: EP und Steuerungshinweis
    ep_text = f"EP: {spieler.ep_verfuegbar}"
    console.print(1, console.height - 1, ep_text, fg=(100, 200, 120))
    if modus == "hub":
        console.print(console.width - 20, console.height - 1,
                      "[TAB] Menue oeffnen", fg=(80, 80, 80))

    # Menue-Overlay (wenn aktiv, uebermalt Karte + HUD)
    if aktives_menue:
        verfuegbar = menus_system.verfuegbare_menues(modus)
        zeichne_menue(console, aktives_menue, spieler, alle_skills,
                      menue_auswahl, status_meldung, verfuegbar)


# ---------------------------------------------------------------------------
# Spielschleife
# ---------------------------------------------------------------------------

def starte(console, context):
    global spieler_x, spieler_y, aktives_menue, menue_auswahl, status_meldung

    while True:
        zeichne(console)
        context.present(console)

        for event in tcod.event.wait():

            if isinstance(event, tcod.event.Quit):
                raise SystemExit()

            if isinstance(event, tcod.event.KeyDown):
                _handle_key(event)


def _handle_key(event):
    global spieler_x, spieler_y, aktives_menue, menue_auswahl, status_meldung

    sym   = event.sym
    shift = bool(event.mod & tcod.event.KMOD_SHIFT)

    # -----------------------------------------------------------------------
    # Menue ist offen
    # -----------------------------------------------------------------------
    if aktives_menue:

        if sym == tcod.event.KeySym.ESCAPE:
            aktives_menue = None
            status_meldung = ""

        elif sym == tcod.event.KeySym.TAB:
            if shift:
                aktives_menue = menus_system.vorheriges_menue(aktives_menue, modus)
            else:
                aktives_menue = menus_system.naechstes_menue(aktives_menue, modus)
            menue_auswahl = 0
            status_meldung = ""

        elif sym in (tcod.event.KeySym.UP, tcod.event.KeySym.w):
            menue_auswahl = max(0, menue_auswahl - 1)
            status_meldung = ""

        elif sym in (tcod.event.KeySym.DOWN, tcod.event.KeySym.s):
            n = menus_system.anzahl_auswaehlbar(alle_skills)
            menue_auswahl = min(n - 1, menue_auswahl + 1)
            status_meldung = ""

        elif sym == tcod.event.KeySym.RETURN:
            if aktives_menue == "skills":
                sid = menus_system.ausgewaehlte_skill_id(alle_skills, menue_auswahl)
                if sid:
                    ok, msg = spieler.skill_lernen(sid, alle_skills)
                    status_meldung = msg if ok else f"!{msg}"

        return  # Tasten im Menue bewegen den Spieler nicht

    # -----------------------------------------------------------------------
    # Kein Menue offen — normale Spieleingabe
    # -----------------------------------------------------------------------

    if sym == tcod.event.KeySym.TAB:
        verfuegbar = menus_system.verfuegbare_menues(modus)
        if verfuegbar:
            aktives_menue = verfuegbar[0]["id"]
            menue_auswahl = 0
            status_meldung = ""

    elif sym in (tcod.event.KeySym.UP, tcod.event.KeySym.w):
        _bewege(0, -1)
    elif sym in (tcod.event.KeySym.DOWN, tcod.event.KeySym.s):
        _bewege(0, 1)
    elif sym in (tcod.event.KeySym.LEFT, tcod.event.KeySym.a):
        _bewege(-1, 0)
    elif sym in (tcod.event.KeySym.RIGHT, tcod.event.KeySym.d):
        _bewege(1, 0)
    elif sym == tcod.event.KeySym.q:
        raise SystemExit()


def _bewege(dx, dy):
    global spieler_x, spieler_y
    nx, ny = spieler_x + dx, spieler_y + dy
    if ist_betretbar(nx, ny):
        spieler_x, spieler_y = nx, ny
        spieler.runden += 1
        spieler.ep_hinzufuegen(spieler.ep_pro_runde(alle_skills))
