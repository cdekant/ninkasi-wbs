import json
import random
import time
import tcod
import config

try:
    with open("VERSION", encoding="utf-8") as _vf:
        _VERSION = "v" + _vf.read().split()[0]
except Exception:
    _VERSION = "v?"

try:
    from PIL import Image as _PILImage
    _img = _PILImage.open("assets/ninkasi_brutality_120x144.png").convert("RGBA")
    _TITEL_PIXEL = list(_img.getdata())   # [(r,g,b,a), ...] flach, 120×144
    _TITEL_W, _TITEL_H = _img.size       # 120, 144
except Exception:
    _TITEL_PIXEL = None
    _TITEL_W = _TITEL_H = 0

import src.tiles as tiles
import src.systems.skills as skills_system
import src.systems.menus as menus_system
import src.systems.inventar as inventar_system
from src.entities.player import Spieler
from src.entities.gegner import typen_laden, Gegner
from src.entities.item import typen_laden as items_laden
from src.systems.kampf import KampfZustand, runde_ausfuehren
from src.systems.speichern import tod_reset, STANDARD_AKTUELL, speichern, laden
from src.ui.menu_anzeige import zeichne_menue
from src.map.karte import generiere_karte
from src.map.hub import generiere_hub as _generiere_hub
from src.systems import sichtfeld
from src.systems import ki


# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

_nachrichtenlog  = []   # letzte Meldungen fuer den Log-Bereich unten
_karte_boden_tile = None  # optionales Custom-Tile fuer Boden-Rendering (None = ".")


def _log(text):
    """Fuegt einen Eintrag zum Nachrichtenlog hinzu (max. 40 Eintraege)."""
    _nachrichtenlog.append(text)
    if len(_nachrichtenlog) > 40:
        _nachrichtenlog.pop(0)


# ---------------------------------------------------------------------------
# Startbildschirm — ASCII-Art Buchstaben (5 Zeilen hoch)
# ---------------------------------------------------------------------------

_GLYPH = {
    "B": ["###.", "#..#", "###.", "#..#", "###."],
    "A": [".##.", "#..#", "####", "#..#", "#..#"],
    "T": ["#####", "..#..", "..#..", "..#..", "..#.."],
    "L": ["#...", "#...", "#...", "#...", "####"],
    "E": ["####", "#...", "###.", "#...", "####"],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"],
    "K": ["#..#", "#.#.", "##..", "#.#.", "#..#"],
    "S": [".###", "#...", ".##.", "...#", "###."],
}

_START_ZITATE = [
    '"Hopfen und Malz, Gott erhalts."',
    '"Wen der Hopfen einmal kratzt, den laesst er nicht mehr los."',
    '"Der Prohibitus wird fallen und wir trinken auf seinen Ruin."',
    '"Die Hefe tut was sie will. Die Goettin lenkt sie nur."',
    '"Das Leben ist zu kurz fuer schlechtes Bier."',
    '"Der Tod ist nur ein Neustart ohne Stammwuerze."',
    '"Nieder mit dem Daemon der Abstinenz!"',
    '"Bier ist der Beweis, dass die Goettin uns liebt."',
    '"Durst wird durch Bier erst schoen."',
]

_TOD_ZITATE = [
    "Das Bier raeche sich. Du nicht.",
    "Selbst Goettinnen koennen sterben. Manche sogar mehrfach.",
    "Tod ist nur eine Pause zwischen zwei Gaerungen.",
    "Der Prohibitus lacht. Noch.",
    "Niemand hat gesagt, Brauen sei einfach.",
    "Hefe 1, Ninkasi 0.",
    "Du riechst nach Niederlage. Und ein bisschen nach Schimmel.",
    "Komm wieder wenn du kein Wasser mehr trinkst.",
    "Du musst auhoeren weniger zu trinken!",
]

_TOTENKOPF = [
    r"   .---.   ",
    r"  ( o o )  ",
    r"   ) ^ (   ",
    r"  '-----'  ",
    r"  ||| |||  ",
]


# ---------------------------------------------------------------------------
# Spielzustand
# ---------------------------------------------------------------------------

alle_skills = skills_system.lade_skills()
alle_gegner_typen = typen_laden()
alle_items = items_laden()
spieler = Spieler()

# Spielmodus: "hub"   = Erkundung (Menues verfuegbar)
#             "kampf" = Kampf laeuft (nur Kampf-Eingabe aktiv)
#             "tod"   = Tod-Screen (nur Auferstehen moeglich)
modus = "hub"

# Ort: "pilsstube" = Hub | "dungeon" = laufender Run
ort = "pilsstube"

# Menue-Zustand
aktives_menue = None
menue_auswahl = 0
status_meldung = ""

# Kampf-Zustand
aktiver_kampf = None          # KampfZustand oder None
aktiver_kampf_eintrag = None  # Dict-Referenz in gegner_auf_karte
_letzter_bewegungszeitpunkt = 0.0   # fuer Haltetasten-Rate-Limit

# Spielstand-Dict (level_index, tod_zaehler, ...)
aktuell = dict(STANDARD_AKTUELL)

# Tod-Info fuer den Tod-Screen
tod_gegner_name = ""
tod_zitat       = ""

# Level-Daten
with open("data/levels.json", encoding="utf-8") as f:
    alle_level = json.load(f)

KARTE = []
spieler_x, spieler_y = 1, 1
gegner_auf_karte = []   # [{"gegner": Gegner-Instanz, "x": int, "y": int}]

# Sichtfeld (Dungeon)
TRANSPARENZ = None
FOV         = None
ERKUNDET    = None

# Dungeon-Ausgang (Rueckkehr zum Hub)
DUNGEON_AUSGANG_X = 0
DUNGEON_AUSGANG_Y = 0

# Hub-Zustand
HUB_KARTE      = []
HUB_OBJEKTE    = []
HUB_START_X    = 0
HUB_START_Y    = 0
hub_spieler_x  = 0
hub_spieler_y  = 0
HUB_TRANSPARENZ = None
HUB_FOV         = None
HUB_ERKUNDET    = None


# ---------------------------------------------------------------------------
# Level initialisieren und Gegner spawnen
# ---------------------------------------------------------------------------

def _initialisiere_level():
    """Generiert die Karte, setzt Spielerposition und spawnt Gegner.
    Wird beim Dungeon-Eintritt, Zonen-Wechsel und nach dem Tod aufgerufen.
    """
    global KARTE, spieler_x, spieler_y, gegner_auf_karte
    global TRANSPARENZ, FOV, ERKUNDET
    global DUNGEON_AUSGANG_X, DUNGEON_AUSGANG_Y
    global _karte_boden_tile

    level_name = aktuell.get("level_name", "pflanzenzuechtung")
    grammatik  = alle_level[level_name]
    KARTE = generiere_karte(grammatik, breite=config.BREITE, hoehe=config.KARTE_HOEHE)
    roh = grammatik.get("boden_tile")
    _karte_boden_tile = tiles.TILE_NAMEN.get(roh) if roh else None

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

    # Ausgang auf dem Bodentile am weitesten vom Spieler
    max_dist = -1
    DUNGEON_AUSGANG_X, DUNGEON_AUSGANG_Y = spieler_x, spieler_y
    for y, zeile in enumerate(KARTE):
        for x, kachel in enumerate(zeile):
            if kachel == ".":
                dist = abs(x - spieler_x) + abs(y - spieler_y)
                if dist > max_dist:
                    max_dist = dist
                    DUNGEON_AUSGANG_X, DUNGEON_AUSGANG_Y = x, y

    zone_idx = aktuell.get("zone_index", 0)
    _spawne_gegner(12 + zone_idx * 2)

    # Bodenloot zuruecksetzen (neue Karte, neues Loot)
    aktuell["bodenloot"] = []

    # Sichtfeld initialisieren
    TRANSPARENZ = sichtfeld.baue_transparenz(KARTE)
    ERKUNDET    = sichtfeld.neues_erkundet(KARTE)
    FOV         = sichtfeld.berechne_fov(TRANSPARENZ, spieler_x, spieler_y)
    sichtfeld.aktualisiere_erkundet(ERKUNDET, FOV)


def _spawne_gegner(anzahl):
    """Waehlt Gegner gewichtet aus dem gegner_pool und platziert sie zufaellig.

    Die Staerke wird pro Zone um 5 % erhoeht (zone_index * 0.05).
    """
    global gegner_auf_karte
    gegner_auf_karte = []

    level_name = aktuell.get("level_name", "pflanzenzuechtung")
    pool = alle_level[level_name].get("gegner_pool", [])
    if not pool:
        return

    zone_idx     = aktuell.get("zone_index", 0)
    staerke_mult = 1.0 + 0.05 * zone_idx

    freie = [
        (x, y)
        for y, zeile in enumerate(KARTE)
        for x, kachel in enumerate(zeile)
        if kachel == "." and (x, y) != (spieler_x, spieler_y)
    ]

    ids      = [e["id"]      for e in pool]
    weights  = [e["gewicht"] for e in pool]
    staerken = {e["id"]: min(1.0, e["staerke"] * staerke_mult) for e in pool}

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


def _initialisiere_hub():
    """Baut die Hub-Karte einmalig beim Spielstart auf."""
    global HUB_KARTE, HUB_OBJEKTE, HUB_START_X, HUB_START_Y
    global hub_spieler_x, hub_spieler_y
    global HUB_TRANSPARENZ, HUB_FOV, HUB_ERKUNDET

    HUB_KARTE, sx, sy, ausgang = _generiere_hub(config.BREITE, config.KARTE_HOEHE)
    HUB_START_X   = sx
    HUB_START_Y   = sy
    hub_spieler_x = sx
    hub_spieler_y = sy
    HUB_OBJEKTE   = [ausgang]

    HUB_TRANSPARENZ = sichtfeld.baue_transparenz(HUB_KARTE)
    HUB_ERKUNDET    = sichtfeld.neues_erkundet(HUB_KARTE)
    HUB_FOV         = sichtfeld.berechne_fov(HUB_TRANSPARENZ, hub_spieler_x, hub_spieler_y)
    sichtfeld.aktualisiere_erkundet(HUB_ERKUNDET, HUB_FOV)


_initialisiere_hub()


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _ist_wand(zeichen):
    """True fuer '#' und alle wandartigen Custom-Tiles (Fenster etc.)."""
    return zeichen == "#" or zeichen in tiles.WAND_TILES


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
    KY = config.KARTE_Y0

    # Karte mit FOV / Fog of War
    for y, zeile in enumerate(KARTE):
        for x, zeichen in enumerate(zeile):
            cy = y + KY
            # "." ggf. durch Level-spezifisches Boden-Tile ersetzen
            anzeige = _karte_boden_tile if (zeichen == "." and _karte_boden_tile) else zeichen
            if FOV[y, x]:
                if zeichen == tiles.WAND_GITTER:
                    console.print(x, cy, anzeige, fg=(140, 210, 140))
                elif zeichen == tiles.OBJ_VEG_GRAS:
                    console.print(x, cy, anzeige, fg=(255, 255, 255))
                elif _ist_wand(zeichen):
                    console.print(x, cy, anzeige, fg=(200, 200, 200))
                elif anzeige == tiles.BODEN_FLIESSE:
                    # jede 7. Fliese leicht bläulich (deterministisch per Position)
                    if (x * 3 + y * 7) % 7 == 0:
                        console.print(x, cy, anzeige, fg=(160, 180, 220))
                    else:
                        console.print(x, cy, anzeige, fg=(200, 200, 200))
                else:
                    console.print(x, cy, anzeige, fg=(90, 90, 90))
            elif ERKUNDET[y, x]:
                if zeichen == tiles.WAND_GITTER:
                    console.print(x, cy, anzeige, fg=(45, 70, 45))
                elif zeichen == tiles.OBJ_VEG_GRAS:
                    console.print(x, cy, anzeige, fg=(60, 60, 60))
                elif _ist_wand(zeichen):
                    console.print(x, cy, anzeige, fg=(60, 60, 60))
                elif anzeige == tiles.BODEN_FLIESSE:
                    console.print(x, cy, anzeige, fg=(40, 45, 60))
                else:
                    console.print(x, cy, anzeige, fg=(20, 20, 20))
            # Nie gesehen: nicht zeichnen (bleibt schwarz)

    # Dungeon-Ausgang
    if FOV[DUNGEON_AUSGANG_Y, DUNGEON_AUSGANG_X]:
        console.print(DUNGEON_AUSGANG_X, DUNGEON_AUSGANG_Y + KY, "<", fg=(80, 200, 255))

    # Bodenloot — nur sichtbar wenn im FOV
    for loot in aktuell.get("bodenloot", []):
        if FOV[loot["y"], loot["x"]]:
            item_def = alle_items.get(loot["id"])
            if item_def:
                console.print(loot["x"], loot["y"] + KY,
                               item_def["symbol"], fg=tuple(item_def["farbe"]))

    # Gegner — nur sichtbar wenn im FOV
    for eintrag in gegner_auf_karte:
        if eintrag["gegner"].lebt and FOV[eintrag["y"], eintrag["x"]]:
            console.print(eintrag["x"], eintrag["y"] + KY,
                          eintrag["gegner"].symbol, fg=(200, 80, 80))

    # Spieler
    console.print(spieler_x, spieler_y + KY, tiles.HUB_NINKASI, fg=(255, 215, 0))

    # Statuszeile (Zeilen 0-1)
    _zeichne_statuszeile(console)

    # Schwebendes Kampffenster
    if modus == "kampf" and aktiver_kampf:
        _zeichne_kampf_panel(console)

    # Nachrichtenlog + Shortcuts
    shortcut = "" if modus == "kampf" else "[TAB] Menue  [<] Hub  [Q] Beenden"
    _zeichne_log(console, shortcut)

    # Menue-Overlay (uebermalt alles andere)
    if aktives_menue:
        verfuegbar = menus_system.verfuegbare_menues(ort)
        zeichne_menue(console, aktives_menue, spieler, alle_skills, alle_items,
                      menue_auswahl, status_meldung, verfuegbar)


def _zeichne_statuszeile(console):
    """Statuszeile: Zeile 0 (LP/PP/MP-Balken) + Zeile 1 (Zone/Kontext)."""
    w = console.width
    console.draw_rect(0, 0, w, 2, 32, bg=(10, 5, 20))

    # Zeile 0: drei Balken + EP rechts
    lp_b = _balken(spieler.lp,  spieler.lp_max,  14)
    pp_b = _balken(spieler.pp,  spieler.pp_max,  14)
    mp_b = _balken(spieler.mp,  spieler.mp_max,  14)
    console.print( 2, 0, f"LP [{lp_b}] {spieler.lp:>3}/{spieler.lp_max:<3}", fg=(100, 220, 100))
    console.print(40, 0, f"PP [{pp_b}] {spieler.pp:>3}/{spieler.pp_max:<3}", fg=(100, 150, 255))
    console.print(78, 0, f"MP [{mp_b}] {spieler.mp:>3}/{spieler.mp_max:<3}", fg=(200, 100, 255))
    ep_txt = f"EP: {spieler.ep_verfuegbar}"
    console.print(w - 2 - len(ep_txt), 0, ep_txt, fg=(100, 200, 120))

    # Zeile 1: Zone (spaeter: Statuseffekte)
    if ort == "dungeon":
        z  = aktuell.get("zone_index",   0) + 1
        zg = aktuell.get("zonen_gesamt", 1)
        console.print(2, 1, f"Zone {z}/{zg}", fg=(110, 110, 110))


def _zeichne_log(console, shortcut=""):
    """Nachrichtenlog (Zeilen 61-65) + Shortcut-Zeile (Zeile 66)."""
    w = console.width
    console.draw_rect(0, config.LOG_Y0, w, config.LOG_HOEHE + 1, 32, bg=(8, 4, 12))

    eintraege = _nachrichtenlog[-config.LOG_HOEHE:]
    for i, text in enumerate(eintraege):
        # Neueste Eintraege heller
        hell = 80 + i * (120 // max(1, config.LOG_HOEHE))
        console.print(2, config.LOG_Y0 + i, text[:w - 4], fg=(hell, hell, hell))

    if shortcut:
        console.print(w - 2 - len(shortcut), config.SHORTCUT_Y,
                      shortcut, fg=(65, 65, 65))


def _rahmen_kampf(console, x, y, w, h):
    """Einfacher Rahmen fuer das Kampffenster."""
    BG = (15, 8, 8)
    FG = (100, 40, 10)
    console.print(x,     y,     "\u250c", fg=FG, bg=BG)  # ┌
    console.print(x+w-1, y,     "\u2510", fg=FG, bg=BG)  # ┐
    console.print(x,     y+h-1, "\u2514", fg=FG, bg=BG)  # └
    console.print(x+w-1, y+h-1, "\u2518", fg=FG, bg=BG)  # ┘
    for i in range(1, w - 1):
        console.print(x+i, y,     "\u2500", fg=FG, bg=BG)  # ─
        console.print(x+i, y+h-1, "\u2500", fg=FG, bg=BG)
    for j in range(1, h - 1):
        console.print(x,     y+j, "\u2502", fg=FG, bg=BG)  # │
        console.print(x+w-1, y+j, "\u2502", fg=FG, bg=BG)


def _linie_kampf(console, x, y, w):
    """Horizontale Trennlinie innerhalb des Kampffensters."""
    BG = (15, 8, 8)
    FG = (80, 40, 10)
    console.print(x,     y, "\u251c", fg=FG, bg=BG)  # ├
    console.print(x+w-1, y, "\u2524", fg=FG, bg=BG)  # ┤
    for i in range(1, w - 1):
        console.print(x+i, y, "\u2500", fg=FG, bg=BG)  # ─


def _zeichne_kampf_panel(console):
    """Schwebendes Kampffenster (zentriert in der Karte)."""
    zst = aktiver_kampf
    fx  = config.KAMPF_FENSTER_X
    fy  = config.KAMPF_FENSTER_Y
    fw  = config.KAMPF_FENSTER_BREITE
    fh  = config.KAMPF_FENSTER_HOEHE
    inn = fw - 2   # nutzbare Innenbreite

    # Hintergrund + Rahmen
    console.draw_rect(fx, fy, fw, fh, 32, bg=(15, 8, 8))
    _rahmen_kampf(console, fx, fy, fw, fh)

    # --- Kopfzeile: Gegner links / Spieler rechts ---
    g     = zst.gegner
    mitte = fw // 2
    console.print(fx + 1, fy + 1, f"{g.symbol} {g.name}", fg=(220, 80, 80))
    console.print(fx + mitte, fy + 1, f"@ {zst.spieler.name}", fg=(255, 215, 0))

    # HP / LP Balken
    gp_bar = _balken(g.hp, g.hp_max, 12)
    sp_bar = _balken(zst.spieler.lp, zst.spieler.lp_max, 12)
    console.print(fx + 1, fy + 2,
                  f"HP [{gp_bar}] {g.hp}/{g.hp_max}", fg=(180, 60, 60))
    console.print(fx + mitte, fy + 2,
                  f"LP [{sp_bar}] {zst.spieler.lp}/{zst.spieler.lp_max}",
                  fg=(100, 200, 120))

    # Trennlinie nach Kopf
    _linie_kampf(console, fx, fy + 3, fw)

    # --- Kampf-Log (scrollend, aeltere Zeilen dunkler) ---
    log_zeilen = fh - 7   # Rahmen(2) + Kopf(2) + Trennl.(1) + Trennl.(1) + Hint(1)
    log = zst.log[-log_zeilen:] if zst.log else ["Kampf beginnt!"]
    for i, zeile in enumerate(log):
        hell = 80 + i * (120 // max(1, len(log)))
        console.print(fx + 1, fy + 4 + i, zeile[:inn], fg=(hell, hell, hell))

    # Trennlinie vor Steuerung
    _linie_kampf(console, fx, fy + fh - 3, fw)

    # --- Steuerungshinweis / Ergebnis ---
    if not zst.beendet:
        if aktives_menue:
            hint  = "[ESC/TAB] Schliessen  [W/S] Navigieren  [ENTER] Benutzen"
            farbe = (80, 80, 80)
        else:
            hint  = "[LEERTASTE] Angreifen  [TAB] Inventar"
            farbe = (80, 80, 80)
    elif zst.ergebnis == "sieg":
        hint  = "SIEG!  [LEERTASTE] Weiter"
        farbe = (100, 220, 100)
    else:
        hint  = "NIEDERLAGE  [LEERTASTE] Neu starten"
        farbe = (220, 80, 80)
    console.print(fx + 1, fy + fh - 2, hint[:inn], fg=farbe)


# ---------------------------------------------------------------------------
# Hub und Tod-Screen zeichnen
# ---------------------------------------------------------------------------

def _zeichne_hub(console):
    """Hub zeichnen."""
    console.clear()
    KY = config.KARTE_Y0

    # Karte mit FOV — warme Bodenfarbe (Holz/Stroh) statt Dungeon-Grau
    for y, zeile in enumerate(HUB_KARTE):
        for x, zeichen in enumerate(zeile):
            cy = y + KY
            if HUB_FOV[y, x]:
                fg = (200, 200, 200) if _ist_wand(zeichen) else (110, 80, 35)
                console.print(x, cy, zeichen, fg=fg)
            elif HUB_ERKUNDET[y, x]:
                fg = (60, 60, 60) if _ist_wand(zeichen) else (40, 28, 10)
                console.print(x, cy, zeichen, fg=fg)

    # Hub-Objekte (Braukessel/Ausgang etc.)
    for obj in HUB_OBJEKTE:
        if HUB_FOV[obj["y"], obj["x"]]:
            console.print(obj["x"], obj["y"] + KY, obj["symbol"], fg=obj["farbe"])

    # Spieler
    console.print(hub_spieler_x, hub_spieler_y + KY, tiles.HUB_NINKASI, fg=(255, 215, 0))

    # Statuszeile + Log
    _zeichne_statuszeile(console)
    _zeichne_log(console, "[TAB] Menue  [Kessel] Dungeon  [Q] Beenden")

    # Menue-Overlay
    if aktives_menue:
        verfuegbar = menus_system.verfuegbare_menues(ort)
        zeichne_menue(console, aktives_menue, spieler, alle_skills, alle_items,
                      menue_auswahl, status_meldung, verfuegbar)


def _zeichne_tod_screen(console):
    """Tod-Screen: gruselig, mit Totenkopf und zufaelligem Zitat."""
    console.clear()
    w = console.width
    h = console.height

    # Blutroter Hintergrund
    for y in range(h):
        for x in range(w):
            console.print(x, y, " ", bg=(18, 0, 0))

    # Totenkopf zentriert, oberes Drittel
    skull_y = h // 2 - 10
    skull_x = (w - len(_TOTENKOPF[0])) // 2
    for i, zeile in enumerate(_TOTENKOPF):
        console.print(skull_x, skull_y + i, zeile, fg=(160, 0, 0))

    # Titel
    y = skull_y + len(_TOTENKOPF) + 2
    titel = "- DU BIST TOT -"
    console.print((w - len(titel)) // 2, y, titel, fg=(220, 0, 0))

    # Todesursache und Zaehler
    ursache = f"Getoetet von:  {tod_gegner_name}"
    console.print((w - len(ursache)) // 2, y + 2, ursache, fg=(180, 50, 50))
    zaehler_txt = f"Tod Nr. {aktuell.get('tod_zaehler', 0)}"
    console.print((w - len(zaehler_txt)) // 2, y + 4, zaehler_txt, fg=(140, 30, 30))

    # Zitat
    zitat_txt = f'"{tod_zitat}"'
    console.print((w - len(zitat_txt)) // 2, y + 7, zitat_txt, fg=(120, 20, 20))

    # Weiter-Hinweis
    weiter = "[ LEERTASTE ]  Auferstehen"
    console.print((w - len(weiter)) // 2, h - 6, weiter, fg=(160, 60, 60))


# ---------------------------------------------------------------------------
# Spielschleife
# ---------------------------------------------------------------------------

def _zeichne_startbildschirm(console, zitat, hat_speicherstand=False):
    """Startbildschirm: Hintergrundbild (Halbblock), Titel-Overlay, Menue."""
    console.clear()
    w = console.width
    h = console.height

    # --- Hintergrundbild via Halbblock-Technik ---
    # Jede Kachel zeigt zwei Bildzeilen: fg=obere Haelfte, bg=untere Haelfte.
    # Dunkel-Zonen oben (Titel) und unten (Menue): Helligkeit auf 25% gedaempft.
    DUNKEL_OBEN  = 0    # kein abgedunkelter Bereich oben
    DUNKEL_UNTEN = 62   # Zeilen 62-71 abgedunkelt (Menubereich)

    def _px(tx, py):
        """Gibt (r,g,b) des Bildpixels an Kachel-x=tx, Pixel-y=py zurueck."""
        if _TITEL_PIXEL is None or tx >= _TITEL_W or py >= _TITEL_H:
            return (8, 4, 2)
        r, g, b, _ = _TITEL_PIXEL[py * _TITEL_W + tx]
        return r, g, b

    def _daempfe(rgb, faktor):
        return tuple(int(c * faktor) for c in rgb)

    for ty in range(h):
        dunkel = ty < DUNKEL_OBEN or ty >= DUNKEL_UNTEN
        faktor = 0.22 if dunkel else 1.0
        for tx in range(w):
            oben  = _daempfe(_px(tx, ty * 2),     faktor)
            unten = _daempfe(_px(tx, ty * 2 + 1), faktor)
            console.print(tx, ty, "\u2580", fg=oben, bg=unten)

    # --- Hilfsfunktionen fuer ASCII-Art ---
    def _glyph_breite(text):
        return sum(len(_GLYPH[c][0]) for c in text) + len(text) - 1

    def _ascii_wort(text, start_x, start_y, farbe):
        for zeile in range(5):
            x = start_x
            for i, buchstabe in enumerate(text):
                glyph = _GLYPH[buchstabe]
                for ch in glyph[zeile]:
                    if ch == "#":
                        console.print(x, start_y + zeile, ch, fg=farbe)
                    x += 1
                if i < len(text) - 1:
                    x += 1

    # --- Menue (im abgedunkelten Bereich unten, Zeilen 62-66) ---
    console.print((w - len(zitat)) // 2, 62, zitat, fg=(160, 100, 40))
    for x in range(25, w - 25):
        console.print(x, 63, "-", fg=(80, 50, 15))
    mx = (w - 26) // 2
    if hat_speicherstand:
        console.print(mx, 64, "[ ENTER ]  Weiter spielen", fg=(230, 215, 160))
        console.print(mx, 65, "[  N    ]  Neues Spiel",    fg=(180, 140, 80))
        console.print(mx, 66, "[  Q    ]  Beenden",        fg=(150, 100, 70))
    else:
        console.print(mx, 64, "[ ENTER ]  Neues Spiel", fg=(230, 215, 160))
        console.print(mx, 66, "[  Q    ]  Beenden",     fg=(150, 100, 70))
    version_txt = _VERSION
    console.print(w - 3 - len(version_txt), 66, version_txt, fg=(70, 45, 15))


def starte(console, context):
    global spieler, aktuell

    # Speicherstand pruefen
    geladener_spieler, geladenes_aktuell = laden()
    hat_speicherstand = geladener_spieler is not None
    if hat_speicherstand:
        spieler = geladener_spieler
        aktuell = geladenes_aktuell
        spieler.aktualisiere_lp_max(alle_skills)

    # Phase 1: Startbildschirm
    zitat = random.choice(_START_ZITATE)
    im_start = True
    while im_start:
        _zeichne_startbildschirm(console, zitat, hat_speicherstand)
        context.present(console)
        for event in tcod.event.wait():
            if isinstance(event, tcod.event.Quit):
                raise SystemExit()
            if isinstance(event, tcod.event.KeyDown):
                if event.sym in (tcod.event.KeySym.RETURN, tcod.event.KeySym.SPACE):
                    # Weiter spielen (oder neues Spiel wenn kein Save vorhanden)
                    im_start = False
                elif event.sym == tcod.event.KeySym.n and hat_speicherstand:
                    # Neues Spiel trotz vorhandenem Speicherstand
                    spieler = Spieler()
                    aktuell = dict(STANDARD_AKTUELL)
                    im_start = False
                elif event.sym == tcod.event.KeySym.q:
                    raise SystemExit()

    # Phase 2: Hauptspielschleife
    while True:
        if modus == "tod":
            _zeichne_tod_screen(console)
        elif ort == "pilsstube":
            _zeichne_hub(console)
        else:
            zeichne(console)
        context.present(console)

        for event in tcod.event.wait():
            if isinstance(event, tcod.event.Quit):
                raise SystemExit()
            if isinstance(event, tcod.event.KeyDown):
                _handle_key(event)


_BEWEGUNG_WIEDERHOLRATE = 0.12   # Sekunden zwischen Schritten beim Halten (ca. 8/s)

def _handle_key(event):
    global spieler_x, spieler_y, aktives_menue, menue_auswahl, status_meldung
    global aktiver_kampf, aktiver_kampf_eintrag, modus, ort
    global _letzter_bewegungszeitpunkt

    sym   = event.sym
    shift = bool(event.mod & tcod.event.KMOD_SHIFT)

    # -----------------------------------------------------------------------
    # Tod-Screen — nur Auferstehen
    # -----------------------------------------------------------------------
    if modus == "tod":
        if sym in (tcod.event.KeySym.SPACE, tcod.event.KeySym.RETURN):
            _tod_auferstehen()
        return

    # -----------------------------------------------------------------------
    # Kampf laeuft — Kampf-Eingabe oder Inventar
    # -----------------------------------------------------------------------
    if modus == "kampf":
        if aktives_menue:
            # Inventar im Kampf navigieren
            if sym in (tcod.event.KeySym.ESCAPE, tcod.event.KeySym.TAB):
                aktives_menue = None
                status_meldung = ""
            elif sym in (tcod.event.KeySym.UP, tcod.event.KeySym.w):
                menue_auswahl = max(0, menue_auswahl - 1)
                status_meldung = ""
            elif sym in (tcod.event.KeySym.DOWN, tcod.event.KeySym.s):
                n = menus_system.anzahl_auswaehlbar_fuer(aktives_menue, alle_skills, spieler)
                if n > 0:
                    menue_auswahl = min(n - 1, menue_auswahl + 1)
                status_meldung = ""
            elif sym == tcod.event.KeySym.RETURN:
                if aktives_menue == "inventar" and spieler.inventar:
                    idx = max(0, min(menue_auswahl, len(spieler.inventar) - 1))
                    item_id = spieler.inventar[idx]["id"]
                    ok, msg = inventar_system.benutzen(
                        spieler.inventar, item_id, spieler, alle_items)
                    status_meldung = msg if ok else f"!{msg}"
                    menue_auswahl = min(menue_auswahl, max(0, len(spieler.inventar) - 1))
        elif sym == tcod.event.KeySym.TAB:
            aktives_menue = "inventar"
            menue_auswahl = 0
            status_meldung = ""
        elif sym in (tcod.event.KeySym.SPACE, tcod.event.KeySym.RETURN):
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
                aktives_menue = menus_system.vorheriges_menue(aktives_menue, ort)
            else:
                aktives_menue = menus_system.naechstes_menue(aktives_menue, ort)
            menue_auswahl = 0
            status_meldung = ""

        elif sym in (tcod.event.KeySym.UP, tcod.event.KeySym.w):
            menue_auswahl = max(0, menue_auswahl - 1)
            status_meldung = ""

        elif sym in (tcod.event.KeySym.DOWN, tcod.event.KeySym.s):
            n = menus_system.anzahl_auswaehlbar_fuer(aktives_menue, alle_skills, spieler)
            if n > 0:
                menue_auswahl = min(n - 1, menue_auswahl + 1)
            status_meldung = ""

        elif sym == tcod.event.KeySym.RETURN:
            if aktives_menue == "skills":
                sid = menus_system.ausgewaehlte_skill_id(alle_skills, menue_auswahl)
                if sid:
                    ok, msg = spieler.skill_lernen(sid, alle_skills)
                    if ok:
                        spieler.aktualisiere_lp_max(alle_skills)
                    status_meldung = msg if ok else f"!{msg}"

            elif aktives_menue == "inventar" and spieler.inventar:
                idx = max(0, min(menue_auswahl, len(spieler.inventar) - 1))
                item_id = spieler.inventar[idx]["id"]
                ok, msg = inventar_system.benutzen(
                    spieler.inventar, item_id, spieler, alle_items)
                status_meldung = msg if ok else f"!{msg}"
                # Cursor korrigieren wenn Item verbraucht wurde
                menue_auswahl = min(menue_auswahl, max(0, len(spieler.inventar) - 1))

        return

    # -----------------------------------------------------------------------
    # Erkundung
    # -----------------------------------------------------------------------

    if sym == tcod.event.KeySym.TAB:
        verfuegbar = menus_system.verfuegbare_menues(ort)
        if verfuegbar:
            aktives_menue = verfuegbar[0]["id"]
            menue_auswahl = 0
            status_meldung = ""

    else:
        bewegen = _hub_bewege if ort == "pilsstube" else _bewege
        bewegungstasten = (
            tcod.event.KeySym.UP, tcod.event.KeySym.DOWN,
            tcod.event.KeySym.LEFT, tcod.event.KeySym.RIGHT,
            tcod.event.KeySym.w, tcod.event.KeySym.s,
            tcod.event.KeySym.a, tcod.event.KeySym.d,
        )
        if sym in bewegungstasten:
            if event.repeat:
                jetzt = time.monotonic()
                if jetzt - _letzter_bewegungszeitpunkt < _BEWEGUNG_WIEDERHOLRATE:
                    return
                _letzter_bewegungszeitpunkt = jetzt
            if   sym in (tcod.event.KeySym.UP,    tcod.event.KeySym.w): bewegen( 0, -1)
            elif sym in (tcod.event.KeySym.DOWN,  tcod.event.KeySym.s): bewegen( 0,  1)
            elif sym in (tcod.event.KeySym.LEFT,  tcod.event.KeySym.a): bewegen(-1,  0)
            elif sym in (tcod.event.KeySym.RIGHT, tcod.event.KeySym.d): bewegen( 1,  0)
        elif sym == tcod.event.KeySym.q:
            speichern(spieler, aktuell)
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

    # Ausgang betreten -> naechste Zone oder Hub
    if nx == DUNGEON_AUSGANG_X and ny == DUNGEON_AUSGANG_Y:
        if aktuell.get("zone_index", 0) < aktuell.get("zonen_gesamt", 1) - 1:
            aktuell["zone_index"] += 1
            _initialisiere_level()
        else:
            _zurueck_zum_hub()
        return

    # Freies Feld -> bewegen
    if ist_betretbar(nx, ny):
        spieler_x, spieler_y = nx, ny
        spieler.runden += 1
        spieler.ep_hinzufuegen(1)
        FOV = sichtfeld.berechne_fov(TRANSPARENZ, spieler_x, spieler_y)
        sichtfeld.aktualisiere_erkundet(ERKUNDET, FOV)

        # Item auf dem Feld aufheben (automatisch)
        bodenloot = aktuell.setdefault("bodenloot", [])
        aufzuheben = [l for l in bodenloot if l["x"] == nx and l["y"] == ny]
        for loot in aufzuheben:
            item_def = alle_items.get(loot["id"])
            if item_def:
                inventar_system.hinzufuegen(spieler.inventar, loot["id"], item_def)
                _log(f"{item_def['name']} aufgehoben.")
            bodenloot.remove(loot)

        # Gegner reagieren auf den Spielerzug
        angreifer = ki.ki_tick(gegner_auf_karte, spieler_x, spieler_y, KARTE)
        if angreifer:
            aktiver_kampf = KampfZustand(spieler, angreifer["gegner"])
            aktiver_kampf_eintrag = angreifer
            modus = "kampf"


def _hub_bewege(dx, dy):
    """Bewegung im Hub. Betritt der Spieler den Ausgang, startet der Run."""
    global hub_spieler_x, hub_spieler_y, HUB_FOV

    nx = hub_spieler_x + dx
    ny = hub_spieler_y + dy

    # Ausgang betreten?
    for obj in HUB_OBJEKTE:
        if obj["typ"] == "ausgang" and obj["x"] == nx and obj["y"] == ny:
            _betrete_dungeon()
            return

    # Normales Bodenfeld
    if 0 <= ny < len(HUB_KARTE) and 0 <= nx < len(HUB_KARTE[ny]):
        if HUB_KARTE[ny][nx] == ".":
            hub_spieler_x, hub_spieler_y = nx, ny
            HUB_FOV = sichtfeld.berechne_fov(HUB_TRANSPARENZ, hub_spieler_x, hub_spieler_y)
            sichtfeld.aktualisiere_erkundet(HUB_ERKUNDET, HUB_FOV)


def _zurueck_zum_hub():
    """Spieler verlaesst den Dungeon und kehrt zum Hub zurueck.

    LP, PP und MP werden vollstaendig aufgefuellt (Hub = sicherer Ort).
    """
    global ort
    spieler.lp = spieler.lp_max
    spieler.pp = spieler.pp_max
    spieler.mp = spieler.mp_max
    _log("Zurueck im Hub. LP/PP/MP aufgefuellt.")
    ort = "pilsstube"
    speichern(spieler, aktuell)


def _betrete_dungeon():
    """Spieler tritt durch den Braukessel ins Dungeon.

    Wuerfelt die Zonen-Anzahl fuer diesen Run und startet bei Zone 0.
    """
    global ort
    level_name = aktuell.get("level_name", "pflanzenzuechtung")
    grammatik  = alle_level[level_name]
    zonen_min  = grammatik.get("zonen_anzahl_min", 1)
    zonen_max  = grammatik.get("zonen_anzahl_max", 1)
    aktuell["zone_index"]   = 0
    aktuell["zonen_gesamt"] = random.randint(zonen_min, zonen_max)
    _initialisiere_level()
    _log(f"Dungeon betreten. {aktuell['zonen_gesamt']} Zone(n) warten.")
    ort = "dungeon"


def _tod_auferstehen():
    """LEERTASTE auf dem Tod-Screen: LP/PP zuruecksetzen, zurueck zum Hub."""
    global modus, ort, aktuell, hub_spieler_x, hub_spieler_y, HUB_FOV

    aktuell = tod_reset(spieler, aktuell)
    hub_spieler_x = HUB_START_X
    hub_spieler_y = HUB_START_Y
    HUB_FOV = sichtfeld.berechne_fov(HUB_TRANSPARENZ, hub_spieler_x, hub_spieler_y)
    sichtfeld.aktualisiere_erkundet(HUB_ERKUNDET, HUB_FOV)
    ort   = "pilsstube"
    modus = "hub"
    speichern(spieler, aktuell)


def _kampf_aktion():
    """LEERTASTE / ENTER im Kampf: naechste Runde oder Ergebnis bestaetigen."""
    global modus, aktiver_kampf, aktiver_kampf_eintrag, tod_gegner_name, tod_zitat

    if not aktiver_kampf.beendet:
        runde_ausfuehren(aktiver_kampf)
        return

    # Kampf beendet — Ergebnis verarbeiten
    if aktiver_kampf.ergebnis == "sieg":
        _log(f"{aktiver_kampf.gegner.name} besiegt.")
        # Loot-Wuerfel: jedes Item im loot_pool wird unabhaengig gewuerfelt
        for loot_eintrag in aktiver_kampf.gegner.loot_pool:
            if random.random() < loot_eintrag["chance"]:
                aktuell.setdefault("bodenloot", []).append({
                    "x": aktiver_kampf_eintrag["x"],
                    "y": aktiver_kampf_eintrag["y"],
                    "id": loot_eintrag["id"],
                })
        if aktiver_kampf_eintrag in gegner_auf_karte:
            gegner_auf_karte.remove(aktiver_kampf_eintrag)
        aktiver_kampf = None
        aktiver_kampf_eintrag = None
        modus = "hub"

    elif aktiver_kampf.ergebnis == "niederlage":
        tod_gegner_name = aktiver_kampf.gegner.name
        tod_zitat       = random.choice(_TOD_ZITATE)
        aktiver_kampf = None
        aktiver_kampf_eintrag = None
        modus = "tod"
