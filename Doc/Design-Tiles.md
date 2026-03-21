# Design-Referenz: Tile-System

Letzte Aktualisierung: 2026-03-21

---

## Die 3 wichtigsten Regeln

1. **`src/tiles.py` ist die einzige Quelle der Wahrheit** für Tile-Codepoints und -Namen.
   Alle anderen Dateien (JSON, Code) verwenden ausschließlich symbolische Namen wie `"INTER_PFLANZE"` —
   nie rohe Unicode-Codepoints.

2. **Benennungsschema: `GRUPPE_NAME[_VARIANTE]`** — Alles in GROSSBUCHSTABEN, Wörter mit `_` getrennt.
   Keine Level-Präfixe. Tiles beschreiben was sie zeigen, nicht wo sie vorkommen.

3. **Custom Tiles = 16×16 px PNGs** unter `assets/tiles/<gruppe>/`, Dateiname = Konstantenname (lowercase).
   Injiziert via `tileset.set_tile()` in `main.py`. Jedes Tile braucht einen Eintrag in
   `TILE_NAMEN` (symbolischer Lookup) und `TILE_DATEIEN` (PNG-Pfad).

---

## Benennungsschema

### Regel: `GRUPPE_NAME[_VARIANTE]`

```
GRUPPE     Kürzel für die semantische Kategorie (s.u.)
NAME       Beschreibendes Substantiv — Deutsch, ohne Sonderzeichen
VARIANTE   Nur bei mehreren Varianten eines Typs: _HELL, _DUNKEL, _NASS, _RISSIG …
```

**Keine Level-Präfixe.** Farbvarianten pro Level kommen aus dem `farben`-Block in `levels.json`,
nicht aus separaten Tile-Namen. Beispiel: `BODEN_FLIESSE`, `BODEN_FLIESSE_NASS` — nie `PFZ_BODEN_FLIESSE`.

Nur so viele Namensteile wie nötig für eindeutige Lesbarkeit.
VEG, BRAU und DEKO sind keine eigenen Gruppen — sie tauchen als beschreibender Mittelteil auf:
`OBJ_BRAU_KEG_HOLZ`, `OBJ_VEG_STRAUCH`.

### Gruppen-Kürzel

| Kürzel   | Bedeutung                                          | Beispiele                                     |
|----------|----------------------------------------------------|-----------------------------------------------|
| `HUB`    | Hub-Objekte, Story-Tiles, Einmaliges               | `HUB_BRAUKESSEL`                              |
| `BODEN`  | Bodentypen (begehbar)                              | `BODEN_FLIESSE`, `BODEN_ERDE`, `BODEN_STEIN` |
| `WAND`   | Wandtypen (blockierend, inkl. Fenster/Türen)       | `WAND_FENSTER`, `WAND_GITTER`, `WAND_TUER`   |
| `INTER`  | Interaktive Karten-Objekte                         | `INTER_PFLANZE`, `INTER_TRUHE`                |
| `OBJ`    | Nicht-interaktive Karten-Objekte                   | `OBJ_VEG_GRAS`, `OBJ_BRAU_KEG_HOLZ`          |
| `GEGNER` | Gegner-Sprites                                     | `GEGNER_SCHLEIM_GESICHT`                      |
| `ITEM`   | Item-Sprites                                       | `ITEM_TRANK`, `ITEM_SCHLUESSEL`               |
| `UI`     | Interface-Elemente                                 | `UI_BALKEN_RAND`, `UI_STERN`                  |

### JSON-Schlüssel

Identisch zur Python-Konstante (String): `"INTER_PFLANZE"`, `"WAND_FENSTER"` usw.
Gegner-IDs in `enemies.json` folgen dem Schema `typ[_variante]` — **kein** `GEGNER_`-Präfix,
da sie eine andere Kategorie sind: `wildhefe`, `schleimblob_einfach`, `lebensmittelkontrolleur`.

---

## PUA-Cluster

Unicode Private Use Area U+E000–U+F8FF (6400 Slots) — kein Konflikt mit Cheepicus/CP437.

```
U+E000 – U+E03F  (  64)  HUB      Hub-Objekte, Story-Tiles, Einmaliges
U+E040 – U+E07F  (  64)  BODEN    Bodentypen (begehbar)
U+E080 – U+E0BF  (  64)  WAND     Wandtypen (inkl. Fenster, Türen, Gitter)
U+E0C0 – U+E1BF  ( 256)  INTER    Interaktive Karten-Objekte
U+E1C0 – U+E2BF  ( 256)  OBJ      Nicht-interaktive Karten-Objekte
U+E2C0 – U+E33F  ( 128)  GEGNER   Gegner-Sprites
U+E340 – U+E3BF  ( 128)  ITEM     Item-Sprites
U+E3C0 – U+E3DF  (  32)  UI       Interface-Elemente
U+E3E0 – U+F8FF         Reserviert
```

---

## Aktuelles Tile-Register

| Konstante                        | Codepoint | PNG-Datei                                      |
|----------------------------------|-----------|------------------------------------------------|
| `HUB_BRAUKESSEL`                 | U+E000    | `assets/tiles/hub/hub_braukessel.png`          |
| `HUB_NINKASI`                    | U+E001    | `assets/tiles/hub/hub_ninkasi.png`             |
| `BODEN_FLIESSE`                  | U+E040    | `assets/tiles/boden/boden_fliesse.png`         |
| `WAND_FENSTER`                   | U+E080    | `assets/tiles/wand/wand_fenster.png`           |
| `WAND_GITTER`                    | U+E081    | `assets/tiles/wand/wand_gitter.png`            |
| `INTER_PFLANZE`                  | U+E0C0    | `assets/tiles/inter/inter_pflanze.png`         |
| `OBJ_VEG_GRAS`                   | U+E1C0    | `assets/tiles/obj/obj_veg_gras.png`            |
| `GEGNER_SCHLEIM_GESICHT`         | U+E2C0    | `assets/tiles/gegner/schleim-gesicht.png`      |
| `GEGNER_LEBENSMITTELKONTROLLEUR` | U+E2C1    | `assets/tiles/gegner/lebensmittelkontrolleur.png` |

---

## Roadmap: CP437 → Custom Tiles

CP437-Zeichen werden über `set_tile(ord('X'), png)` überschrieben — kein Architektur-Umbau nötig.
Cheepicus bleibt als Basis-Tileset bis alle relevanten Zeichen ersetzt sind.

| Priorität | Zeichen           | Verwendung          | Tile-Name                 | Status     |
|-----------|-------------------|---------------------|---------------------------|------------|
| 1         | `@`               | Spieler-Sprite      | `HUB_NINKASI`             | ✓ erledigt |
| 1         | Gegner-Buchstaben | Gegner-Sprites      | GEGNER-Cluster            | ✓ 2 von N  |
| 2         | `#`               | Standard-Wand       | `WAND_STANDARD`           | offen      |
| 2         | `.`               | Standard-Boden      | `BODEN_STANDARD`          | offen      |
| 3         | `O`, `>`, `<`     | Objekte, Ausgänge   | OBJ- bzw. HUB-Cluster     | offen      |
| 4         | `!`, `*`, `/`, `[`| Item-Symbole        | ITEM-Cluster              | offen      |
| 5         | Box-Drawing       | Kampffenster-Rahmen | UI-Cluster                | offen      |
| 6         | Buchstaben/Zahlen | Text                | Zuletzt oder nie          | offen      |

**Hinweis Gegner:** Gegner-Zeichen (`m`, `K`) sind CP437-Buchstaben. Wenn ein eigenes Sprite
gezeichnet wird, bekommt der Typ einen PUA-Codepoint aus dem GEGNER-Cluster. Das `symbol`-Feld
in `enemies.json` wird auf den symbolischen Namen umgestellt — kein `set_tile(ord('m'))` nötig.

---

## Farbsystem

### Prinzip: Graustufen-Tiles + `fg`-Tinting

tcod multipliziert beim Rendern: `Ergebnis = Tile-Pixel × (fg / 255)`

Die Graustufe wird zur Helligkeits- und Texturmaske — die Farbe kommt aus dem `fg`-Wert in
`levels.json`. Ein einziges PNG, beliebig viele Farbvarianten. `bg` füllt transparente Pixel
(Ambientlicht, Raumatmosphäre).

| Tile-Typ                      | Graustufen? | Begründung                              |
|-------------------------------|-------------|------------------------------------------|
| Boden, Wand, Decke            | ✓ ja        | nehmen Level-Farbe via `fg` an           |
| Architektur (Fenster, Türen)  | ✓ ja        | idem                                     |
| Brauerei-Ausstattung          | ✓ ja        | idem                                     |
| Objekte (Fass, Kiste)         | ✓ ja        | idem                                     |
| Pflanzen, Vegetation          | ~ teilweise | grüne Eigenfarbe oft gewünscht           |
| Items                         | ✗ nein      | Farbe signalisiert Seltenheit            |
| Gegner-Sprites                | ✗ nein      | Eigenfarbe zur Identifikation            |
| UI-Elemente                   | ✗ nein      | Level-unabhängig                         |

**Konventionen beim Zeichnen:**
- Hellstes Pixel max. (220, 220, 220) — nicht reines Weiß, damit `fg` noch Wirkung zeigt
- Schwarz (0, 0, 0) sparsam — bleibt immer schwarz unabhängig von `fg`
- Transparenz (Alpha < 255) für `bg`-Durchscheinen nutzen

### Stufe A: Farbpaletten in `levels.json` (umzusetzen)

```json
"farben": {
  "boden_fg":  [r, g, b],  "boden_fog":  [r, g, b],
  "wand_fg":   [r, g, b],  "wand_fog":   [r, g, b],
  "boden_bg":  [r, g, b],  "wand_bg":    [r, g, b]
}
```

Beispielpaletten:

| Level            | Stimmung               | `boden_fg`       | `wand_fg`        |
|------------------|------------------------|------------------|------------------|
| Pflanzenzüchtung | Grünliches Gewächshaus | [160, 185, 140]  | [120, 145, 100]  |
| Gärkeller        | Feuchter Keller, gelblich | [140, 135, 100] | [100, 95, 70]   |
| Sudhaus          | Warm, kupfrig          | [190, 155, 110]  | [150, 120, 85]   |
| Getreidelager    | Staubig, beige         | [175, 165, 140]  | [130, 120, 100]  |
| Abfüllung        | Kalt, industriell      | [130, 145, 165]  | [90, 105, 120]   |

### Stufe B: Separate Boden-Tiles für Raum und Gang (mittelfristig)

```json
"kacheln": {
  "boden":      ".",
  "boden_gang": ",",
  "wand":       "#"
}
```

Generatoren verwenden `kacheln.get("boden_gang", kacheln["boden"])` beim Korridor-Graben.
Farbpalette entsprechend um `gang_fg`, `gang_bg`, `gang_fog` erweitern.
