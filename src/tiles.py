# Tile-Konstanten und zugehoerige PNG-Dateien.
# Unicode Private Use Area U+E000–U+F8FF (6400 Slots) — kein Konflikt mit Cheepicus/CP437.
#
# Neues Tile hinzufuegen: Konstante in passendem Cluster + Eintrag in TILE_DATEIEN.
#
# Benennungsschema: GRUPPE_NAME[_VARIANTE]
#   GRUPPE beschreibt Funktion, NAME was das Tile zeigt, VARIANTE nur bei echten Varianten.
#   Kein Level-Praefix — Farbvarianten kommen aus levels.json ("farben"-Block).
#   Themen-Kontext im Namen bei Bedarf: OBJ_BRAU_KEG_HOLZ, OBJ_VEG_GRAS.
#
# ---------------------------------------------------------------------------
# Cluster-Uebersicht
# ---------------------------------------------------------------------------
#
#  U+E000 – U+E03F  (  64)  HUB      Hub-Objekte, Story-Tiles, Einmaliges
#  U+E040 – U+E07F  (  64)  BODEN    Bodentypen (begehbar)
#  U+E080 – U+E0BF  (  64)  WAND     Wandtypen (inkl. Fenster, Tueren, Gitter)
#  U+E0C0 – U+E1BF  ( 256)  INTER    Interaktive Karten-Objekte
#  U+E1C0 – U+E2BF  ( 256)  OBJ      Nicht-interaktive Karten-Objekte
#  U+E2C0 – U+E33F  ( 128)  GEGNER   Gegner-Sprites
#  U+E340 – U+E3BF  ( 128)  ITEM     Item-Sprites
#  U+E3C0 – U+E3DF  (  32)  UI       Interface-Elemente
#  U+E3E0 – U+F8FF         Reserviert
#
# ---------------------------------------------------------------------------
# HUB  U+E000 – U+E03F
# ---------------------------------------------------------------------------

HUB_BRAUKESSEL = "\uE000"   # Hub-Ausgang ins Dungeon
HUB_NINKASI = "\uE001"      # Spieler-Sprite (ersetzt "@")

# ---------------------------------------------------------------------------
# BODEN  U+E040 – U+E07F
# ---------------------------------------------------------------------------

BODEN_FLIESSE = "\uE040"    # Gefliester Boden (Gewaechshaus, Innenraum)

# ---------------------------------------------------------------------------
# WAND  U+E080 – U+E0BF
# ---------------------------------------------------------------------------

WAND_FENSTER = "\uE080"     # Wandkachel mit Fensterausschnitt
WAND_GITTER  = "\uE081"     # Wandkachel mit Fenstergitter

# ---------------------------------------------------------------------------
# INTER  U+E0C0 – U+E1BF
# ---------------------------------------------------------------------------

INTER_PFLANZE = "\uE0C0"    # Interaktive Pflanze (Pflanzenzuechtung)

# ---------------------------------------------------------------------------
# OBJ  U+E1C0 – U+E2BF
# ---------------------------------------------------------------------------

OBJ_VEG_GRAS = "\uE1C0"    # Gras-Block (dekorativ/blockierend, Aussen-Level)

# ---------------------------------------------------------------------------
# GEGNER  U+E2C0 – U+E33F
# ---------------------------------------------------------------------------

GEGNER_SCHLEIM_GESICHT = "\uE2C0"   # Gaerkeller-Schimmel

GEGNER_LEBENSMITTELKONTROLLEUR  = "\uE2C1"  # Lebensmittelkontrolleur

# ---------------------------------------------------------------------------
# ITEM  U+E340 – U+E3BF
# ---------------------------------------------------------------------------

# (leer)

# ---------------------------------------------------------------------------
# UI  U+E3C0 – U+E3DF
# ---------------------------------------------------------------------------

# (leer)

# ---------------------------------------------------------------------------
# Namens-Lookup: symbolischer Name → Zeichen (fuer levels.json u.a. JSON-Daten)
# ---------------------------------------------------------------------------

# Tiles die wie Waende behandelt werden (blockieren Bewegung + FOV)
WAND_TILES = {WAND_FENSTER, WAND_GITTER}

TILE_NAMEN = {
    "HUB_BRAUKESSEL": HUB_BRAUKESSEL,
    "HUB_NINKASI":    HUB_NINKASI,
    "BODEN_FLIESSE":  BODEN_FLIESSE,
    "WAND_FENSTER":   WAND_FENSTER,
    "WAND_GITTER":    WAND_GITTER,
    "INTER_PFLANZE":  INTER_PFLANZE,
    "OBJ_VEG_GRAS":            OBJ_VEG_GRAS,
    "GEGNER_SCHLEIM_GESICHT":           GEGNER_SCHLEIM_GESICHT,
    "GEGNER_LEBENSMITTELKONTROLLEUR":   GEGNER_LEBENSMITTELKONTROLLEUR,
}

# ---------------------------------------------------------------------------
# Wird von main.py gelesen — ein Eintrag pro eigenem Tile mit PNG-Datei.
# ---------------------------------------------------------------------------

TILE_DATEIEN = {
    ord(HUB_BRAUKESSEL): "assets/tiles/hub/hub_braukessel.png",
    ord(HUB_NINKASI):    "assets/tiles/hub/hub_ninkasi.png",
    ord(BODEN_FLIESSE):  "assets/tiles/boden/boden_fliesse.png",
    ord(WAND_FENSTER):   "assets/tiles/wand/wand_fenster.png",
    ord(WAND_GITTER):    "assets/tiles/wand/wand_gitter.png",
    ord(INTER_PFLANZE):  "assets/tiles/inter/inter_pflanze.png",
    ord(OBJ_VEG_GRAS):            "assets/tiles/obj/obj_veg_gras.png",
    ord(GEGNER_SCHLEIM_GESICHT):          "assets/tiles/gegner/schleim-gesicht.png",
    ord(GEGNER_LEBENSMITTELKONTROLLEUR):  "assets/tiles/gegner/lebensmittelkontrolleur.png",
}
