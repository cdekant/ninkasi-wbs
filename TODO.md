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

- [x] Inventar-System
  - [x] `data/items.json`: verbrauchbar/waffe/ruestung/material/quest; stapelbar, seltenheit, haltbarkeit_max
  - [x] `src/entities/item.py`: typen_laden()
  - [x] `src/systems/inventar.py`: hinzufuegen (stapelbar vs. Instanz), entfernen, benutzen (heilen_lp/pp/mp)
  - [x] `src/entities/player.py`: inventar, ausruestung (6 Slots) + Serialisierung
  - [x] `src/systems/speichern.py`: bodenloot in STANDARD_AKTUELL
  - [x] `data/enemies.json`: loot_pool befuellt (gaerkeller_schimmel, lebensmittelkontrolleur)
  - [x] `src/systems/menus.py`: Inventar-Tab (Hub + Dungeon), anzahl_auswaehlbar_fuer()
  - [x] `src/ui/menu_anzeige.py`: Inventar-Renderer (seltenheit-Farben, Haltbarkeit, Detail-Text)
  - [x] `game.py`: bodenloot, Loot-Drop nach Sieg, Auto-Pickup beim Betreten, Rendering, ENTER benutzen
  - [x] `game.py`: Inventar per TAB auch im Kampf oeffnen; Verbrauchsmaterialien ohne Kampfrunde benutzen
  - [x] `game.py`: Versionsnummer aus `VERSION`-Datei lesen (keine Doppelpflege mehr)

### Mittelfristig

- [x] Zonen-System (Zonen-Abfolge pro Level, Uebergaenge, Schwierigkeits-Skalierung)
  - [x] `src/systems/speichern.py`: zone_index, zonen_gesamt, level_name in STANDARD_AKTUELL + tod_reset
  - [x] `game.py`: _betrete_dungeon wuerfelt zonen_gesamt; _bewege naechste Zone oder Hub; _spawne_gegner skaliert Staerke (+5%/Zone) und Anzahl (+2/Zone)
  - [x] HUD: Zone X/Y im Dungeon angezeigt
  - [x] HP/PP/MP-Auffuellung bei Hub-Rueckkehr
- [x] Raster-Kartengenerator fuer Gewaechshaus-Level
  - [x] `src/map/raster.py`: gleichmaessiges N×M-Raster, Raeume zentriert, Korridore konfigurierbar breit, Objekte mit position/abstand_wand
  - [x] `src/map/karte.py`: Algorithmus-Dispatcher (bsp / raster)
  - [x] `data/levels.json`: pflanzenzuechtung (raster 3×2, Hochbeete, Pflanzen, 5–7 Zonen)
- [ ] Ausruestungs-System (Anlegen/Ablegen, Kampf-Integration, Waffe ersetzt basis_schaden)
- [ ] Mini-Map (Fog of War, Zone-Graph-Anzeige)
- [ ] Schwarm-Gegner (SchwarmGegner-Klasse, AoE-Logik)
- [ ] Noise-Generator fuer Aussen-Level (Aussaat, Ernte)

### Langfristig

- [ ] Alle Level der Braukette (Aussaat bis Verkauf) in `data/levels.json`
  - inkl. Geheim-Level (erben Grammatik via `"basis"`)
- [ ] Charaktererstellung / Archetypen
- [ ] Tile-Grafikschicht (nur `src/ui/` betroffen — Tileset-Tausch genuegt)
- [ ] Musik/Sound
