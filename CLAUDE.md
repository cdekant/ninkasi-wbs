# Battle Ninkasi  RPG im Terminal

## Projekt

- Solo-Rollenspiel im Terminal
- Roguelite (Tod = zurück zum Level-Anfang, nicht zum Spielanfang)
- Nicht-kommerziell

## Spieldesign

### Konzept
Der Spieler kämpft sich durch alle Stufen der Bierherstellung — von der Aussaat
des Getreides bis zum Verkauf an den Kunden. Jede Stufe ist ein eigenes Level
mit zufälliger Karte. Zentrales Ziel: das Bier sauber brauen und zum Kunden
bringen.

### Ton
Humorvoll, sarkastisch, schwarz.

### Level (Braukette)
1. Aussaat
2. Ernte
3. Getreidelager
3. Mälzen
3. Schroten
4. Maischen
5. Läutern
6. Kochen / Hopfengabe
6. Whirlpool
7. Gärung
8. Reifung
9. Abfüllung
10. Verkauf (Endboss)

### Gegner
Vielfältig je nach Level — z.B. Insekten/Vögel (Aussaat), Bakterien/Wildhefen
(Gärung), Gesundheitsinspektor/Konkurrenz (Verkauf). Kein Gegner-Typ ist auf ein
Level beschränkt.

### Kampf
- Rundenbasiert (klassisch)
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
├── main.py              # Einstiegspunkt, startet das Spiel
├── game.py              # Hauptspielschleife
├── data/                # Alle Spieldaten als JSON
│   ├── skills.json      # Skill-Definitionen (12 Skills, 6 Stufen je)
│   ├── enemies.json     # (geplant)
│   ├── weapons.json     # (geplant)
│   ├── items.json       # (geplant)
│   └── characters.json  # (geplant)
├── saves/               # Spielstände
│   └── savegame.json
├── src/                 # Gesamter Spielcode
│   ├── entities/        # Spieler, Gegner, Items
│   │   └── player.py    # Spieler-Klasse mit EP + Skill-Stufen
│   ├── map/             # Kartengenerierung, Kacheltypen
│   ├── systems/         # Kampf, Inventar, Sichtfeld
│   │   ├── skills.py    # Skill-Logik (laden, prüfen, kaufen)
│   │   ├── menus.py     # Menue-Registry + State (verfügbar je Modus)
│   │   └── speichern.py # Speichern/Laden + Tod-Reset
│   └── ui/              # Darstellung, HUD
│       └── menu_anzeige.py  # TAB-Menue-Overlay (Vollbild)
└── assets/              # Schriftarten für tcod (tile fonts)
```

## Entwickler

- Keinerlei Programmiererfahrung — Erklärungen und Code so einfach wie möglich halten
- Ausnahme: Klare Vorteile für zukünftige Erweiterungen (insbesondere Modularisierbarkeit/Portierbarkeit) können die Regel "möglichst einfacher Code" überstimmen — dann aber mit Erklärung warum.

## Dokumentation

**Pflicht:** Erst wenn eine Aufgabe vollständig abgeschlossen ist, @CLAUDE.md, @TODO.md, @README.md, @HANDBUCH.md und @VERSION einlesen, auf Konsistenz prüfen und bei Bedarf nachziehen. Während der Aufgabe diese Dateien nicht laden.
