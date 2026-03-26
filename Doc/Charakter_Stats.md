---
lang: de-DE
---

# Charakter-Eigenschaften und Skill-Cluster

Design-Dokument: Charaktereigenschaften, Skill-Cluster, EP-Kostenmodifikation und Soft-Cap-System.

---

## Überblick

Sechs **Charaktereigenschaften** sind keine Kampf- oder Magie-Werte, sondern **Persönlichkeitsausrichtungen**: Sie beeinflussen ausschließlich, wie schnell der Spieler bestimmte Skills erlernen kann (EP-Kostenreduktion). Kein Mapping auf LP, Verteidigung, Angriff oder sonstige Spielwerte. Skills bleiben für alle Charaktere zugänglich — keine harten Sperren, nur Spezialisierungsanreize.

---

## Die sechs Eigenschaften

| Eigenschaft | Thematischer Schwerpunkt |
|---|---|
| **Körperkraft** | Physische Ausdauer, Nahkampf, Lebenskraft |
| **Geschicklichkeit** | Präzision, Kampftechnik, Bewegung |
| **Wissen** | Brauwissenschaft, Natur, Rohstoffe |
| **Weisheit** | Magie, Wahrnehmung, metaphysisches Verständnis |
| **Charisma** | Handel, Überzeugung, soziale Kontrolle |
| **Geist** | Psi, Intuition, Zahlenmystik |

---

## Charaktererstellung

Zu Beginn eines Runs erhält der Spieler **10 Eigenschaftspunkte** zum freien Verteilen.

- **Minimum pro Eigenschaft:** 0
- **Maximum pro Eigenschaft:** `EIGENSCHAFT_START_MAX` in `config.py` (Standard: 5; Startobergrenze — nicht die globale Obergrenze)
- Punkte können nicht zurückgenommen werden (kein Umskill)

**UI:** Eigener Charaktererstellungs-Bildschirm vor dem ersten Dungeon-Einstieg (eigener `modus`-Zustand).

**Weitere Eigenschaftspunkte im Spielverlauf:** Durch Bosskämpfe, besondere Items, Levelaufstiege und ähnliche Ereignisse können weitere Punkte dazugewonnen werden. Diese können in bereits investierte Eigenschaften oder in bisher vernachlässigte fließen. Kein globales Cap — das Diminishing-Returns-System übernimmt die Balance. Details zur Vergabe werden später geplant; die Datenstruktur muss Eigenschaftspunkte-Vergabe von Anfang an unterstützen.

---

## Skill-Kategorien und Eigenschafts-Mapping

Es gibt genau **6 Skill-Kategorien**. Kategorie und Cluster fallen zusammen — jede Kategorie hat eine Primär- und eine Sekundär-Eigenschaft. Skills tragen in `skills.json` direkt den Kategorienamen.

| Kategorie | Primär | Sekundär |
|---|---|---|
| **Lebenskraft und Tennentänzerei** | Körperkraft | Geschicklichkeit |
| **Kesselzorn und Sudwall** | Geschicklichkeit | Wissen |
| **Natur-, Korn- und Braukunde** | Wissen | Geist |
| **Kessel-Magie und Meta-Braukunde** | Weisheit | Charisma |
| **Marktschreierei und Nachschub** | Charisma | Weisheit |
| **Brennblasen-Psi und Zahlenkult** | Geist | Charisma |

**Struktur in `skills.json`:**

```json
{
  "eigenschaften": ["koerperkraft", "geschicklichkeit", "wissen", "weisheit", "charisma", "geist"],
  "kategorien": [
    { "name": "Lebenskraft und Tennentänzerei",  "primaer": "koerperkraft",     "sekundaer": "geschicklichkeit" },
    { "name": "Kesselzorn und Sudwall",           "primaer": "geschicklichkeit", "sekundaer": "wissen"           },
    { "name": "Natur-, Korn- und Braukunde",      "primaer": "wissen",           "sekundaer": "geist"            },
    { "name": "Kessel-Magie und Meta-Braukunde",  "primaer": "weisheit",         "sekundaer": "charisma"         },
    { "name": "Marktschreierei und Nachschub",    "primaer": "charisma",         "sekundaer": "weisheit"         },
    { "name": "Brennblasen-Psi und Zahlenkult",   "primaer": "geist",            "sekundaer": "charisma"         }
  ],
  "skills": [ ... ]
}
```

Neuen Skill einer Kategorie zuordnen: nur `"kategorie"` im Skill-Eintrag setzen. Neue Kategorie anlegen: einen Eintrag in `"kategorien"` ergänzen — kein Code-Umbau nötig.

---

## EP-Kostenreduktion: Stufenmodell (Soft Cap)

Die Wirksamkeit pro Eigenschaftspunkt nimmt mit steigender Gesamtpunktzahl ab.
Dadurch bleibt Spezialisierung lohnend, ohne bei hohen Punktzahlen trivial zu werden.

### Primär-Eigenschaft

| Punkte in der Eigenschaft | Reduktion pro Punkt |
|---|---|
| 1 – 5 | 7 % |
| 6 – 10 | 3,5 % |
| 11 + | 1,75 % |

### Sekundär-Eigenschaft

| Punkte in der Eigenschaft | Reduktion pro Punkt |
|---|---|
| 1 – 5 | 3 % |
| 6 – 10 | 1,5 % |
| 11 + | 0,75 % |

### Formel

```
reduktion = summe(wirkung_pro_punkt je Stufe, primär)
          + summe(wirkung_pro_punkt je Stufe, sekundär)

ep_kosten_effektiv = ep_kosten_basis × (1 − reduktion)
```

Minimum-Kosten: 20 % der Basiskosten (maximale Gesamtreduktion 80 %).

### Beispielrechnung: maximale Startspezialisierung

5 Punkte Körperkraft (Primär) + 5 Punkte Geschicklichkeit (Sekundär)
→ Cluster „Lebenskraft und Tennentänzerei":

```
5 × 7 % + 5 × 3 % = 35 % + 15 % = 50 % Reduktion
```

Halbe EP-Kosten — das Maximum das mit 10 Startpunkten erreichbar ist.

### Konfiguration

Die Stufengrenzen, Prozentwerte und Startobergrenze liegen in `config.py`,
nicht hartcodiert in der Spiellogik. Änderungen am Balance erfordern keine Code-Anpassung.

```json
"eigenschaft_stufen": {
  "primaer": [
    { "bis_punkt": 5,  "pct_pro_punkt": 7.0  },
    { "bis_punkt": 10, "pct_pro_punkt": 3.5  },
    { "bis_punkt": 99, "pct_pro_punkt": 1.75 }
  ],
  "sekundaer": [
    { "bis_punkt": 5,  "pct_pro_punkt": 3.0  },
    { "bis_punkt": 10, "pct_pro_punkt": 1.5  },
    { "bis_punkt": 99, "pct_pro_punkt": 0.75 }
  ]
}
```

Zusätzlich in `config.py`:

```python
EIGENSCHAFT_START_MAX = 5   # maximale Punkte pro Eigenschaft bei der Charaktererstellung
```

---

## Bildschirme und Tastenbelegung

| Taste | Bildschirm | Verfügbar |
|-------|------------|-----------|
| TAB | Skill-Baum | nur Hub |
| I | Inventar | Hub, Dungeon, Kampf |
| C | Charakter + Ausrüstung | Hub, Dungeon |

**Charakterbildschirm (C):**
- Eigenschaften mit aktuellen Punktzahlen
- Ausrüstungsslots (Planung nach hinten gestellt)
- Ausrüsten nur außerhalb des Kampfes

**Hinweis zur Implementierung:** Inventar ist aktuell noch auf TAB — Umstellung auf I steht aus.

---

## Eigenschaftspunkte im Spielverlauf

Weitere Eigenschaftspunkte werden über **verbrauchbare Items** vergeben — eine einheitliche Code-Stelle in `inventar.py`, kein separater Trigger pro Quelle.

**Effekttyp:** `eigenschaft_punkt_erhoehen` in `effekttypen.json`
**Ablauf beim Benutzen:** Item benutzen → Auswahlbildschirm (welche Eigenschaft +1?) → Punkt vergeben

| Quelle | Mechanismus |
|--------|-------------|
| Truhen | `loot_pool` → Item landet im Inventar (bereits implementiert) |
| Bosskämpfe | Boss-Tod triggert „Loot droppen"-Event → `loot_pool` des Bosses → Item landet im Inventar |
| Hub nach Level-Abschluss | Item im Hub-Shop erhältlich |

**Hinweis zur Implementierung:** Bosskämpfe benötigen ein „Loot droppen"-Event beim Boss-Tod — analog zur Truhen-Interaktion. Dieses Event ist noch nicht implementiert.

---

## Savegame-Struktur

Eigenschaften werden in `savegame.json` unter einer eigenen `charakter`-Ebene gespeichert, getrennt vom laufenden Spielstand:

```json
{
  "charakter": {
    "eigenschaften": { "koerperkraft": 3, "geschicklichkeit": 5, "wissen": 0, "weisheit": 2, "charisma": 0, "geist": 0 }
  },
  "spielstand": {
    "hp": 80, "ort": "dungeon"
  }
}
```

**Warum diese Trennung:** „Wer bin ich" (Persönlichkeitsausrichtung, persistent pro Run) ist sauber getrennt von „Wo bin ich gerade" (laufender Spielstand). Mehrere Charakterslots oder Charakter-Vorlagen (`characters.json`) lassen sich später ergänzen, ohne `spielstand` anzufassen.

---

## `modus`-Zustandsautomat

`modus` in `game.py` steuert Eingabe-Behandlung und Rendering. Jeder Zustand ist ein eigener Block — ein neuer Zustand kostet keine Umstrukturierung.

| modus | Zweck | Status |
|-------|-------|--------|
| `hub` | Hub-Bewegung | implementiert |
| `kampf` | Kampfbildschirm | implementiert |
| `tod` | Tod-Screen | implementiert |
| `charaktererstellung` | Startbildschirm, Punkte verteilen | geplant |
| `dialog` | NPC-Gespräche | später |
| `zwischensequenz` | Story-Momente | später |
