# TODO

## Abgeschlossen

- [x] Grundgeruest: tcod-Fenster, Karte, Spielerbewegung
- [x] Skill- & Progressionssystem
  - [x] `data/skills.json` (12 Skills, 6 Stufen, Brauerstern-Lore)
  - [x] `src/systems/skills.py` (laden, pruefen, kaufen)
  - [x] `src/entities/player.py` (EP, Skills, Serialisierung)
  - [x] `src/systems/speichern.py` (Speichern/Laden/Tod-Reset)
  - [x] `game.py`: EP-Tick pro Zug
  - [x] `HANDBUCH.md`: Skill-Kapitel + Brauerstern-Lore
- [x] TAB-Menue-System mit State-Konzept
  - [x] `src/systems/menus.py` (Registry, Modi, Navigation)
  - [x] `src/ui/menu_anzeige.py` (Vollbild-Overlay, Tab-Leiste)
  - [x] `game.py`: TAB oeffnet Menue, ESC schliesst, UP/DOWN navigiert, ENTER kauft
  - [x] HUD: EP-Anzeige + Steuerungshinweis

## Offen

### Naechste Schritte (Prioritaet hoch)

- [ ] Speichern/Laden in die Spielschleife integrieren
- [ ] Modus "run" aktivieren beim Level-Start (Hub-Menues sperren)

### Mittelfristig

- [ ] Kampfsystem (rundenbasiert)
- [ ] Erste Gegner (`data/enemies.json`)
- [ ] Inventar-System (`data/items.json`, `data/weapons.json`)
- [ ] Kartengenerierung mit Seed
- [ ] Sichtfeld (FOV)

### Langfristig

- [ ] Alle Level der Braukette (Aussaat bis Verkauf)
- [ ] Charaktererstellung / Archetypen
- [ ] Tile-Grafikschicht (nur `src/ui/` betroffen)
- [ ] Musik/Sound
