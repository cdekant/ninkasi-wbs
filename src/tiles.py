# Tile-Konstanten und zugehoerige PNG-Dateien.
# Unicode Private Use Area U+E000–U+F8FF (6400 Slots) — kein Konflikt mit Cheepicus/CP437.
#
# Neues Tile hinzufuegen: Konstante in passendem Cluster + Eintrag in TILE_DATEIEN.
#
# ---------------------------------------------------------------------------
# Cluster-Uebersicht
# ---------------------------------------------------------------------------
#
#  U+E000 – U+E03F  (  64)  SPEZIAL       Hub, Story-Objekte, einmalige Tiles
#  U+E040 – U+E13F  ( 256)  UMWELT        Pflanzen, Getreide, Terrain, Natur
#  U+E140 – U+E23F  ( 256)  BRAUEREI      Tanks, Kessel, Rohre, Maschinen
#  U+E240 – U+E33F  ( 256)  ARCHITEKTUR   Wand-/Boden-Varianten, Tueren, Fenster
#  U+E340 – U+E3BF  ( 128)  GEGNER        Custom-Sprites fuer Gegner-Typen
#  U+E3C0 – U+E43F  ( 128)  ITEMS         Custom-Sprites fuer Items und Loot
#  U+E440 – U+E45F  (  32)  UI            Balken, Rahmen, Interface-Elemente
#  U+E460 – U+F8FF  (frei)  Reserviert / zukuenftige Erweiterungen
#
# ---------------------------------------------------------------------------
# SPEZIAL  U+E000 – U+E03F
# ---------------------------------------------------------------------------

BRAUKESSEL = "\uE000"   # Hub-Ausgang ins Dungeon

# ---------------------------------------------------------------------------
# UMWELT  U+E040 – U+E13F
# ---------------------------------------------------------------------------

PFLANZE    = "\uE040"   # Interaktive Pflanze (Pflanzenzuechtung)

# ---------------------------------------------------------------------------
# BRAUEREI  U+E140 – U+E23F
# ---------------------------------------------------------------------------

# (leer — erste Tiles folgen mit Brauerei-Levels)

# ---------------------------------------------------------------------------
# ARCHITEKTUR  U+E240 – U+E33F
# ---------------------------------------------------------------------------

# (leer)

# ---------------------------------------------------------------------------
# GEGNER  U+E340 – U+E3BF
# ---------------------------------------------------------------------------

# (leer)

# ---------------------------------------------------------------------------
# ITEMS  U+E3C0 – U+E43F
# ---------------------------------------------------------------------------

# (leer)

# ---------------------------------------------------------------------------
# UI  U+E440 – U+E45F
# ---------------------------------------------------------------------------

# (leer)

# ---------------------------------------------------------------------------
# Namens-Lookup: symbolischer Name → Zeichen (fuer levels.json u.a. JSON-Daten)
# ---------------------------------------------------------------------------

TILE_NAMEN = {
    "BRAUKESSEL": BRAUKESSEL,
    "PFLANZE":    PFLANZE,
}

# ---------------------------------------------------------------------------
# Wird von main.py gelesen — ein Eintrag pro eigenem Tile mit PNG-Datei.
# ---------------------------------------------------------------------------

TILE_DATEIEN = {
    ord(BRAUKESSEL): "assets/tiles/braukessel.png",
    ord(PFLANZE):    "assets/tiles/pflanze.png",
}
