---
lang: 'de-DE'
---

# Battle Ninkasi — RPG im Terminal

## Projekt

- Solo-Roguelite im Terminal, privat, nicht-kommerziell
- Ansprache an den Projektleiter: Ninkasi
- Spielinhalt, Spielregeln, Lore: siehe `HANDBUCH.md`

## Technische Darstellung

- Cheepicus 16×16 Tileset (CP437) als Basis + eigene Tiles via `set_tile()` — so schnell es geht vollständig auf custom Tiles umstellen (Plan: `Plaene/2026-03-20_tileset-benennung-und-transition.md`)
- Custom Tiles: einzelne 16×16 PNGs unter `assets/tiles/<gruppe>/`, definiert in `src/tiles.py`, injiziert via `tileset.set_tile()`
- **`src/tiles.py` ist die einzige Quelle der Wahrheit für Tile-Codepoints und -Namen.** JSON-Dateien verwenden symbolische Namen (z.B. `"INTER_PFLANZE"`), die von `karte.py` aufgelöst werden — nie rohe Codepoints in JSON schreiben.
- Benennungsschema: `GRUPPE_NAME[_VARIANTE]` — Details, PUA-Cluster und aktuelles Tile-Register in `Doc/Design-Tiles.md`
- **Benennungsprüfung:** Bei jeder Tile-bezogenen Aufgabe (neue Tiles, Umbenennung, JSON-Schlüssel, PNG-Pfade, Gegner-IDs) aktiv auf Inkonsistenzen mit dem Schema hinweisen — auch unaufgefordert.
- Startbildschirm: 120×144 RGBA-Bild via Halbblock-Technik (▀, fg=oben, bg=unten)
- Fenster: borderless (SDL_WINDOW_BORDERLESS), 120×67 Kacheln à 16×16 px = 1920×1072 px
- UI-Layout: Statuszeile (Zeilen 0–1), Karte (Zeilen 2–60, 59 Zeilen), Nachrichtenlog (Zeilen 61–65), Shortcut-Zeile (Zeile 66)
- Schwebendes Kampffenster: 80×20 Kacheln, Konsolen-Position x=20/y=21, überlagert die Karte
- Darstellung vollständig in `src/ui/` isoliert — Tileset-Tausch möglich ohne Spiellogik-Änderung

## Karten-System

- **Zonen-basiert:** Kein Scrolling; jede Zone passt ins Terminal-Fenster
- **Hybrid-Struktur:** Baum-Graph + zufällige Querverbindungen
- **Neu generiert:** Bei Tod UND Level-Wechsel (Seed wird nicht gespeichert)
- **Zone-Graph:** Ein Pflicht-Ausgang (tief im Baum), zufällige Bonus/Geheim-Ausgänge
- **Algorithmen:** BSP (Gebäude-Level), Raster (Innenraum/Gewächshaus), Noise (Außen-Level — geplant)
- **Level-Grammatik:** `data/levels.json` — Algorithmus, Kacheln, Objekte, Gegner-Pool je Level
- **Gegner-Pool:** Gewichtete Häufigkeit + Stärke-Skalierung pro Level (0.0–1.0)
- **Geheim-Level:** `"basis": "<level_name>"` erbt Grammatik, überschreibt einzelne Parameter
- **Items:** `data/items.json`, Pflichtfeld `kategorie` (verbrauchbar, waffe, ruestung, material, quest)
- **Objekte vs. Items:** Objekte bleiben auf der Karte (Gärtank, Hecke); Items wandern ins Inventar; Objekte haben `loot_pool`

## Hub-System

- `src/map/hub.py`: kreisrunder Raum (Radius 7) um die Bildschirmmitte; eigener FOV/Fog-of-War-Zustand
- **Braukessel** (`HUB_BRAUKESSEL`, U+E000, `assets/tiles/hub/hub_braukessel.png`): Ausgang vom Hub ins Dungeon
- **Dungeon-Ausgang** (`<`, hellblau): per BFS-Flood-Fill das erreichbare Bodentile am weitesten vom Spawn-Punkt
- `modus` = "hub"/"kampf"/"tod" (Spielzustand); `ort` = "pilsstube"/"dungeon" (Aufenthaltsort)
- TAB-Menü Skill-Baum nur im Hub (`ort == "pilsstube"`); Inventar in Hub, Dungeon und Kampf
- 15 Skill-Kategorien (Details in HANDBUCH.md)

## Technologie

- Windows 11, Python 3.13.9 (Befehl: `python`), tcod, Notepad++, Git
- Spieldaten unter `data/` als JSON — Erweiterungen ohne Code-Änderungen möglich
- Spielstand: `saves/savegame.json`; Umstieg auf SQLite möglich ohne Änderung der Spiellogik

## Projektstruktur

```
bn/
├── main.py              # Einstiegspunkt: Tileset laden (Cheepicus + custom tiles), Fenster öffnen
├── config.py            # Zentrale Anzeige-Konfiguration: BREITE, HOEHE, KACHEL_PX, SDL_FLAGS, UI-Layout-Konstanten
├── game.py              # Hauptspielschleife (Bewegung, Kampf, Spawn, Rendering, Hub, Tod-Screen)
├── data/                # Alle Spieldaten als JSON
│   ├── skills.json      # Skill-Definitionen (Skelett — offen)
│   ├── levels.json      # Level-Grammatiken (Algorithmus, Kacheln, Objekte, Gegner-Pool)
│   ├── effekttypen.json # Zentrales Register aller Effekt-Typen (inkl. DoT, Debuffs)
│   ├── enemies.json     # Gegner-Typ-Definitionen (einzel/schwarm, Angriffe, Resistenzen, loot_pool)
│   ├── items.json       # Item-Definitionen (verbrauchbar/waffe/schild/ruestung/material/quest; stapelbar, seltenheit, haltbarkeit_max)
│   ├── weapons.json     # (aufgegangen in items.json)
│   └── characters.json  # (geplant)
├── saves/               # Spielstände
│   └── savegame.json
├── src/                 # Gesamter Spielcode
│   ├── tiles.py         # Custom-Tile-Definitionen: Unicode-Platzhalter (U+E000+) + Dateipfade
│   ├── entities/        # Spieler, Gegner, Items
│   │   ├── entitaet.py  # Basis-Klasse: hp/hp_max, pp, mp, verteidigung, resistenzen, angriffe, lebt
│   │   ├── player.py    # Spieler(Entitaet): EP, Skills, lp/lp_max-Aliases, inventar, ausruestung
│   │   ├── gegner.py    # Gegner(Entitaet): typen_laden(), aus_typ() mit Staerke-Skalierung
│   │   └── item.py      # typen_laden() — laedt data/items.json
│   ├── map/             # Kartengenerierung
│   │   ├── karte.py     # Algorithmus-Dispatcher: waehlt bsp/raster anhand Grammatik; loest symbolische Tile-Namen auf
│   │   ├── bsp.py       # BSP-Generator (Raeume + Korridore + Objekte)
│   │   ├── raster.py    # Raster-Generator (N×M-Gitter, Korridorbreite, Objekt-Positionierung)
│   │   └── hub.py       # Hub-Generator: kreisrunder Raum (Radius 7), Braukessel-Ausgang
│   ├── systems/         # Kampf, Inventar, Sichtfeld
│   │   ├── kampf.py     # Kampfsystem: KampfZustand, runde_ausfuehren, Status-Effekte
│   │   ├── ki.py        # Gegner-KI: ki_tick, verhalten (statisch/territorial/verfolgen/flucht)
│   │   ├── sichtfeld.py # FOV: baue_transparenz, berechne_fov (tcod), Fog of War
│   │   ├── skills.py    # Skill-Logik (laden, prüfen, kaufen)
│   │   ├── inventar.py  # Inventar-Logik: hinzufuegen, entfernen, benutzen
│   │   ├── menus.py     # Menue-Registry + State (Skill-Baum: Hub; Inventar: Hub+Dungeon)
│   │   └── speichern.py # Speichern/Laden + Tod-Reset (setzt LP/PP zurueck); bodenloot in aktuell
│   └── ui/              # Darstellung, HUD
│       └── menu_anzeige.py  # TAB-Menue-Overlay (Vollbild)
└── assets/              # Tilesets und Bilder für tcod
    ├── Cheepicus_16x16.png        # Aktives Tileset (16×16 px, quadratisch, CP437)
    ├── ninkasi_brutality_120x144.png  # Startbildschirm-Hintergrundbild (Halbblock-Rendering)
    └── tiles/
        ├── hub/                   # HUB-Cluster  U+E000–U+E03F
        ├── boden/                 # BODEN-Cluster U+E040–U+E07F
        ├── wand/                  # WAND-Cluster  U+E080–U+E0BF
        ├── inter/                 # INTER-Cluster U+E0C0–U+E1BF
        ├── obj/                   # OBJ-Cluster   U+E1C0–U+E2BF
        ├── gegner/                # GEGNER-Cluster U+E2C0–U+E33F
        ├── item/                  # ITEM-Cluster  U+E340–U+E3BF
        └── ui/                    # UI-Cluster    U+E3C0–U+E3DF
        # Aktuelles Tile-Register: Doc/Design-Tiles.md
```

## Entwickler

- Keinerlei Programmiererfahrung — Erklärungen und Code so einfach wie möglich halten
- Ausnahme: Klare Vorteile für Modularisierbarkeit/Portierbarkeit können Einfachheit überstimmen — dann mit Erklärung warum.
- **Sprechende Namen:** Dateien, Funktionen, Variablen, Konstanten und JSON-Schlüssel immer so benennen, dass der Name ohne Kommentar verständlich ist. Lieber `schaden_pro_runde` als `dpr`, lieber `wand_fenster.png` als `w2.png`. Abkürzungen nur wenn allgemein bekannt (z.B. `hp`, `ui`, `fov`).

## Dokumentation

**Pflicht:** Erst wenn eine Aufgabe vollständig abgeschlossen ist, `CLAUDE.md`, `TODO.md`, `README.md`, `HANDBUCH.md` und `VERSION` einlesen, auf Konsistenz prüfen und bei Bedarf nachziehen. Während der Aufgabe diese Dateien nicht automatisch laden.

## Pläne

Implementierungspläne liegen unter `Plaene/` im Projektroot.
- Dateiname: `JJJJ-MM-TT_stichwort.md` (ISO-Datum vorangestellt)
- Nicht versioniert (in `.gitignore` eingetragen)
- Inhalt: Ziel, betroffene Dateien, Codebeispiele, offene Fragen
