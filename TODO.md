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
- [x] Sichtfeld / Fog of War
  - [x] `src/systems/sichtfeld.py`: baue_transparenz, berechne_fov (tcod, Radius 8), neues_erkundet, aktualisiere_erkundet
  - [x] `game.py`: FOV/ERKUNDET-Arrays, Neuberechnung nach jedem Zug, Rendering (sichtbar/erkundet/schwarz), Gegner nur im FOV sichtbar

## Offen

### Naechste Schritte (Prioritaet hoch)

- [x] Gegner-KI
  - [x] `data/enemies.json`: verhalten, sicht_radius, flucht_hp_pct, geschwindigkeit je Gegner
  - [x] `src/entities/gegner.py`: KI-Felder in __init__/aus_typ/als_dict/aus_dict; ki_zustand + bewegungs_zaehler als Laufzeitzustand
  - [x] `src/systems/ki.py`: ki_tick (statisch/territorial/verfolgen/flucht), geschwindigkeit-Akkumulation, flucht_hp_pct-Override, _schritt_zu/_schritt_weg
  - [x] `game.py`: ki_tick nach jedem Spielerzug; Gegner-Angriff loest Kampf aus
- [x] Hub-Dungeon-Rueckkehr: `<`-Kachel am weitesten Punkt vom Spawn, Betritt kehrt zum Hub zurueck
- [x] Speichern/Laden in die Spielschleife integrieren
  - [x] `game.py`: `starte()` laedt Speicherstand, zeigt "Weiter spielen" / "Neues Spiel" je nach Lage
  - [x] Auto-Speichern beim Hub-Eintritt, nach Tod-Reset und beim Beenden (Q)

- [x] Entitaet-Basis (Refactor)
  - [x] `src/entities/entitaet.py`: Basis-Klasse mit hp/hp_max, pp, verteidigung, resistenzen, angriffe, lebt
  - [x] `Spieler(Entitaet)`: lp/lp_max als Alias-Properties auf hp/hp_max — kampf.py/speichern.py unveraendert
  - [x] `Gegner(Entitaet)`: lebt-Property in Basis; als_dict/aus_dict via super()

### Mittelfristig

- [ ] items.json + Inventar-System (Spieler.inventar, Item-Klasse, Loot)
- [ ] weapons.json + Ausruestungsslots (Waffe ueberschreibt basis_schaden)
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
