# Zentrale Konfiguration — Fenstergröße und Darstellung
#
# Fensterpixel = BREITE × KACHEL_PX  bzw.  HOEHE × KACHEL_PX
# Beispiele:
#   1920×1080 bei 16px → BREITE=120, HOEHE=67  (67×16=1072, 8px Rand unten)
#   1280×720  bei 16px → BREITE=80,  HOEHE=45
#   800×600   bei 16px → BREITE=50,  HOEHE=37

BREITE    = 120   # Kachelspalten
HOEHE     = 72    # Kachelzeilen
KACHEL_PX = 16    # Kachelgröße in Pixel (Tileset muss passen)

# SDL_WINDOW_BORDERLESS: kein Titelbalken, keine Fensterränder.
# Auf None setzen für normales Fenster mit Titelleiste.
SDL_FLAGS = 0x00000010
