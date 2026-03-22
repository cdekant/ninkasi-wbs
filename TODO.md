# TODO

- Onboarding-Dokumentation: entscheiden, was neben CLAUDE.md für einen schnellen Einstieg fehlt
- [ ] Systeminteraktion dokumentieren: Wie `game.py` die Subsysteme aufruft (Reihenfolge, Abhängigkeiten) — z.B. als `Doc/Architektur.md`
- [ ] Skill-System dokumentieren: Effekt-Pipeline, Kauflogik, Zusammenspiel `skills.py` ↔ `skills.json` ↔ `effekttypen.json`
- [ ] Savegame-Struktur dokumentieren: Felder in `saves/savegame.json` erklären (z.B. in `Doc/Savegame.md` oder direkt in `speichern.py`)

## 1 BUGS UND LOGIKFEHLER

## 2 NEUE FEATURES

### 2.1 Kurzfristig

#### 2.1.1 NUR custom-Tiles verwenden

- [ ] Tileset: Umbenennung + PUA-Reorganisation — Plan: `Plaene/2026-03-20_tileset-benennung-und-transition.md`
- Prio: Spieler (@), Gegner-Sprites, Wand (#), Boden (.), Objekte — Buchstaben zuletzt

### Mittelfristig

- [ ] Bonus-Raum / Geheim-Level — Plan: `Plaene/2026-03-20_bonus-raum.md`
  - `"basis"`-Auflösung in `karte.py`, Bonus-Ausgang in `game.py`, Geheim-Einträge in `levels.json`
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
