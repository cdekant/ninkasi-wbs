# TODO

## Abgeschlossen

- [x] Grundgeruest: tcod-Fenster, Karte, Spielerbewegung
- [x] Skill- & Progressionssystem
  - [x] `data/skills.json` (Skelett angelegt, konkreter Inhalt offen)
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
- [x] BSP-Kartengenerator (Demo: Gaerkeller)
  - [x] `src/map/bsp.py` (BSP-Baum, Raeume, Korridore, Objekte)
  - [x] `data/levels.json` (Level-Grammatik: Gaerkeller, Gegner-Pool)
  - [x] `main.py`: Tileset auf Cheepicus_16x16 (quadratisch), Konsole 100x56
  - [x] `game.py`: hardcodierte Karte durch generierten Gaerkeller ersetzt
- [x] Gegner-Entitaeten
  - [x] `data/enemies.json` (wildhefe/schwarm-Skelett, gaerkeller_schimmel, lebensmittelkontrolleur)
  - [x] `data/effekttypen.json`: psi_malus_pct, dot_biologisch, dot_chemisch, dauer_moeglich-Flag
  - [x] `src/entities/gegner.py` (typen_laden, Gegner-Klasse, aus_typ mit Staerke-Skalierung)
- [x] Spieler-Kampfwerte
  - [x] `src/entities/player.py`: lp/lp_max, pp/pp_max, verteidigung, basis_schaden
  - [x] `src/systems/speichern.py`: tod_reset setzt LP/PP zurueck; lp/pp aus STANDARD_AKTUELL entfernt
- [x] Kampfsystem
  - [x] `src/systems/kampf.py`: KampfZustand, runde_ausfuehren, Status-Effekte (DoT + Debuffs), Resistenzen, Regeneration, EP-Vergabe
- [x] Spielschleife mit Kampf
  - [x] `game.py`: Gegner-Spawn aus gegner_pool, Anlaufen startet Kampf, Kampf-Panel (HP-Balken, Log, Status), Tod-Reset + Level-Neustart

## Offen

### Naechste Schritte (Prioritaet hoch)

- [ ] Gegner-KI: Bewegung auf der Karte (auf Spieler zu)
- [ ] Sichtfeld / Fog of War (FOV)
- [ ] Speichern/Laden in die Spielschleife integrieren

### Mittelfristig

- [ ] Zonen-System (Zone-Graph, Hybrid-Struktur, Uebergaenge)
- [ ] Mini-Map (Fog of War, Zone-Graph-Anzeige)
- [ ] Inventar-System (`data/items.json`, `data/weapons.json`)
- [ ] Schwarm-Gegner (SchwarmGegner-Klasse, AoE-Logik)
- [ ] Noise-Generator fuer Aussen-Level (Aussaat, Ernte)

### Langfristig

- [ ] Alle Level der Braukette (Aussaat bis Verkauf) in `data/levels.json`
  - inkl. Geheim-Level (erben Grammatik via `"basis"`)
- [ ] Charaktererstellung / Archetypen
- [ ] Tile-Grafikschicht (nur `src/ui/` betroffen — Tileset-Tausch genuegt)
- [ ] Musik/Sound
