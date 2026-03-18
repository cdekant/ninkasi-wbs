import json
import random
import tcod

import src.systems.skills as skills_system
import src.systems.menus as menus_system
from src.entities.player import Spieler
from src.entities.gegner import typen_laden, Gegner
from src.systems.kampf import KampfZustand, runde_ausfuehren
from src.systems.speichern import tod_reset, STANDARD_AKTUELL
from src.ui.menu_anzeige import zeichne_menue
from src.map.bsp import generiere_karte
from src.systems import sichtfeld
from src.systems import ki


# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

KAMPF_PANEL_HOEHE = 9   # Zeilen fuer das Kampf-Panel am unteren Rand


# ---------------------------------------------------------------------------
# Spielzustand
# ---------------------------------------------------------------------------

alle_skills = skills_system.lade_skills()
alle_gegner_typen = typen_laden()
spieler = Spieler()

# Spielmodus: "hub"   = Erkundung (Menues verfuegbar)
#             "kampf" = Kampf laeuft (nur Kampf-Eingabe aktiv)
modus = "hub"

# Menue-Zustand
aktives_menue = None
menue_auswahl = 0
status_meldung = ""

# Kampf-Zustand
aktiver_kampf = None          # KampfZustand oder None
aktiver_kampf_eintrag = None  # Dict-Referenz in gegner_auf_karte

# Level-Daten
with open("data/levels.json", encoding="utf-8") as f:
    alle_level = json.load(f)

KARTE = []
spieler_x, spieler_y = 1, 1
gegner_auf_karte = []   # [{"gegner": Gegner-Instanz, "x": int, "y": int}]

# Sichtfeld
TRANSPARENZ = None   # bool-Array: True = durchsichtig (Boden)
FOV         = None   # bool-Array: True = gerade sichtbar
ERKUNDET    = None   # bool-Array: True = schon einmal gesehen


# ---------------------------------------------------------------------------
# Level initialisieren und Gegner spawnen
# ---------------------------------------------------------------------------

def _initialisiere_level():
    """Generiert die Karte, setzt Spielerposition und spawnt Gegner.
    Wird beim Start und nach dem Tod aufgerufen.
    """
    global KARTE, spieler_x, spieler_y, gegner_auf_karte
    global TRANSPARENZ, FOV, ERKUNDET

    KARTE = generiere_karte(alle_level["gaerkeller"], breite=100, hoehe=55)

    # Spieler auf die erste freie Bodenkachel setzen
    spieler_x, spieler_y = 1, 1
    for y, zeile in enumerate(KARTE):
        for x, kachel in enumerate(zeile):
            if kachel == ".":
                spieler_x, spieler_y = x, y
                break
        else:
            continue
        break

    _spawne_gegner(3)

    # Sichtfeld initialisieren
    TRANSPARENZ = sichtfeld.baue_transparenz(KARTE)
    ERKUNDET    = sichtfeld.neues_erkundet(KARTE)
    FOV         = sichtfeld.berechne_fov(TRANSPARENZ, spieler_x, spieler_y)
    sichtfeld.aktualisiere_erkundet(ERKUNDET, FOV)


def _spawne_gegner(anzahl):
    """Waehlt Gegner gewichtet aus dem gegner_pool und platziert sie zufaellig."""
    global gegner_auf_karte
    gegner_auf_karte = []

    pool = alle_level["gaerkeller"].get("gegner_pool", [])
    if not pool:
        return

    freie = [
        (x, y)
        for y, zeile in enumerate(KARTE)
        for x, kachel in enumerate(zeile)
        if kachel == "." and (x, y) != (spieler_x, spieler_y)
    ]

    ids      = [e["id"]      for e in pool]
    weights  = [e["gewicht"] for e in pool]
    staerken = {e["id"]: e["staerke"] for e in pool}

    spawned = 0
    versuche = 0
    while spawned < anzahl and freie and versuche < anzahl * 20:
        versuche += 1
        typ_id = random.choices(ids, weights=weights, k=1)[0]
        g = Gegner.aus_typ(typ_id, alle_gegner_typen, staerken[typ_id])
        if g is None:   # Schwarm-Typ — noch nicht implementiert
            continue
        pos = random.choice(freie)
        freie.remove(pos)
        gegner_auf_karte.append({"gegner": g, "x": pos[0], "y": pos[1]})
        spawned += 1


_initialisiere_level()


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def ist_betretbar(x, y):
    if y < 0 or y >= len(KARTE):
        return False
    if x < 0 or x >= len(KARTE[y]):
        return False
    return KARTE[y][x] == "."


def _balken(aktuell, maximum, breite=16):
    """ASCII-Fortschrittsbalken: '######..........'"""
    pct = aktuell / maximum if maximum > 0 else 0
    voll = round(pct * breite)
    return "#" * voll + "." * (breite - voll)


# ---------------------------------------------------------------------------
# Zeichnen
# ---------------------------------------------------------------------------

def zeichne(console):
    console.clear()

    # Karte mit FOV / Fog of War
    for y, zeile in enumerate(KARTE):
        for x, zeichen in enumerate(zeile):
            if FOV[y, x]:
                # Gerade sichtbar — volle Helligkeit
                if zeichen == "#":
                    console.print(x, y, zeichen, fg=(160, 160, 160))
                else:
                    console.print(x, y, zeichen, fg=(90, 90, 90))
            elif ERKUNDET[y, x]:
                # Schon gesehen, aber gerade nicht im Blickfeld — abgedunkelt
                if zeichen == "#":
                    console.print(x, y, zeichen, fg=(50, 50, 50))
                else:
                    console.print(x, y, zeichen, fg=(20, 20, 20))
            # Nie gesehen: nicht zeichnen (bleibt schwarz)

    # Gegner — nur sichtbar wenn im FOV
    for eintrag in gegner_auf_karte:
        if eintrag["gegner"].lebt and FOV[eintrag["y"], eintrag["x"]]:
            console.print(eintrag["x"], eintrag["y"],
                          eintrag["gegner"].symbol, fg=(200, 80, 80))

    # Spieler
    console.print(spieler_x, spieler_y, "@", fg=(255, 215, 0))

    # HUD (nur ausserhalb des Kampfes)
    if modus != "kampf":
        hud = (f"EP: {spieler.ep_verfuegbar}  "
               f"LP: {spieler.lp}/{spieler.lp_max}  "
               f"PP: {spieler.pp}/{spieler.pp_max}")
        console.print(1, console.height - 1, hud, fg=(100, 200, 120))
        console.print(console.width - 20, console.height - 1,
                      "[TAB] Menue  [Q] Beenden", fg=(80, 80, 80))

    # Kampf-Panel
    if modus == "kampf" and aktiver_kampf:
        _zeichne_kampf_panel(console)

    # Menue-Overlay (uebermalt alles andere)
    if aktives_menue:
        verfuegbar = menus_system.verfuegbare_menues(modus)
        zeichne_menue(console, aktives_menue, spieler, alle_skills,
                      menue_auswahl, status_meldung, verfuegbar)


def _zeichne_kampf_panel(console):
    """Kampf-Panel am unteren Bildschirmrand."""
    zst = aktiver_kampf
    w  = console.width
    h  = console.height
    y0 = h - KAMPF_PANEL_HOEHE

    # Hintergrund
    for y in range(y0, h):
        for x in range(w):
            console.print(x, y, " ", bg=(15, 8, 8))

    # Trennlinie
    console.print(0, y0, "-" * w, fg=(80, 40, 10))

    # --- Gegner (linke Haelfte) ---
    g    = zst.gegner
    mitte = w // 2
    console.print(2, y0 + 1, f"{g.symbol} {g.name}", fg=(220, 80, 80))
    console.print(2, y0 + 2,
                  f"HP [{_balken(g.hp, g.hp_max)}] {g.hp}/{g.hp_max}",
                  fg=(180, 60, 60))

    # --- Spieler (rechte Haelfte) ---
    console.print(mitte, y0 + 1,
                  f"@ {zst.spieler.name}", fg=(255, 215, 0))
    console.print(mitte, y0 + 2,
                  f"LP [{_balken(zst.spieler.lp, zst.spieler.lp_max)}] "
                  f"{zst.spieler.lp}/{zst.spieler.lp_max}",
                  fg=(100, 200, 120))

    # --- Kampf-Log (letzte 4 Eintraege) ---
    log = zst.log[-4:] if zst.log else ["Kampf beginnt!"]
    for i, zeile in enumerate(log):
        console.print(2, y0 + 3 + i, zeile[:w - 4], fg=(155, 155, 155))

    # --- Steuerungshinweis / Ergebnis ---
    if not zst.beendet:
        console.print(2, y0 + KAMPF_PANEL_HOEHE - 1,
                      "[LEERTASTE] Angreifen", fg=(80, 80, 80))
    elif zst.ergebnis == "sieg":
        console.print(2, y0 + KAMPF_PANEL_HOEHE - 1,
                      f"SIEG!  [LEERTASTE] Weiter", fg=(100, 220, 100))
    else:
        console.print(2, y0 + KAMPF_PANEL_HOEHE - 1,
                      "NIEDERLAGE  [LEERTASTE] Neu starten", fg=(220, 80, 80))


# ---------------------------------------------------------------------------
# Spielschleife
# ---------------------------------------------------------------------------

def starte(console, context):
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
    global aktiver_kampf, aktiver_kampf_eintrag, modus

    sym   = event.sym
    shift = bool(event.mod & tcod.event.KMOD_SHIFT)

    # -----------------------------------------------------------------------
    # Kampf laeuft — nur Kampf-Eingabe
    # -----------------------------------------------------------------------
    if modus == "kampf":
        if sym in (tcod.event.KeySym.SPACE, tcod.event.KeySym.RETURN):
            _kampf_aktion()
        return

    # -----------------------------------------------------------------------
    # Menue offen
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

        return

    # -----------------------------------------------------------------------
    # Erkundung
    # -----------------------------------------------------------------------

    if sym == tcod.event.KeySym.TAB:
        verfuegbar = menus_system.verfuegbare_menues(modus)
        if verfuegbar:
            aktives_menue = verfuegbar[0]["id"]
            menue_auswahl = 0
            status_meldung = ""

    elif sym in (tcod.event.KeySym.UP,    tcod.event.KeySym.w): _bewege( 0, -1)
    elif sym in (tcod.event.KeySym.DOWN,  tcod.event.KeySym.s): _bewege( 0,  1)
    elif sym in (tcod.event.KeySym.LEFT,  tcod.event.KeySym.a): _bewege(-1,  0)
    elif sym in (tcod.event.KeySym.RIGHT, tcod.event.KeySym.d): _bewege( 1,  0)
    elif sym == tcod.event.KeySym.q:
        raise SystemExit()


def _bewege(dx, dy):
    global spieler_x, spieler_y, aktiver_kampf, aktiver_kampf_eintrag, modus, FOV

    nx, ny = spieler_x + dx, spieler_y + dy

    # Gegner auf Zielfeld? -> Kampf starten
    for eintrag in gegner_auf_karte:
        if eintrag["x"] == nx and eintrag["y"] == ny and eintrag["gegner"].lebt:
            aktiver_kampf = KampfZustand(spieler, eintrag["gegner"])
            aktiver_kampf_eintrag = eintrag
            modus = "kampf"
            return

    # Freies Feld -> bewegen
    if ist_betretbar(nx, ny):
        spieler_x, spieler_y = nx, ny
        spieler.runden += 1
        spieler.ep_hinzufuegen(1)
        FOV = sichtfeld.berechne_fov(TRANSPARENZ, spieler_x, spieler_y)
        sichtfeld.aktualisiere_erkundet(ERKUNDET, FOV)
        # Gegner reagieren auf den Spielerzug
        angreifer = ki.ki_tick(gegner_auf_karte, spieler_x, spieler_y, KARTE)
        if angreifer:
            aktiver_kampf = KampfZustand(spieler, angreifer["gegner"])
            aktiver_kampf_eintrag = angreifer
            modus = "kampf"


def _kampf_aktion():
    """LEERTASTE / ENTER im Kampf: naechste Runde oder Ergebnis bestaetigen."""
    global modus, aktiver_kampf, aktiver_kampf_eintrag

    if not aktiver_kampf.beendet:
        runde_ausfuehren(aktiver_kampf)
        return

    # Kampf beendet — Ergebnis verarbeiten
    if aktiver_kampf.ergebnis == "sieg":
        if aktiver_kampf_eintrag in gegner_auf_karte:
            gegner_auf_karte.remove(aktiver_kampf_eintrag)

    elif aktiver_kampf.ergebnis == "niederlage":
        tod_reset(spieler, {"tod_zaehler": 0})
        _initialisiere_level()

    aktiver_kampf = None
    aktiver_kampf_eintrag = None
    modus = "hub"
