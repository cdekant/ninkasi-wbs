# TODO

- Onboarding-Dokumentation: entscheiden, was neben CLAUDE.md für einen schnellen Einstieg fehlt
- [ ] Skill-System dokumentieren: Effekt-Pipeline, Kauflogik, Zusammenspiel `skills.py` ↔ `skills.json` ↔ `effekttypen.json`
- [ ] Savegame-Struktur dokumentieren: Felder in `saves/savegame.json` erklären (z.B. in `Doc/Savegame.md` oder direkt in `speichern.py`)

## 1 BUGS UND LOGIKFEHLER

## 2 NEUE FEATURES

### 2.1 Kurzfristig

#### 2.1.1 NUR custom-Tiles verwenden

- [ ] Tileset: Umbenennung + PUA-Reorganisation — Plan: `Plaene/2026-03-20_tileset-benennung-und-transition.md`
- Prio: Spieler (@), Gegner-Sprites, Wand (#), Boden (.), Objekte — Buchstaben zuletzt

### Mittelfristig

- [x] **Direkt-Kampf auf der Karte + Aktionsökonomie** (ersetzt schwebendes Kampffenster)

  **Architektur-Entscheidung:** Kein `modus = "kampf"`, kein schwebendes Fenster. Jede Spieleraktion (Bewegung, Bump-Angriff, Fernkampf, Item benutzen) kostet 1 Runde; danach agieren alle lebenden Gegner einmal (Welt-Tick). Kampf findet direkt auf der Karte statt.

  *Wegfällt komplett:*
  - `KampfZustand`-Klasse und `runde_ausfuehren()` / `abschlag_ausfuehren()` in `kampf.py`
  - `aktiver_kampf`, `aktiver_kampf_eintrag`, `_kampfrunden_zaehler` in `game.py`
  - `_zeichne_kampf_panel()`, `_rahmen_kampf()`, `_linie_kampf()` in `game.py`
  - `modus = "kampf"` (nur noch `"hub"`, `"zielauswahl"`, `"tod"`, `"charaktererstellung"`, `"eigenschaft_auswahl"`)

  *`src/systems/kampf.py` wird reines Berechnungsmodul:*
  - `schaden_berechnen()` bleibt unverändert
  - `_effekt_hinzufuegen()` und `aktiver_effekt_wert()` bleiben (werden auf Entitäten angewendet)
  - Neuer Einstiegspunkt `nahkampf_angriff(angreifer, ziel) -> list[str]`: berechnet Schaden, wendet Effekte an, gibt Log-Zeilen zurück
  - Neuer Einstiegspunkt `fernkampf_angriff(angreifer, ziel, angriff_def) -> list[str]`: analog für Fernkampf-Angriffe

  *Status-Effekte wandern auf die Entitäten:*
  - `Entitaet` bekommt `self.aktive_effekte: list` (ersetzt `KampfZustand.spieler_effekte` / `gegner_effekte`)
  - Neues Modul-Funktion `effekte_tick(entitaet) -> list[str]`: tickt Effekte auf einer Entität, gibt Log-Zeilen zurück
  - `game.py` ruft `effekte_tick()` für Spieler + alle lebenden Gegner einmal pro Welt-Tick auf

  *Festgelegte Kampfregeln:*
  - **Kein Gegenangriff nach Bump-Kill:** Stirbt ein Gegner durch den Bump-Angriff, handelt er nicht mehr im selben Welt-Tick. Kann später per Flag (`gegner_schlaegt_zurueck: bool` in `enemies.json`) aktivierbar gemacht werden.
  - **Gelegenheitsangriff beim Verlassen:** Bewegt sich der Spieler weg, erhalten **alle** Chebyshev-1-anliegenden Gegner sofort einen Angriff (vor der Bewegung, außerhalb des normalen Welt-Ticks). Implementierung: in `_bewege()` alle Gegner mit Chebyshev-Distanz 1 zur aktuellen Spielerposition sammeln → je `nahkampf_angriff(gegner, spieler)` in Listenreihenfolge → dann erst Spieler bewegen.
  - **Welt-Tick-Reihenfolge:** `effekte_tick()` für alle Entitäten (Spieler + Gegner) → danach KI-Aktionen aller lebenden Gegner. Bei mehreren Gegnern: Reihenfolge nach Listenreihenfolge in `gegner_auf_karte` (deterministisch, kein Zufallsfaktor).
  - **Unbewaffnet:** Bump-Angriff ohne ausgerüstete Waffe nutzt `spieler.basis_schaden` mit Schadenstyp `"nah"`.

  *`game.py` — Aktionsökonomie:*
  - Jede Aktion endet mit `_welt_tick()`: `effekte_tick()` für alle, dann KI aller lebenden Gegner
  - Bump auf Gegner → `nahkampf_angriff(spieler, gegner)` → falls Gegner tot: Loot + entfernen, kein Welt-Tick-Angriff dieses Gegners; dann `_welt_tick()`
  - Bewegung auf freies Feld → Gelegenheitsangriff-Check → Spieler bewegt sich → `_welt_tick()`
  - Item benutzen → Effekt anwenden → `_welt_tick()`
  - Tod des Spielers: wenn `spieler.lp <= 0` nach beliebiger Schadens-Anwendung → sofort `modus = "tod"`

  *Gegner-Zustand sichtbar machen (kein HP-Fenster):*
  - Gegner-Symbol-Farbe wechselt mit HP-Schwellwerten: > 60% grün → > 30% gelb → ≤ 30% rot (Farben in `config.py` als Konstanten)
  - Bei erstem Unterschreiten von 60% und 30% HP: einmalige Log-Meldung, z.B. `"Gaerkeller-Schimmel wirkt angeschlagen."` / `"... wirkt schwer verwundet."`
  - Schwellwert-Texte pro Gegner-Typ optional in `enemies.json` überschreibbar (`"meldung_angeschlagen"`, `"meldung_verwundet"`); sonst generischer Fallback

  *Fernkampf (Spieler und Gegner) — Map-Level ohne Fenster:*
  - `data/enemies.json`: Angriffs-Einträge bekommen optionales `"reichweite": N` (Default 1); neues `"verhalten": "distanz"` (hält Abstand, weicht zurück wenn Spieler zu nah)
  - `src/systems/ki.py`: vor Bewegung prüfen ob Spieler in Angriffs-Reichweite + LOS → Angriff ohne Bewegung; `verhalten == "distanz"`: Rückzug wenn Spieler näher als `reichweite - 1`; Hilfsfunktion `in_reichweite(ax, ay, bx, by, r)` (Chebyshev-Distanz)
  - `game.py` — Modus `"zielauswahl"`: Taste `F` aktiviert Cursor auf Spielerposition; WASD bewegt Cursor (nur FOV-sichtbare Felder); ENTER auf Gegner → Reichweite + LOS prüfen → `fernkampf_angriff()` → `_welt_tick()`; ESC abbrechn; kein Fernkampf ohne Waffe mit `reichweite > 1`
  - `src/ui/` — Cursor-Rendering: Cursor-Kachel auf Zielfeld; Gegner in Reichweite + LOS: Rot hervorgehoben; sonst Grau; Shortcut-Zeile: `[WASD] Cursor   [ENTER] Angreifen   [ESC] Abbrechen`

- [x] **Diagonalbewegung + Geschwindigkeitssystem** (Z/U/B/N = NW/NE/SW/SE; Skill `sudlaeufer`; Bonus-Schritt ohne Welt-Tick)
- [ ] Bonus-Raum / Geheim-Level — Plan: `Plaene/2026-03-20_bonus-raum.md`
  - `"basis"`-Auflösung in `karte.py`, Bonus-Ausgang in `game.py`, Geheim-Einträge in `levels.json`
- [ ] Ausruestungs-System (Anlegen/Ablegen, Kampf-Integration, Waffe ersetzt basis_schaden)
- [ ] Mini-Map (Fog of War, Zone-Graph-Anzeige)
- [ ] Schwarm-Gegner (SchwarmGegner-Klasse, AoE-Logik)
- [ ] Noise-Generator fuer Aussen-Level (Aussaat, Ernte)

### Langfristig

- [ ] **Designwechsel: Roguelite → Roguelike** (keine permanente Stat-Progression über Runs)
  - **Kern:** Skillpunkte, Skills und Ausrüstung werden bei Tod vollständig zurückgesetzt — kein Cross-Run-Vorteil
  - **Hub bleibt**, aber nur mit Run-temporären Ressourcen (Gold, Brauwährung):
    - Skills im Hub kaufen (mit im aktuellen Run gesammeltem Gold) → bei Tod weg
    - Ausrüstung kaufen → bei Tod weg
    - NPC/Story-Interaktion bleibt dauerhaft (narrativer Fortschritt, keine Stats)
  - **Skills:** Kaufbar im Hub zwischen Dungeon-Levels (nicht dauerhaft); Skill-Menü-Zugang via TAB nur im Hub
  - **Meta-Progression optional (nur Inhalte, keine Stats):** neue Gegner-Typen, neue Level-Grammatiken freischalten — kein Stat-Vorteil, roguelike-kompatibel
  - **Betroffene Dateien:** `player.py` (EP/Skill-Reset bei Tod), `speichern.py` (was wird gespeichert?), `src/systems/skills.py` (Kauflogik nur Run-Scope), `HANDBUCH.md`, `CLAUDE.md`
  - **Offene Entscheidung:** Meta-Progression (Inhalts-Freischaltung) ja/nein?

- [ ] Alle Level der Braukette (Aussaat bis Verkauf) in `data/levels.json`
  - inkl. Geheim-Level (erben Grammatik via `"basis"`)
- [ ] Tile-Grafikschicht (nur `src/ui/` betroffen — Tileset-Tausch genuegt)
- [ ] Musik/Sound
