# Zentrale Konfiguration — Fenstergröße und Darstellung
#
# Fensterpixel = BREITE × KACHEL_PX  bzw.  HOEHE × KACHEL_PX
# Zielauflösung: 1920×1080 (borderless, kein Titelbalken)
#   16px-Tiles: 120×67 = 1920×1072  (8 px schwarzer Streifen unten — unvermeidbar)
#   32px-Tiles: 60×33  = 1920×1056  (für spätere Skalierung, 24 px Streifen unten)
#
# Weitere Auflösungen bei 16px:
#   1280×720  → BREITE=80,  HOEHE=45
#   800×600   → BREITE=50,  HOEHE=37

BREITE    = 120   # Kachelspalten  →  120 × 16 = 1920 px
HOEHE     =  67   # Kachelzeilen   →   67 × 16 = 1072 px  (8 px Streifen unten bei 1080p)
KACHEL_PX =  16   # Kachelgröße in Pixel (Tileset muss passen)

# SDL_WINDOW_BORDERLESS: kein Titelbalken, keine Fensterränder.
# Auf None setzen für normales Fenster mit Titelleiste.
SDL_FLAGS = 0x00000010   # borderless  (normales Fenster: 0)

# -----------------------------------------------------------------------
# UI-Layout  (alle Masse in Kacheln; Summe = HOEHE = 67)
# -----------------------------------------------------------------------
#
#  Zeile  0–1  : Statuszeile  (LP / PP / MP / EP)          2 Zeilen
#  Zeile  2–60 : Spielkarte                                59 Zeilen  = KARTE_HOEHE
#  Zeile 61–65 : Nachrichtenlog                             5 Zeilen  = LOG_HOEHE
#  Zeile 66    : Kontextsensitive Shortcuts                 1 Zeile
#  -----------------------------------------------------------------------
KARTE_Y0           =  2    # Karte beginnt in Zeile 2
KARTE_HOEHE        = 59    # Karte: Zeilen 2–60
LOG_Y0             = 61    # Nachrichtenlog
LOG_HOEHE          =  5
SHORTCUT_Y         = 66    # Shortcut-Zeile

# Schwebendes Kampffenster (Konsolen-Koordinaten, innerhalb der Karte)
KAMPF_FENSTER_X      = 20
KAMPF_FENSTER_Y      = 21
KAMPF_FENSTER_BREITE = 80
KAMPF_FENSTER_HOEHE  = 20
