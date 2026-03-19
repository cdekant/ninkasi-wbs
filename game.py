import json
import random
import tcod
import config

try:
    from PIL import Image as _PILImage
    _img = _PILImage.open("assets/ninkasi_brutality_120x144.png").convert("RGBA")
    _TITEL_PIXEL = list(_img.getdata())   # [(r,g,b,a), ...] flach, 120×144
    _TITEL_W, _TITEL_H = _img.size       # 120, 144
except Exception:
    _TITEL_PIXEL = None
    _TITEL_W = _TITEL_H = 0

import src.systems.skills as skills_system
import src.systems.menus as menus_system
from src.entities.player import Spieler
from src.entities.gegner import typen_laden, Gegner
from src.systems.kampf import KampfZustand, runde_ausfuehren
from src.systems.speichern import tod_reset, STANDARD_AKTUELL, speichern, laden
from src.ui.menu_anzeige import zeichne_menue
from src.map.bsp import generiere_karte
from src.map.hub import generiere_hub as _generiere_hub
from src.systems import sichtfeld
from src.systems import ki


# ---------------------------------------------------------------------------
# Konstanten
# ---------------------------------------------------------------------------

KAMPF_PANEL_HOEHE = 9   # Zeilen fuer das Kampf-Panel am unteren Rand


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
    '"Der Prohibitus wird fallen. Oder wir trinken seinen Ruin."',
    '"Die Hefe tut was sie will. Der Brauer lenkt sie nur."',
    '"Tod ist nur ein Neustart ohne Stammwuerze."',
    '"Nieder mit dem Daemon der Abstinenz!"',
    '"Bier ist der Beweis, dass die Goetter uns lieben."',
]

_TOD_ZITATE = [
    "Das Bier raeche sich. Du nicht.",
    "Selbst Goetter koennen sterben. Manche sogar mehrfach.",
    "Tod ist nur eine Pause zwischen zwei Gaerungen.",
    "Der Prohibitus lacht. Noch.",
    "Niemand hat gesagt, Brauen sei einfach.",
    "Hefe 1, Ninkasi 0.",
    "Du riechst nach Niederlage. Und ein bisschen nach Schimmel.",
    "Komm wieder wenn du kein Wasser mehr trinkst.",
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
    Wird beim Start und nach dem Tod aufgerufen.
    """
    global KARTE, spieler_x, spieler_y, gegner_auf_karte
    global TRANSPARENZ, FOV, ERKUNDET
    global DUNGEON_AUSGANG_X, DUNGEON_AUSGANG_Y

    KARTE = generiere_karte(alle_level["gaerkeller"], breite=config.BREITE, hoehe=config.HOEHE - 1)

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

    _spawne_gegner(12)

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


def _initialisiere_hub():
    """Baut die Hub-Karte einmalig beim Spielstart auf."""
    global HUB_KARTE, HUB_OBJEKTE, HUB_START_X, HUB_START_Y
    global hub_spieler_x, hub_spieler_y
    global HUB_TRANSPARENZ, HUB_FOV, HUB_ERKUNDET

    HUB_KARTE, sx, sy, ausgang = _generiere_hub(config.BREITE, config.HOEHE - 1)
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

    # Dungeon-Ausgang
    if FOV[DUNGEON_AUSGANG_Y, DUNGEON_AUSGANG_X]:
        console.print(DUNGEON_AUSGANG_X, DUNGEON_AUSGANG_Y, "<", fg=(80, 200, 255))

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
               f"PP: {spieler.pp}/{spieler.pp_max}  "
               f"MP: {spieler.mp}/{spieler.mp_max}")
        console.print(1, console.height - 1, hud, fg=(100, 200, 120))
        console.print(console.width - 32, console.height - 1,
                      "[TAB] Menue  [<] Hub  [Q] Beenden", fg=(80, 80, 80))

    # Kampf-Panel
    if modus == "kampf" and aktiver_kampf:
        _zeichne_kampf_panel(console)

    # Menue-Overlay (uebermalt alles andere)
    if aktives_menue:
        verfuegbar = menus_system.verfuegbare_menues(ort)
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
# Hub und Tod-Screen zeichnen
# ---------------------------------------------------------------------------

def _zeichne_hub(console):
    """Hub zeichnen."""
    console.clear()

    # Karte mit FOV — warme Bodenfarbe (Holz/Stroh) statt Dungeon-Grau
    for y, zeile in enumerate(HUB_KARTE):
        for x, zeichen in enumerate(zeile):
            if HUB_FOV[y, x]:
                fg = (160, 160, 160) if zeichen == "#" else (110, 80, 35)
                console.print(x, y, zeichen, fg=fg)
            elif HUB_ERKUNDET[y, x]:
                fg = (50, 50, 50) if zeichen == "#" else (40, 28, 10)
                console.print(x, y, zeichen, fg=fg)

    # Hub-Objekte (Braukessel/Ausgang etc.)
    for obj in HUB_OBJEKTE:
        if HUB_FOV[obj["y"], obj["x"]]:
            console.print(obj["x"], obj["y"], obj["symbol"], fg=obj["farbe"])

    # Spieler
    console.print(hub_spieler_x, hub_spieler_y, "@", fg=(255, 215, 0))

    # HUD
    hud = (f"EP: {spieler.ep_verfuegbar}  "
           f"LP: {spieler.lp}/{spieler.lp_max}  "
           f"PP: {spieler.pp}/{spieler.pp_max}  "
           f"MP: {spieler.mp}/{spieler.mp_max}")
    console.print(1, console.height - 1, hud, fg=(100, 200, 120))
    console.print(console.width - 38, console.height - 1,
                  "[TAB] Menue  [Kessel] Dungeon  [Q] Beenden", fg=(80, 80, 80))

    # Menue-Overlay
    if aktives_menue:
        verfuegbar = menus_system.verfuegbare_menues(ort)
        zeichne_menue(console, aktives_menue, spieler, alle_skills,
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

    # --- Menue (im abgedunkelten Bereich unten) ---
    console.print((w - len(zitat)) // 2, 63, zitat, fg=(160, 100, 40))
    for x in range(25, w - 25):
        console.print(x, 65, "-", fg=(80, 50, 15))
    mx = (w - 26) // 2
    if hat_speicherstand:
        console.print(mx, 66, "[ ENTER ]  Weiter spielen", fg=(230, 215, 160))
        console.print(mx, 68, "[  N    ]  Neues Spiel",    fg=(180, 140, 80))
        console.print(mx, 70, "[  Q    ]  Beenden",        fg=(150, 100, 70))
    else:
        console.print(mx, 67, "[ ENTER ]  Neues Spiel", fg=(230, 215, 160))
        console.print(mx, 69, "[  Q    ]  Beenden",      fg=(150, 100, 70))
    version_txt = "v0.5.7"
    console.print(w - 3 - len(version_txt), 71, version_txt, fg=(70, 45, 15))


def starte(console, context):
    global spieler, aktuell

    # Speicherstand pruefen
    geladener_spieler, geladenes_aktuell = laden()
    hat_speicherstand = geladener_spieler is not None
    if hat_speicherstand:
        spieler = geladener_spieler
        aktuell = geladenes_aktuell

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


def _handle_key(event):
    global spieler_x, spieler_y, aktives_menue, menue_auswahl, status_meldung
    global aktiver_kampf, aktiver_kampf_eintrag, modus, ort

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
                aktives_menue = menus_system.vorheriges_menue(aktives_menue, ort)
            else:
                aktives_menue = menus_system.naechstes_menue(aktives_menue, ort)
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
        verfuegbar = menus_system.verfuegbare_menues(ort)
        if verfuegbar:
            aktives_menue = verfuegbar[0]["id"]
            menue_auswahl = 0
            status_meldung = ""

    else:
        bewegen = _hub_bewege if ort == "pilsstube" else _bewege
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

    # Ausgang betreten -> zurueck zum Hub
    if nx == DUNGEON_AUSGANG_X and ny == DUNGEON_AUSGANG_Y:
        _zurueck_zum_hub()
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
    """Spieler verlaesst den Dungeon und kehrt zum Hub zurueck."""
    global ort
    ort = "pilsstube"
    speichern(spieler, aktuell)


def _betrete_dungeon():
    """Spieler tritt durch den Braukessel ins Dungeon."""
    global ort
    _initialisiere_level()
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
