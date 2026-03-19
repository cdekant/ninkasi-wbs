# Battle Ninkasi  RPG im Terminal

## Projekt

- Solo-Rollenspiel im Terminal
- Roguelite (Tod = zurück zum Level-Anfang, nicht zum Spielanfang)
- privates, nicht-kommerzielles Projekt

## Spieldesign

### Konzept

Der Spieler kämpft sich durch alle Stufen der Bierherstellung — von der Aussaat des Getreides bis zum Verkauf an den Kunden. Jede Stufe ist ein eigenes Level mit zufälliger Karte.

Der Spieler steuert Ninkasi, die frühgeschichtliche mesopotamische Göttin des Bierbrauens, die als Rachegöttin wiedererstanden ist, um die Welt vom "Dämon der Abstinenz", dem "Prohibitus" und seine dunklen Adepti Lobbyisti, gegen Veganer und Zölikultisten, intelligente Schleime, Schädlinge, Lebensmittelkontrolleure, schlitzohrige Landwirte, Gastronomen anzutreten und den Menschen die Drinkability zurückzubringen.

### Ton

Humorvoll, sarkastisch, schwarz, respektlos, blutig, eklig, mikrobiologisch-schleimig.

### Level (Braukette)

Durchgehendes Thema für geheime Level?

1. Pflanzenzüchtung
1. Aussaat
2. Ernte
3. Getreidelager
3. Mälzen
3. Reinigen
3. Schroten (geheimes Level: Schrotmühle)
4. Maischen (geheimes Level: Sauergut)
5. Läutern (geheimes Level: Maischefiltern)
6. Kochen / Hopfengabe
6. Whirlpool (geheimes Level: Bier-Rückgewinnung)
7. Gärung (geheimes Level: Hefe-Propagation)
8. Reifung
9. Abfüllung
10. Verkauf (Endboss)

### Gegner

Vielfältig je nach Level — z.B. Insekten/Vögel (Aussaat), Bakterien/Wildhefen
(Gärung), Gesundheitsinspektor/Konkurrenz (Verkauf). Kein Gegner-Typ ist auf ein
Level beschränkt.

### Kampf

- Rundenbasiert (klassisch)
- taktisch?
- Rätselelemente je nach Level möglich

### Progression
- **Tod:** Neustart am Anfang des aktuellen Levels
- **Permanente Verbesserungen:** Skills bleiben erhalten + Währung zum Freischalten
- **Skill-Entwicklung:** Fähigkeiten verbessern sich durch Wiederholung
- **Charaktererstellung:** Flexible Archetypen statt starrer Klassen

### Darstellung
- Aktuell: Cheepicus 16×16 Tileset (CP437) + custom Tiles via Unicode Private Use Area (U+E000+)
- Custom Tiles: einzelne 16×16 PNGs, definiert in `src/tiles.py`, injiziert via `tileset.set_tile()`
- Startbildschirm: 120×144 RGBA-Bild via Halbblock-Technik (▀, fg=oben, bg=unten) — doppelte Auflösung
- Fenster: borderless (SDL_WINDOW_BORDERLESS), 120×72 Kacheln à 16×16 px
- Weiterer Wechsel auf vollständiges Tile-Set möglich — Darstellung ist vollständig in `src/ui/` isoliert

### Karten-System (Design-Entscheidungen)

- **Zonen-basiert:** Kein Scrolling; jede Zone passt ins Terminal-Fenster
- **Hybrid-Struktur:** Baum-Graph + zufällige Querverbindungen
- **Neu generiert:** Bei Tod UND Level-Wechsel (Seed wird nicht gespeichert)
- **Zone-Graph:** Ein Pflicht-Ausgang (tief im Baum), zufällige Bonus/Geheim-Ausgänge
- **Algorithmen:** BSP für Gebäude-Level, Noise für Außen-Level
- **Level-Grammatik:** Jedes Level definiert Algorithmus, Kacheln, Objekte, Gegner-Pool in `data/levels.json`
- **Gegner-Pool:** Gewichtete Häufigkeit + Stärke-Skalierung pro Level (0.0–1.0)
- **Geheim-Level:** Erben Grammatik vom regulären Level (`"basis": "..."`) mit überschriebenen Parametern (kleiner, höhere Loot-Chance)
- **Mini-Map:** Fog of War (nur Erkundetes sichtbar), aktuelle Zone hervorgehoben, Ausgänge erst bei Entdeckung, alles neu nach Tod
- **Items:** Eigene `data/items.json`, Pflichtfeld `kategorie` (verbrauchbar, waffe, ruestung, material, quest)
- **Objekte vs. Items:** Objekte bleiben auf der Karte (Gärtank, Hecke); Items wandern ins Inventar; Objekte haben `loot_pool`

### Hub-System

- **Hub** (`src/map/hub.py`): kreisrunder Raum (Radius 7) um die Bildschirmmitte; eigener FOV/Fog-of-War-Zustand
- **Braukessel** (U+E000, `assets/tiles/braukessel.png`): Ausgang vom Hub ins Dungeon; Betreten startet neuen Run
- **Dungeon-Ausgang** (`<`, hellblau): Liegt am vom Spieler-Spawn am weitesten entfernten Bodentile; Betreten kehrt zum Hub zurück
- **Modus vs. Ort:** `modus` = "hub"/"kampf"/"tod" (Spielzustand); `ort` = "pilsstube"/"dungeon" (wo man sich befindet)
- **TAB-Menü** nur im Hub verfügbar (`ort == "pilsstube"`), im Dungeon gesperrt

## Technologie

- Windows 11
- Python 3.13.9 (Befehl: `python`)
- pip (vorhanden)
- Terminal-Bibliothek: `tcod`
- Code-Editor: Notepad++
- Git (vorhanden)
- Speicherformat: JSON (Spielstand); Umstieg auf SQLite möglich ohne Änderung an der Spiellogik
- Spieldaten (Gegner, Waffen, Items, Charaktere usw.) liegen als JSON-Dateien unter `data/` — Erweiterungen ohne Code-Änderungen möglich

## Projektstruktur

```
bn/
├── main.py              # Einstiegspunkt: Tileset laden (Cheepicus + custom tiles), Fenster öffnen
├── config.py            # Zentrale Anzeige-Konfiguration: BREITE, HOEHE, KACHEL_PX, SDL_FLAGS
├── game.py              # Hauptspielschleife (Bewegung, Kampf, Spawn, Rendering, Hub, Tod-Screen)
├── data/                # Alle Spieldaten als JSON
│   ├── skills.json      # Skill-Definitionen (Skelett — offen)
│   ├── levels.json      # Level-Grammatiken (Algorithmus, Kacheln, Objekte, Gegner-Pool)
│   ├── effekttypen.json # Zentrales Register aller Effekt-Typen (inkl. DoT, Debuffs)
│   ├── enemies.json     # Gegner-Typ-Definitionen (einzel/schwarm, Angriffe, Resistenzen)
│   ├── weapons.json     # (geplant)
│   ├── items.json       # (geplant)
│   └── characters.json  # (geplant)
├── saves/               # Spielstände
│   └── savegame.json
├── src/                 # Gesamter Spielcode
│   ├── tiles.py         # Custom-Tile-Definitionen: Unicode-Platzhalter (U+E000+) + Dateipfade
│   ├── entities/        # Spieler, Gegner, Items
│   │   ├── entitaet.py  # Basis-Klasse: hp/hp_max, pp, verteidigung, resistenzen, angriffe, lebt
│   │   ├── player.py    # Spieler(Entitaet): EP, Skills, lp/lp_max-Aliases, Inventar (geplant)
│   │   └── gegner.py    # Gegner(Entitaet): typen_laden(), aus_typ() mit Staerke-Skalierung
│   ├── map/             # Kartengenerierung
│   │   ├── bsp.py       # BSP-Generator (Raeume + Korridore + Objekte)
│   │   └── hub.py       # Hub-Generator: kreisrunder Raum (Radius 7), Braukessel-Ausgang
│   ├── systems/         # Kampf, Inventar, Sichtfeld
│   │   ├── kampf.py     # Kampfsystem: KampfZustand, runde_ausfuehren, Status-Effekte
│   │   ├── ki.py        # Gegner-KI: ki_tick, verhalten (statisch/territorial/verfolgen/flucht)
│   │   ├── sichtfeld.py # FOV: baue_transparenz, berechne_fov (tcod), Fog of War
│   │   ├── skills.py    # Skill-Logik (laden, prüfen, kaufen)
│   │   ├── menus.py     # Menue-Registry + State (verfügbar je ort: pilsstube/dungeon)
│   │   └── speichern.py # Speichern/Laden + Tod-Reset (setzt LP/PP zurueck)
│   └── ui/              # Darstellung, HUD
│       └── menu_anzeige.py  # TAB-Menue-Overlay (Vollbild)
└── assets/              # Tilesets und Bilder für tcod
    ├── Cheepicus_16x16.png        # Aktives Tileset (16×16 px, quadratisch, CP437)
    ├── ninkasi_brutality_120x144.png  # Startbildschirm-Hintergrundbild (Halbblock-Rendering)
    └── tiles/
        └── braukessel.png         # Custom-Tile (16×16 px, U+E000) — Hub-Ausgang ins Dungeon
```

## Entwickler

- Keinerlei Programmiererfahrung — Erklärungen und Code so einfach wie möglich halten
- Ausnahme: Klare Vorteile für zukünftige Erweiterungen (insbesondere Modularisierbarkeit/Portierbarkeit) können die Regel "möglichst einfacher Code" überstimmen — dann aber mit Erklärung warum.

## Dokumentation

**Pflicht:** Erst wenn eine Aufgabe vollständig abgeschlossen ist, @CLAUDE.md, @TODO.md, @README.md, @HANDBUCH.md und @VERSION einlesen, auf Konsistenz prüfen und bei Bedarf nachziehen. Während der Aufgabe diese Dateien nicht laden.
