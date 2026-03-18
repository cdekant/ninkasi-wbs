# Battle Ninkasi  RPG im Terminal

## Projekt

- Solo-Rollenspiel im Terminal
- Roguelite (Tod = zurück zum Level-Anfang, nicht zum Spielanfang)
- privates, nicht-kommerzielles Projekt

## Spieldesign

### Konzept

Der Spieler kämpft sich durch alle Stufen der Bierherstellung — von der Aussaat
des Getreides bis zum Verkauf an den Kunden. Jede Stufe ist ein eigenes Level
mit zufälliger Karte.

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
- Start: ASCII
- Wechsel auf Tiles später möglich — Darstellung ist vollständig in `src/ui/`
  isoliert, Umbau betrifft nur diese eine Schicht

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
├── main.py              # Einstiegspunkt, startet das Spiel (100×56, Cheepicus 16×16)
├── game.py              # Hauptspielschleife (Bewegung, Kampf, Spawn, Rendering)
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
│   ├── entities/        # Spieler, Gegner, Items
│   │   ├── player.py    # Spieler-Klasse: EP, Skills, LP/PP, Verteidigung
│   │   └── gegner.py    # Gegner-Klasse: typen_laden(), aus_typ() mit Staerke-Skalierung
│   ├── map/             # Kartengenerierung
│   │   └── bsp.py       # BSP-Generator (Raeume + Korridore + Objekte)
│   ├── systems/         # Kampf, Inventar, Sichtfeld
│   │   ├── kampf.py     # Kampfsystem: KampfZustand, runde_ausfuehren, Status-Effekte
│   │   ├── skills.py    # Skill-Logik (laden, prüfen, kaufen)
│   │   ├── menus.py     # Menue-Registry + State (verfügbar je Modus)
│   │   └── speichern.py # Speichern/Laden + Tod-Reset (setzt LP/PP zurueck)
│   └── ui/              # Darstellung, HUD
│       └── menu_anzeige.py  # TAB-Menue-Overlay (Vollbild)
└── assets/              # Tilesets für tcod
    ├── Cheepicus_16x16.png   # Aktives Tileset (16×16 px, quadratisch, CP437)
    └── IBMPlexMono-Regular.ttf  # Alt (nicht mehr verwendet)
```

## Entwickler

- Keinerlei Programmiererfahrung — Erklärungen und Code so einfach wie möglich halten
- Ausnahme: Klare Vorteile für zukünftige Erweiterungen (insbesondere Modularisierbarkeit/Portierbarkeit) können die Regel "möglichst einfacher Code" überstimmen — dann aber mit Erklärung warum.

## Dokumentation

**Pflicht:** Erst wenn eine Aufgabe vollständig abgeschlossen ist, @CLAUDE.md, @TODO.md, @README.md, @HANDBUCH.md und @VERSION einlesen, auf Konsistenz prüfen und bei Bedarf nachziehen. Während der Aufgabe diese Dateien nicht laden.
