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
# UI-Layout  (alle Masse in Kacheln; Summe = BREITE = 120, HOEHE = 67)
# -----------------------------------------------------------------------
#
#  Zeile  0–1  : Statuszeile  (LP / PP / MP / EP)          2 Zeilen
#  Zeile  2–65 : Seitenleisten (Log links, Gegner/Aktionen rechts)
#  Zeile  2–60 : Spielkarte (Mitte)                        59 Zeilen  = KARTE_HOEHE
#  Zeile 66    : Kontextsensitive Shortcuts                 1 Zeile
#
#  Spalten  0–25  : Log-Panel       (PANEL_BREITE)
#  Spalten 26–93  : Karte           (KARTE_X0 .. KARTE_X0+KARTE_BREITE-1)
#  Spalten 94–119 : Kontext-Panel   (PANEL_BREITE)
# -----------------------------------------------------------------------
PANEL_BREITE       = 26    # Breite jeder Seitenleiste (links + rechts)
KARTE_X0           = 26    # x-Startposition der Karte (= PANEL_BREITE)
KARTE_BREITE       = 68    # Kartenbreite (BREITE - 2 * PANEL_BREITE)
KARTE_Y0           =  2    # Karte beginnt in Zeile 2
KARTE_HOEHE        = 59    # Karte: Zeilen 2–60
SHORTCUT_Y         = 66    # Shortcut-Zeile

# Gegner-HP-Schwellwerte und Farben fuer Symbol-Faerbung
GEGNER_HP_ANGESCHLAGEN_PCT = 60            # unter 60 % HP: gelb
GEGNER_HP_VERWUNDET_PCT    = 30            # unter 30 % HP: rot
GEGNER_FARBE_VOLL          = (200,  80,  80)   # volle HP
GEGNER_FARBE_ANGESCHLAGEN  = (220, 180,  40)   # angeschlagen (< 60 %)
GEGNER_FARBE_VERWUNDET     = (255,  40,  40)   # schwer verwundet (< 30 %)

# -----------------------------------------------------------------------
# Charaktererstellung
# -----------------------------------------------------------------------
EIGENSCHAFT_START_PUNKTE = 10   # Punkte zum Verteilen bei Spielbeginn
EIGENSCHAFT_START_MAX    =  5   # Max Punkte pro Eigenschaft bei Erstellung

# EP-Kostenreduktion durch Eigenschaften (Soft-Cap-Stufen)
# Format: {"bis_punkt": int, "pct_pro_punkt": float}
# Die letzte Stufe gilt fuer alle Punkte darueber.
EIGENSCHAFT_REDUKTION_PRIMAER = [
    {"bis_punkt":  5, "pct_pro_punkt": 7.0},
    {"bis_punkt": 10, "pct_pro_punkt": 3.5},
    {"bis_punkt": 99, "pct_pro_punkt": 1.75},
]
EIGENSCHAFT_REDUKTION_SEKUNDAER = [
    {"bis_punkt":  5, "pct_pro_punkt": 3.0},
    {"bis_punkt": 10, "pct_pro_punkt": 1.5},
    {"bis_punkt": 99, "pct_pro_punkt": 0.75},
]
EIGENSCHAFT_REDUKTION_MAX = 0.80   # Nie mehr als 80 % Reduktion

# ---------------------------------------------------------------------------
# Fernkampf
# ---------------------------------------------------------------------------
PP_FERNKAMPF_KOSTEN     =  5   # PP-Kosten pro Schuss
PP_FERNKAMPF_SCHADEN    = 10   # Rohschaden
PP_FERNKAMPF_REICHWEITE =  6   # Max. Reichweite in Kacheln
MP_FERNKAMPF_KOSTEN     =  5
MP_FERNKAMPF_SCHADEN    = 12
MP_FERNKAMPF_REICHWEITE =  8
