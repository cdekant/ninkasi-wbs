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
from src.systems.kampf import nahkampf_angriff, effekte_tick, regen_tick, spieler_fernkampf_angriff, gegner_fernkampf_angriff
from src.systems.speichern import tod_reset, STANDARD_AKTUELL, speichern, laden
from src.ui.menu_anzeige import zeichne_menue
from src.ui.charaktererstellung_anzeige import (
    zeichne_charaktererstellung, zeichne_eigenschaft_auswahl,
    EIGENSCHAFTEN_REIHENFOLGE,
)
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

# Spielmodus: "hub"                = Erkundung (Menues verfuegbar)
#             "tod"                = Tod-Screen (nur Auferstehen moeglich)
#             "charaktererstellung"= Startbildschirm, Punkte verteilen
#             "eigenschaft_auswahl"= Auswahl welche Eigenschaft ein Item-Punkt geht
#             "zielauswahl"        = Fernkampf-Zielauswahl (nur im Dungeon)
modus = "hub"

# Charaktererstellung und Eigenschaftspunkt-Vergabe
neues_spiel               = False   # True nach N oder wenn kein Savegame
eigenschaft_auswahl_item_id  = None    # Item-ID beim eigenschaft_punkt_erhoehen-Flow
eigenschaft_auswahl_index    = 0       # Markierte Eigenschaft (0–5)

# Ort: "pilsstube" = Hub | "dungeon" = laufender Run
ort = "pilsstube"

# Menue-Zustand
aktives_menue = None
menue_auswahl = 0
status_meldung = ""

_letzter_bewegungszeitpunkt = 0.0   # fuer Haltetasten-Rate-Limit

# Fernkampf / Zielauswahl
_ziel_sichtbar       = []   # Sichtbare lebende Gegner beim Eintritt in Zielauswahl
_ziel_gegner_index   = 0    # Aktuell angevisierter Gegner
_fernkampf_typen     = []   # Verfuegbare Angriffsmodi (dicts mit schaden_wert etc.)
_fernkampf_typ_index = 0    # Aktuell gewaehlter Modus

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

# Interaktive Dungeon-Objekte [{x, y, typ, loot_pool}]
DUNGEON_OBJEKTE = []

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

def _bfs_erreichbar(karte, start_x, start_y):
    """Gibt alle von (start_x, start_y) aus per '.' betretbaren Positionen zurueck."""
    from collections import deque
    besucht = {(start_x, start_y)}
    schlange = deque([(start_x, start_y)])
    while schlange:
        x, y = schlange.popleft()
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) not in besucht and 0 <= ny < len(karte) and 0 <= nx < len(karte[ny]):
                if karte[ny][nx] == ".":
                    besucht.add((nx, ny))
                    schlange.append((nx, ny))
    return besucht


def _initialisiere_level():
    """Generiert die Karte, setzt Spielerposition und spawnt Gegner.
    Wird beim Dungeon-Eintritt, Zonen-Wechsel und nach dem Tod aufgerufen.
    """
    global KARTE, spieler_x, spieler_y, gegner_auf_karte
    global TRANSPARENZ, FOV, ERKUNDET
    global DUNGEON_AUSGANG_X, DUNGEON_AUSGANG_Y
    global DUNGEON_OBJEKTE
    global _karte_boden_tile

    level_name = aktuell.get("level_name", "pflanzenzuechtung")
    grammatik  = alle_level[level_name]
    KARTE, DUNGEON_OBJEKTE = generiere_karte(grammatik, breite=config.BREITE, hoehe=config.KARTE_HOEHE)
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

    # Ausgang auf dem erreichbaren Bodentile am weitesten vom Spieler.
    # BFS stellt sicher, dass der Ausgang nie in einem isolierten Raum landet.
    erreichbar = _bfs_erreichbar(KARTE, spieler_x, spieler_y)
    erreichbar.discard((spieler_x, spieler_y))
    max_dist = -1
    DUNGEON_AUSGANG_X, DUNGEON_AUSGANG_Y = spieler_x, spieler_y  # Fallback
    for x, y in erreichbar:
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
    FOV         = sichtfeld.berechne_fov(TRANSPARENZ, spieler_x, spieler_y, spieler.berechne_sichtweite(alle_skills))
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
    HUB_FOV         = sichtfeld.berechne_fov(HUB_TRANSPARENZ, hub_spieler_x, hub_spieler_y, spieler.berechne_sichtweite(alle_skills))
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
# Kampf-Hilfsfunktionen
# ---------------------------------------------------------------------------

def _gegner_farbe(gegner):
    """Gibt die Anzeige-Farbe des Gegner-Symbols basierend auf HP-Anteil zurueck."""
    pct = gegner.hp / gegner.hp_max * 100 if gegner.hp_max > 0 else 0
    if pct <= config.GEGNER_HP_VERWUNDET_PCT:
        return config.GEGNER_FARBE_VERWUNDET
    if pct <= config.GEGNER_HP_ANGESCHLAGEN_PCT:
        return config.GEGNER_FARBE_ANGESCHLAGEN
    return config.GEGNER_FARBE_VOLL


def _gegner_zustand_meldung(gegner):
    """Einmalige Log-Meldung wenn Gegner einen HP-Schwellwert unterschreitet."""
    pct = gegner.hp / gegner.hp_max * 100 if gegner.hp_max > 0 else 0
    if pct <= config.GEGNER_HP_VERWUNDET_PCT and not getattr(gegner, "_meldung_verwundet", False):
        gegner._meldung_verwundet = True
        _log(f"{gegner.name} wirkt schwer verwundet.")
    elif pct <= config.GEGNER_HP_ANGESCHLAGEN_PCT and not getattr(gegner, "_meldung_angeschlagen", False):
        gegner._meldung_angeschlagen = True
        _log(f"{gegner.name} wirkt angeschlagen.")


def _loot_wuerfeln(eintrag):
    """Wuerfelt Loot fuer einen besiegten Gegner und legt ihn als Bodenloot ab."""
    g = eintrag["gegner"]
    spieler.ep_hinzufuegen(g.ep_beute)
    _log(f"{g.name} besiegt. +{g.ep_beute} EP")
    for loot_eintrag in g.loot_pool:
        if random.random() < loot_eintrag["chance"]:
            aktuell.setdefault("bodenloot", []).append({
                "x": eintrag["x"],
                "y": eintrag["y"],
                "id": loot_eintrag["id"],
            })


def _spieler_tot(verursacher_name):
    """Setzt den Tod-Modus mit Verursacher-Name und zufaelligem Zitat."""
    global modus, tod_gegner_name, tod_zitat
    tod_gegner_name = verursacher_name
    tod_zitat       = random.choice(_TOD_ZITATE)
    modus = "tod"


# ---------------------------------------------------------------------------
# Fernkampf
# ---------------------------------------------------------------------------

def _fernkampf_typen_bauen():
    """Baut Liste aller verfuegbaren Fernkampf-Modi aus Ausruestung, Inventar, PP und MP."""
    typen = []
    # Schusswaffe (waffe_haupt oder waffe_neben mit reichweite > 1)
    for slot_name in ("waffe_haupt", "waffe_neben"):
        ausgeruestet = spieler.ausruestung.get(slot_name)
        if ausgeruestet:
            item_def = alle_items.get(ausgeruestet["id"])
            if item_def and item_def.get("reichweite", 1) > 1:
                typen.append({
                    "typ":          "schusswaffe",
                    "name":         item_def["name"],
                    "schaden_wert": spieler.basis_schaden + item_def.get("schaden_bonus", 0),
                    "schaden_typ":  item_def.get("schaden_typ", "fern"),
                    "reichweite":   item_def["reichweite"],
                    "item_def":     item_def,
                })
    # Wurfwaffe (alle Stacks im Inventar)
    for inv_slot in spieler.inventar:
        item_def = alle_items.get(inv_slot["id"])
        if item_def and item_def.get("kategorie") == "wurfwaffe" and inv_slot["anzahl"] > 0:
            typen.append({
                "typ":          "wurfwaffe",
                "name":         item_def["name"],
                "schaden_wert": item_def.get("schaden_wert", spieler.basis_schaden),
                "schaden_typ":  item_def.get("schaden_typ", "nah"),
                "reichweite":   item_def.get("reichweite", 5),
                "item_def":     item_def,
                "inv_slot":     inv_slot,
            })
    # MP-Schuss
    if spieler.mp >= config.MP_FERNKAMPF_KOSTEN:
        typen.append({
            "typ":          "mp",
            "name":         "Magie-Schuss",
            "schaden_wert": config.MP_FERNKAMPF_SCHADEN,
            "schaden_typ":  "magie",
            "reichweite":   config.MP_FERNKAMPF_REICHWEITE,
            "item_def":     None,
        })
    # PP-Schuss
    if spieler.pp >= config.PP_FERNKAMPF_KOSTEN:
        typen.append({
            "typ":          "pp",
            "name":         "Psi-Schuss",
            "schaden_wert": config.PP_FERNKAMPF_SCHADEN,
            "schaden_typ":  "psi",
            "reichweite":   config.PP_FERNKAMPF_REICHWEITE,
            "item_def":     None,
        })
    return typen


def _zielauswahl_eintreten():
    """F-Taste im Dungeon: Wechselt in den Zielauswahl-Modus."""
    global modus, _ziel_sichtbar, _ziel_gegner_index, _fernkampf_typen, _fernkampf_typ_index
    if ort != "dungeon":
        return
    _ziel_sichtbar = [
        e for e in gegner_auf_karte
        if e["gegner"].lebt and FOV[e["y"], e["x"]]
    ]
    if not _ziel_sichtbar:
        _log("Kein Ziel in Sichtweite.")
        return
    _fernkampf_typen = _fernkampf_typen_bauen()
    if not _fernkampf_typen:
        _log("Kein Fernkampf-Angriff verfuegbar.")
        return
    _ziel_gegner_index   = 0
    _fernkampf_typ_index = 0
    modus = "zielauswahl"


def _fernkampf_ausfuehren():
    """Schuss ausfuehren: Ressource pruefen, Schaden anwenden, Welt-Tick."""
    global modus
    eintrag = _ziel_sichtbar[_ziel_gegner_index]
    angriff = _fernkampf_typen[_fernkampf_typ_index]
    ziel    = eintrag["gegner"]

    # Sichtlinie pruefen
    if not sichtfeld.sichtlinie_frei(TRANSPARENZ, spieler_x, spieler_y, eintrag["x"], eintrag["y"]):
        _log("Keine Sichtlinie zum Ziel.")
        return

    # Reichweite pruefen (Chebyshev)
    dist = max(abs(eintrag["x"] - spieler_x), abs(eintrag["y"] - spieler_y))
    if dist > angriff["reichweite"]:
        _log(f"Ziel ausser Reichweite ({dist} > {angriff['reichweite']}).")
        return

    # Ressource pruefen
    typ = angriff["typ"]
    if typ == "pp" and spieler.pp < config.PP_FERNKAMPF_KOSTEN:
        _log(f"Zu wenig PP (benoetigt {config.PP_FERNKAMPF_KOSTEN}).")
        return
    if typ == "mp" and spieler.mp < config.MP_FERNKAMPF_KOSTEN:
        _log(f"Zu wenig MP (benoetigt {config.MP_FERNKAMPF_KOSTEN}).")
        return

    # Zielauswahl verlassen, Angriff ausfuehren
    modus = "hub"
    for z in spieler_fernkampf_angriff(spieler, ziel, angriff):
        _log(z)

    # Ressource abziehen
    if typ == "pp":
        spieler.pp = max(0, spieler.pp - config.PP_FERNKAMPF_KOSTEN)
    elif typ == "mp":
        spieler.mp = max(0, spieler.mp - config.MP_FERNKAMPF_KOSTEN)
    elif typ == "wurfwaffe":
        inventar_system.entfernen(spieler.inventar, angriff["item_def"]["id"])

    # Gegner tot?
    if not ziel.lebt:
        _loot_wuerfeln(eintrag)
        gegner_auf_karte.remove(eintrag)

    _welt_tick()


def _zielauswahl_zeichnen(console):
    """Overlay fuer den Zielauswahl-Modus: Linie, Cursor, Shortcut-Zeile."""
    if not _ziel_sichtbar or not _fernkampf_typen:
        return
    KY = config.KARTE_Y0
    eintrag = _ziel_sichtbar[_ziel_gegner_index]
    tx, ty  = eintrag["x"], eintrag["y"]
    angriff = _fernkampf_typen[_fernkampf_typ_index]

    # Bresenham-Linie zeichnen (ohne Spieler- und Zielfeld)
    for x, y in sichtfeld.linie_punkte(spieler_x, spieler_y, tx, ty)[1:-1]:
        console.print(x, y + KY, "\u00b7", fg=(180, 140, 40))

    # Ziel-Cursor
    console.print(tx, ty + KY, "X", fg=(255, 220, 0))

    # Shortcut-Zeile
    typ = angriff["typ"]
    if typ == "pp":
        ressource = f"PP-{config.PP_FERNKAMPF_KOSTEN}"
    elif typ == "mp":
        ressource = f"MP-{config.MP_FERNKAMPF_KOSTEN}"
    elif typ == "wurfwaffe":
        ressource = f"{angriff['inv_slot']['anzahl']}\u00d7"
    else:
        ressource = "ausger\u00fcstet"

    dist = max(abs(tx - spieler_x), abs(ty - spieler_y))
    los  = sichtfeld.sichtlinie_frei(TRANSPARENZ, spieler_x, spieler_y, tx, ty)
    los_txt = "" if los else " [WAND]"
    ziel_name = eintrag["gegner"].name
    shortcut = (
        f"[TAB] Ziel: {ziel_name}  "
        f"[R] {angriff['name']} ({ressource})  "
        f"Dist:{dist}/{angriff['reichweite']}{los_txt}  "
        f"[ENTER] Schuss  [ESC] Abbruch"
    )
    _zeichne_log(console, shortcut)


def _welt_tick():
    """Ein Welt-Tick nach jeder Spieleraktion: Regen + Effekte, dann Gegner-KI.

    Reihenfolge:
      1. Regeneration + Effekte fuer alle lebenden Gegner (DoT, Dauer sinkt)
      2. Effekte fuer den Spieler
      3. Gegner-KI: alle lebenden Gegner bewegen sich / greifen an
    Tote Gegner werden sofort aus gegner_auf_karte entfernt (Loot gewuerfelt).
    """
    # 1. Regen + Effekte fuer Gegner
    for eintrag in list(gegner_auf_karte):
        g = eintrag["gegner"]
        if not g.lebt:
            continue
        zeile = regen_tick(g)
        if zeile:
            _log(zeile)
        for z in effekte_tick(g):
            _log(z)
        if not g.lebt:
            _loot_wuerfeln(eintrag)
            gegner_auf_karte.remove(eintrag)

    # 2. Effekte fuer Spieler
    for z in effekte_tick(spieler):
        _log(z)
    if spieler.lp <= 0:
        _spieler_tot("Vergiftung")
        return

    # 3. Gegner-KI: Bewegung und Angriffe
    nah_liste, fern_liste = ki.ki_tick(gegner_auf_karte, spieler_x, spieler_y, KARTE, TRANSPARENZ)
    for eintrag in nah_liste:
        for z in nahkampf_angriff(eintrag["gegner"], spieler):
            _log(z)
        if spieler.lp <= 0:
            _spieler_tot(eintrag["gegner"].name)
            return
    for eintrag in fern_liste:
        for z in gegner_fernkampf_angriff(eintrag["gegner"], spieler):
            _log(z)
        if spieler.lp <= 0:
            _spieler_tot(eintrag["gegner"].name)
            return


def _gelegenheitsangriff():
    """Alle Chebyshev-1-anliegenden lebenden Gegner greifen sofort an (vor Bewegung).

    Wird aufgerufen wenn der Spieler sich von einem belegten Feld wegbewegt.
    """
    for eintrag in gegner_auf_karte:
        g = eintrag["gegner"]
        if not g.lebt:
            continue
        if max(abs(eintrag["x"] - spieler_x), abs(eintrag["y"] - spieler_y)) == 1:
            for z in nahkampf_angriff(g, spieler):
                _log(z)
            if spieler.lp <= 0:
                _spieler_tot(g.name)
                return


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
                elif zeichen == tiles.INTER_FASS:
                    console.print(x, cy, anzeige, fg=(160, 110, 60))
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
                elif zeichen == tiles.INTER_FASS:
                    console.print(x, cy, anzeige, fg=(50, 35, 20))
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

    # Gegner — nur sichtbar wenn im FOV; Farbe zeigt HP-Zustand
    for eintrag in gegner_auf_karte:
        g = eintrag["gegner"]
        if g.lebt and FOV[eintrag["y"], eintrag["x"]]:
            console.print(eintrag["x"], eintrag["y"] + KY,
                          g.symbol, fg=_gegner_farbe(g))

    # Spieler
    console.print(spieler_x, spieler_y + KY, tiles.HUB_NINKASI, fg=(255, 215, 0))

    # Statuszeile (Zeilen 0-1)
    _zeichne_statuszeile(console)

    # Nachrichtenlog + Shortcuts
    _zeichne_log(console, "[F] Ziel  [TAB] Skills  [I] Inventar  [C] Charakter  [<] Ausgang  [Q] Beenden")

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
    _zeichne_log(console, "[TAB] Skills  [I] Inventar  [C] Charakter  [Kessel] Dungeon  [Q] Beenden")

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


def _charaktererstellung_durchfuehren(console, context):
    """Zeigt den Charaktererstellungs-Bildschirm und traegt die gewaehlten Punkte ein.

    Laeuft in einer eigenen Schleife bis der Spieler alle Punkte verteilt und ENTER
    gedrueckt hat. Aendert spieler.eigenschaften direkt.
    """
    temp = {k: 0 for k in EIGENSCHAFTEN_REIHENFOLGE}
    auswahl    = 0
    verbleibend = config.EIGENSCHAFT_START_PUNKTE

    while True:
        zeichne_charaktererstellung(console, temp, auswahl, verbleibend)
        context.present(console)
        for event in tcod.event.wait():
            if isinstance(event, tcod.event.Quit):
                raise SystemExit()
            if not isinstance(event, tcod.event.KeyDown):
                continue
            s = event.sym
            key = EIGENSCHAFTEN_REIHENFOLGE[auswahl]
            if s in (tcod.event.KeySym.UP, tcod.event.KeySym.w):
                auswahl = (auswahl - 1) % len(EIGENSCHAFTEN_REIHENFOLGE)
            elif s in (tcod.event.KeySym.DOWN, tcod.event.KeySym.s):
                auswahl = (auswahl + 1) % len(EIGENSCHAFTEN_REIHENFOLGE)
            elif s in (tcod.event.KeySym.RIGHT, tcod.event.KeySym.d):
                if verbleibend > 0 and temp[key] < config.EIGENSCHAFT_START_MAX:
                    temp[key]   += 1
                    verbleibend -= 1
            elif s in (tcod.event.KeySym.LEFT, tcod.event.KeySym.a):
                if temp[key] > 0:
                    temp[key]   -= 1
                    verbleibend += 1
            elif s == tcod.event.KeySym.RETURN and verbleibend == 0:
                spieler.eigenschaften = dict(temp)
                return


def starte(console, context):
    global spieler, aktuell, neues_spiel, modus, ort

    # Speicherstand pruefen
    geladener_spieler, geladenes_aktuell = laden()
    hat_speicherstand = geladener_spieler is not None
    if hat_speicherstand:
        spieler = geladener_spieler
        aktuell = geladenes_aktuell
        spieler.aktualisiere_lp_max(alle_skills)
    else:
        neues_spiel = True   # kein Savegame → Charaktererstellung zeigen

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
                    neues_spiel = True
                    im_start = False
                elif event.sym == tcod.event.KeySym.q:
                    raise SystemExit()

    # Phase 1.5: Charaktererstellung (nur bei neuem Spiel)
    if neues_spiel:
        _charaktererstellung_durchfuehren(console, context)
        neues_spiel = False

    # Phase 2: Hauptspielschleife
    while True:
        if modus == "charaktererstellung":
            _charaktererstellung_durchfuehren(console, context)
            ort   = "pilsstube"
            modus = "hub"
            speichern(spieler, aktuell)
        elif modus == "tod":
            _zeichne_tod_screen(console)
        elif modus == "zielauswahl":
            zeichne(console)
            _zielauswahl_zeichnen(console)
        elif modus == "eigenschaft_auswahl":
            # Hintergrund je nach Aufenthaltsort, dann Overlay
            if ort == "pilsstube":
                _zeichne_hub(console)
            else:
                zeichne(console)
            zeichne_eigenschaft_auswahl(console, spieler, eigenschaft_auswahl_index)
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


_BEWEGUNG_WIEDERHOLRATE = 0.10   # Sekunden zwischen Schritten beim Halten (ca. 10/s)

def _handle_key(event):
    global spieler_x, spieler_y, aktives_menue, menue_auswahl, status_meldung
    global modus, ort
    global _letzter_bewegungszeitpunkt
    global eigenschaft_auswahl_item_id, eigenschaft_auswahl_index
    global _ziel_gegner_index, _fernkampf_typ_index

    sym   = event.sym
    shift = bool(event.mod & tcod.event.KMOD_SHIFT)

    # -----------------------------------------------------------------------
    # Zielauswahl (Fernkampf)
    # -----------------------------------------------------------------------
    if modus == "zielauswahl":
        if sym in (tcod.event.KeySym.ESCAPE, tcod.event.KeySym.f):
            modus = "hub"
        elif sym == tcod.event.KeySym.TAB:
            if _ziel_sichtbar:
                if shift:
                    _ziel_gegner_index = (_ziel_gegner_index - 1) % len(_ziel_sichtbar)
                else:
                    _ziel_gegner_index = (_ziel_gegner_index + 1) % len(_ziel_sichtbar)
        elif sym == tcod.event.KeySym.r:
            if _fernkampf_typen:
                _fernkampf_typ_index = (_fernkampf_typ_index + 1) % len(_fernkampf_typen)
        elif sym == tcod.event.KeySym.RETURN:
            _fernkampf_ausfuehren()
        return

    # -----------------------------------------------------------------------
    # Eigenschaftspunkt-Vergabe per Item — Auswahl welche Eigenschaft
    # -----------------------------------------------------------------------
    if modus == "eigenschaft_auswahl":
        if sym in (tcod.event.KeySym.UP, tcod.event.KeySym.w):
            eigenschaft_auswahl_index = (eigenschaft_auswahl_index - 1) % len(EIGENSCHAFTEN_REIHENFOLGE)
        elif sym in (tcod.event.KeySym.DOWN, tcod.event.KeySym.s):
            eigenschaft_auswahl_index = (eigenschaft_auswahl_index + 1) % len(EIGENSCHAFTEN_REIHENFOLGE)
        elif sym == tcod.event.KeySym.RETURN:
            key = EIGENSCHAFTEN_REIHENFOLGE[eigenschaft_auswahl_index]
            spieler.eigenschaften[key] += 1
            inventar_system.entfernen(spieler.inventar, eigenschaft_auswahl_item_id)
            name_anzeige = key.replace("_", " ").capitalize()
            _log(f"+1 {name_anzeige}")
            status_meldung = f"+1 {name_anzeige}"
            eigenschaft_auswahl_item_id = None
            eigenschaft_auswahl_index   = 0
            modus = "hub"
        elif sym == tcod.event.KeySym.ESCAPE:
            # Abbrechen — Item bleibt im Inventar
            eigenschaft_auswahl_item_id = None
            eigenschaft_auswahl_index   = 0
            modus = "hub"
        return

    # -----------------------------------------------------------------------
    # Tod-Screen — nur Auferstehen
    # -----------------------------------------------------------------------
    if modus == "tod":
        if sym in (tcod.event.KeySym.SPACE, tcod.event.KeySym.RETURN):
            _tod_auferstehen()
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
                ok, extra = inventar_system.benutzen(
                    spieler.inventar, item_id, spieler, alle_items)
                if ok == "auswahl_noetig":
                    eigenschaft_auswahl_item_id = extra
                    eigenschaft_auswahl_index   = 0
                    aktives_menue = None
                    modus = "eigenschaft_auswahl"
                else:
                    status_meldung = extra if ok else f"!{extra}"
                    # Cursor korrigieren wenn Item verbraucht wurde
                    menue_auswahl = min(menue_auswahl, max(0, len(spieler.inventar) - 1))

        return

    # -----------------------------------------------------------------------
    # Erkundung
    # -----------------------------------------------------------------------

    if sym == tcod.event.KeySym.TAB:
        aktives_menue = "skills"
        menue_auswahl = 0
        status_meldung = ""

    elif sym == tcod.event.KeySym.i:
        # I oeffnet Inventar (Hub und Dungeon)
        aktives_menue = "inventar"
        menue_auswahl = 0
        status_meldung = ""

    elif sym == tcod.event.KeySym.c and ort in ("pilsstube", "dungeon"):
        # C oeffnet Charakter-Screen (Hub und Dungeon)
        aktives_menue = "charakter"
        menue_auswahl = 0
        status_meldung = ""

    elif sym == tcod.event.KeySym.f and ort == "dungeon":
        _zielauswahl_eintreten()

    else:
        bewegen = _hub_bewege if ort == "pilsstube" else _bewege
        bewegungstasten = (
            tcod.event.KeySym.UP, tcod.event.KeySym.DOWN,
            tcod.event.KeySym.LEFT, tcod.event.KeySym.RIGHT,
            tcod.event.KeySym.w, tcod.event.KeySym.s,
            tcod.event.KeySym.a, tcod.event.KeySym.d,
            tcod.event.KeySym.z, tcod.event.KeySym.u,    # NW / NE
            tcod.event.KeySym.b, tcod.event.KeySym.n,    # SW / SE
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
            elif sym == tcod.event.KeySym.z:              bewegen(-1, -1)  # NW
            elif sym == tcod.event.KeySym.u:              bewegen( 1, -1)  # NE
            elif sym == tcod.event.KeySym.b:              bewegen(-1,  1)  # SW
            elif sym == tcod.event.KeySym.n:              bewegen( 1,  1)  # SE
        elif sym == tcod.event.KeySym.q:
            speichern(spieler, aktuell)
            raise SystemExit()


def _bewege(dx, dy):
    global spieler_x, spieler_y, FOV, modus

    nx, ny = spieler_x + dx, spieler_y + dy

    # Gegner auf Zielfeld? -> Bump-Angriff (Spieler greift an, kein Modus-Wechsel)
    for eintrag in list(gegner_auf_karte):
        if eintrag["x"] == nx and eintrag["y"] == ny and eintrag["gegner"].lebt:
            for z in nahkampf_angriff(spieler, eintrag["gegner"]):
                _log(z)
            _gegner_zustand_meldung(eintrag["gegner"])
            if not eintrag["gegner"].lebt:
                _loot_wuerfeln(eintrag)
                gegner_auf_karte.remove(eintrag)
            _welt_tick()
            return

    # Interaktives Objekt? (Bump-Interaktion)
    for obj in DUNGEON_OBJEKTE:
        if obj["x"] == nx and obj["y"] == ny:
            for loot_eintrag in obj.get("loot_pool", []):
                if random.random() < loot_eintrag["chance"]:
                    aktuell.setdefault("bodenloot", []).append(
                        {"x": nx, "y": ny, "id": loot_eintrag["id"]}
                    )
            zeile = list(KARTE[ny])
            zeile[nx] = "."
            KARTE[ny] = "".join(zeile)
            DUNGEON_OBJEKTE.remove(obj)
            _log("Holzfass zerstört.")
            return

    # Ausgang betreten -> naechste Zone oder Hub
    if nx == DUNGEON_AUSGANG_X and ny == DUNGEON_AUSGANG_Y:
        if aktuell.get("zone_index", 0) < aktuell.get("zonen_gesamt", 1) - 1:
            aktuell["zone_index"] += 1
            _initialisiere_level()
        else:
            _zurueck_zum_hub()
        return

    # Freies Feld -> Gelegenheitsangriff-Check, dann bewegen
    if ist_betretbar(nx, ny):
        _gelegenheitsangriff()
        if modus == "tod":
            return
        spieler_x, spieler_y = nx, ny
        spieler.runden += 1
        spieler.ep_hinzufuegen(1)
        FOV = sichtfeld.berechne_fov(TRANSPARENZ, spieler_x, spieler_y, spieler.berechne_sichtweite(alle_skills))
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

        # Geschwindigkeits-Akkumulator: Bonus-Schritte loesen keinen Welt-Tick aus.
        # Ganzzahl-Prozente (skaliert x100) vermeiden Floating-Point-Drift.
        bonus_pct = int(round(spieler.berechne_geschwindigkeit(alle_skills) * 100)) - 100
        spieler.bewegungs_bonus_zaehler += bonus_pct
        if spieler.bewegungs_bonus_zaehler >= 100:
            spieler.bewegungs_bonus_zaehler -= 100
        else:
            _welt_tick()


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
            HUB_FOV = sichtfeld.berechne_fov(HUB_TRANSPARENZ, hub_spieler_x, hub_spieler_y, spieler.berechne_sichtweite(alle_skills))
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
    """LEERTASTE auf dem Tod-Screen: Vollstaendiger Reset, weiter zur Charaktererstellung."""
    global modus, ort, aktuell, hub_spieler_x, hub_spieler_y, HUB_FOV

    aktuell = tod_reset(spieler, aktuell)
    spieler.aktualisiere_lp_max(alle_skills)   # lp_max auf Basis zuruecksetzen (Skills geleert)
    spieler.lp = spieler.lp_max
    hub_spieler_x = HUB_START_X
    hub_spieler_y = HUB_START_Y
    HUB_FOV = sichtfeld.berechne_fov(HUB_TRANSPARENZ, hub_spieler_x, hub_spieler_y, spieler.berechne_sichtweite(alle_skills))
    sichtfeld.aktualisiere_erkundet(HUB_ERKUNDET, HUB_FOV)
    ort   = "pilsstube"
    modus = "charaktererstellung"


