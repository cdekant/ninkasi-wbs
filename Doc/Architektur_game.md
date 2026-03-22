# Architektur: game.py

`game.py` ist die Schaltzentrale des Spiels. Es hält den gesamten Spielzustand und entscheidet, was gezeichnet wird, welche Eingaben erlaubt sind und welche Subsysteme wann aufgerufen werden.

---

## Spielzustand: die zwei Variablen

Alles hängt an zwei globalen Variablen:

| Variable | Mögliche Werte | Bedeutung |
|----------|----------------|-----------|
| `modus`  | `"hub"` / `"kampf"` / `"tod"` | Was gerade *passiert* |
| `ort`    | `"pilsstube"` / `"dungeon"` | Wo der Spieler *ist* |

`modus` steuert die Eingabe-Priorität. `ort` steuert, welche Karte gezeichnet wird und welche Menüs verfügbar sind.

---

## Programmstart (Modulebene)

Bevor `starte()` aufgerufen wird, läuft beim Import von `game.py` folgendes ab:

```
1. skills_system.lade_skills()      → alle_skills
2. typen_laden()                    → alle_gegner_typen
3. items_laden()                    → alle_items
4. Spieler()                        → spieler
5. levels.json laden                → alle_level
6. _initialisiere_hub()             → HUB_KARTE, HUB_FOV, …
```

Der Hub wird **einmal** beim Start gebaut und bleibt für die gesamte Sitzung erhalten.

---

## starte() — der Einstiegspunkt

Wird von `main.py` aufgerufen. Läuft in zwei Phasen:

```
Phase 1: Startbildschirm
  laden()                     → Spieler + aktuell aus saves/savegame.json (oder None)
  Loop: _zeichne_startbildschirm → warten auf ENTER / N / Q

Phase 2: Hauptspielschleife
  Loop:
    Zeichnen (abhängig von modus/ort):
      modus == "tod"         → _zeichne_tod_screen()
      ort   == "pilsstube"   → _zeichne_hub()
      sonst                  → zeichne()   (Dungeon)
    context.present(console)
    Events abhören → _handle_key()
```

---

## _handle_key() — Eingabe-Priorität

Die Funktion prüft den Zustand von oben nach unten und gibt nach dem ersten Treffer zurück:

```
1. modus == "tod"    → nur Leertaste: _tod_auferstehen()
2. modus == "kampf"  → Inventar-Navigation ODER Leertaste: _kampf_aktion()
                        ODER WASD: _flucht_versuchen()
3. aktives_menue     → Menü-Navigation (TAB, ESC, W/S, ENTER)
4. Erkundung         → TAB: Menü öffnen
                        WASD/Pfeile: _bewege() oder _hub_bewege()
                        Q: speichern() + Beenden
```

---

## _bewege() — ein Spielerzug im Dungeon

Reihenfolge der Prüfungen (erste zutreffende gewinnt):

```
1. Gegner auf Zielfeld?
     → KampfZustand(spieler, gegner) erstellen
     → modus = "kampf"

2. Interaktives Objekt auf Zielfeld? (loot_pool)
     → Loot würfeln → bodenloot
     → Objekt aus KARTE und DUNGEON_OBJEKTE entfernen

3. Ausgang (<) auf Zielfeld?
     → zone_index < zonen_gesamt-1:  zone_index++, _initialisiere_level()
     → sonst:                        _zurueck_zum_hub()

4. Freies Feld (.)?
     → spieler_x/y aktualisieren
     → FOV neu berechnen  (sichtfeld.berechne_fov)
     → erkundet aktualisieren
     → Bodenloot auf neuem Feld aufheben  (inventar_system.hinzufuegen)
     → ki.ki_tick() → evtl. Gegner startet Kampf → modus = "kampf"
```

---

## _kampf_aktion() — eine Kampfrunde

```
Kampf läuft noch:
  runde_ausfuehren(aktiver_kampf)     ← kampf.py
  alle 3 Runden: ki.ki_tick()         ← "Welt-Tick" (andere Gegner bewegen sich)

Kampf beendet:
  Sieg:       Loot würfeln → bodenloot
              gegner aus gegner_auf_karte entfernen
              modus = "hub"
  Niederlage: tod_gegner_name + Zitat setzen
              modus = "tod"
```

---

## Ort-Übergänge

```
pilsstube → dungeon   _betrete_dungeon()
  Auslöser: Spieler betritt Braukessel-Objekt im Hub
  Ablauf:   zonen_gesamt würfeln, zone_index = 0, _initialisiere_level(), ort = "dungeon"

dungeon → pilsstube   _zurueck_zum_hub()
  Auslöser: Spieler betritt Dungeon-Ausgang (<) auf letzter Zone
  Ablauf:   LP/PP/MP auffüllen, _log, ort = "pilsstube", speichern()

tod → pilsstube       _tod_auferstehen()
  Auslöser: Leertaste auf Tod-Screen
  Ablauf:   tod_reset() (LP/PP zurück, tod_zaehler++), Hub-Position zurücksetzen
            FOV neu berechnen, ort = "pilsstube", modus = "hub", speichern()
```

---

## _initialisiere_level() — neues Level aufbauen

Wird aufgerufen bei: Dungeon-Eintritt, Zonen-Wechsel, nach dem Tod (nicht explizit — erfolgt über _betrete_dungeon).

```
1. generiere_karte(grammatik)   → KARTE + DUNGEON_OBJEKTE   (karte.py)
2. boden_tile aus Grammatik auflösen                         (tiles.py)
3. Spielerposition: erste "." in KARTE
4. BFS-Flood-Fill → Ausgang auf weitestem erreichbaren "."
5. _spawne_gegner(12 + zone_index * 2)
6. bodenloot zurücksetzen ([] — neue Karte, neues Loot)
7. sichtfeld.baue_transparenz()                              (sichtfeld.py)
8. sichtfeld.neues_erkundet()
9. sichtfeld.berechne_fov()
10. sichtfeld.aktualisiere_erkundet()
```

---

## Abhängigkeiten auf einen Blick

| Subsystem | Datei | Wofür |
|-----------|-------|-------|
| `kampf`   | `src/systems/kampf.py` | `KampfZustand`, `runde_ausfuehren`, `abschlag_ausfuehren` |
| `ki`      | `src/systems/ki.py` | `ki_tick` — Gegner-Bewegung nach jedem Spielerzug |
| `sichtfeld` | `src/systems/sichtfeld.py` | FOV + Fog-of-War nach jeder Bewegung |
| `speichern` | `src/systems/speichern.py` | `speichern`, `laden`, `tod_reset`, `STANDARD_AKTUELL` |
| `menus`   | `src/systems/menus.py` | Menü-Auswahl, Tab-Reihenfolge, verfügbare Menüs |
| `inventar` | `src/systems/inventar.py` | `hinzufuegen` (Bodenloot), `benutzen` (Inventar-Menü) |
| `skills`  | `src/systems/skills.py` | `lade_skills` (nur Programmstart) |
| `karte`   | `src/map/karte.py` | `generiere_karte` |
| `hub`     | `src/map/hub.py` | `generiere_hub` (nur Programmstart) |
| `tiles`   | `src/tiles.py` | Tile-Codepoints, `WAND_TILES` |
| `config`  | `config.py` | Layout-Konstanten (Positionen, Größen) |
| `menu_anzeige` | `src/ui/menu_anzeige.py` | `zeichne_menue` — Overlay über Karte |
