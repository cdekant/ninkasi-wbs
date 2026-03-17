# Handbuch: Battle Ninkasi

## Inhalt

1. [Erfahrungspunkte (EP)](#erfahrungspunkte)
2. [Der Brauerstern — Sechs Stufen, ein Zoigl](#der-brauerstern)
3. [Skill-Menue bedienen](#skill-menue)
4. [Kostentabelle](#kostentabelle)
5. [Tod und Neubeginn](#tod-und-neubeginn)

---

## ETHANOL-Punkte

EP sind die Währung deines Fortschritts. Sie werden durch Handlungen verdient und können manuell in Brauer-Fertigkeiten investiert werden.

**Wie verdiene ich EP?** Ein paar Beispiele.

| Aktion | EP |
|---|---|
| Bewegung auf freiem Feld | 1 (+ Skill-Bonus) |
| Bewegung im Sudhaus | 1 (+ Skill-Bonus) |
| Gegner besiegen | je nach Gegner |
| Raetsel loesen | je nach Raetsel |

Wandbewegungen (kein Ortswechsel) zaehlen **nicht** — Leerlauf bringt nichts.

**EP sind permanent.** Sie ueberstehen jeden Tod und jeden Level-Neustart.
Ausgeben: EP werden im Skill-Menue abgezogen, sobald ein Skill gekauft wird.
Kein Verlust durch Tod.

---

## Der Brauerstern

Der Brauerstern — auch Zoigl-Stern oder Brauerstern genannt — ist das
Hexagramm der Brauerzunft. Zwei ineinander verschraenkte Dreiecke: eines zeigt
nach oben (Feuer, Hopfen, Gerste), eines nach unten (Wasser, Hefe, Malz). Die
sechs Zacken stehen fuer die sechs Grundzutaten und die sechs Stufen der
Meisterschaft.

**Jeder Skill hat genau 6 Stufen.** Stufe 6 heisst Zoigl — die volle
Beherrschung einer Kunst. Den Zoigl erreicht man nicht zufaellig; er kostet
viele EP und ist das Ziel langfristiger Planung.

```
         *
        ***
       *****
      **** **
     *** *****
    **  *** **
   *  *  *   *
  ****** ****
 *  ***   **
    *  * ***
       ***
        *
```
*(ASCII-Annaeherung an den Brauerstern mit fünfzackigen Asterisken)*

---

## Skill-Menue

Das Menue ist nur zwischen den Runs verfuegbar — also in **Mannis Pilsstube**,
nicht mitten im Level. Waehrend eines Runs ist TAB wirkungslos.

### Menue oeffnen und wechseln

| Taste | Wirkung |
|---|---|
| **TAB** | Menue oeffnen (erstes verfuegbares) |
| **TAB** (im Menue) | Zum naechsten Tab wechseln |
| **Shift + TAB** | Zum vorherigen Tab wechseln |
| **ESC** | Menue schliessen |

Verfuegbare Tabs zwischen den Runs: **Skill-Baum** und **Mannis Pilsstube**.

### Im Skill-Baum navigieren

| Taste | Wirkung |
|---|---|
| **W** oder **Pfeil oben** | Skill-Auswahl nach oben |
| **S** oder **Pfeil unten** | Skill-Auswahl nach unten |
| **ENTER** | Ausgewaehlten Skill kaufen (naechste Stufe) |

### Was du im Skill-Baum siehst

- Deine EP (verfuegbar und gesamt erhalten)
- Alle Skills nach Kategorie
- Aktuelle Stufe je Skill als Punkte: `●●●○○○` = Stufe 3 von 6
- EP-Kosten fuer die naechste Stufe
- Farbkodierung:
  - **Gelb** = ausgewaehlt
  - **Weiss** = kaufbar
  - **Rot** = zu wenig EP
  - **Grau** = gesperrt (Voraussetzung nicht erfuellt oder Zoigl erreicht)
- Detailzeile unten: Effekt der naechsten Stufe oder Grund fuer Sperre
- Rueckmeldungszeile: Ergebnis des letzten Kaufversuchs

---

## Kostentabelle

Die Kosten steigen exponentiell: `basis * 4^(stufe-1)`

| Stufe | Basis 10 | Basis 15 | Basis 20 | Basis 25 |
|---|---|---|---|---|
| 1 | 10 | 15 | 20 | 25 |
| 2 | 40 | 60 | 80 | 100 |
| 3 | 160 | 240 | 320 | 400 |
| 4 | 640 | 960 | 1.280 | 1.600 |
| 5 | 2.560 | 3.840 | 5.120 | 6.400 |
| 6 (Zoigl) | 10.240 | 15.360 | 20.480 | 25.600 |

Plane langfristig: Zoigl in einem Basis-20-Skill kostet 20.480 EP.

---

## Tod und Neubeginn

Wenn du stirbst:

- **Level-Zustand wird zurueckgesetzt:** Position, LP, PP, Karten-Seed
- **EP und Skills bleiben erhalten** — dein Fortschritt ist sicher
- **Tod-Zaehler** wird erhoeht (ehrliches Protokoll deines Leidens)
- Du startest am Anfang des **aktuellen Levels** (nicht beim allerersten Level)

Das ist das Roguelite-Versprechen: Der Tod kostet Zeit, nicht Fortschritt.
