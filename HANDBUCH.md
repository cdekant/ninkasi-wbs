# Handbuch: Battle Ninkasi

## Inhalt

1. [Erfahrungspunkte (EP)](#erfahrungspunkte)
2. [Der Brauerstern — Sechs Stufen, ein Zoigl](#der-brauerstern)
3. [Skill-Menue bedienen](#skill-menue)
4. [Kostentabelle](#kostentabelle)
5. [Tod und Neubeginn](#tod-und-neubeginn)
6. [Skill-Kategorien (Entwurf)](#skill-kategorien)

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

Die Kosten steigen exponentiell: `basis * 3,5^(stufe-1)` (gerundet)

| Stufe | Basis 10 | Basis 15 | Basis 20 | Basis 30 | Basis 50 | Basis 100 |
|---|---|---|---|---|---|---|
| 1 | 10 | 15 | 20 | 30 | 50 | 100 |
| 2 | 35 | 53 | 70 | 105 | 175 | 350 |
| 3 | 123 | 184 | 245 | 368 | 613 | 1.225 |
| 4 | 429 | 643 | 858 | 1.286 | 2.144 | 4.288 |
| 5 | 1.501 | 2.251 | 3.001 | 4.502 | 7.503 | 15.006 |
| 6 (Zoigl) | 5.252 | 7.878 | 10.504 | 15.757 | 26.261 | 52.522 |

Plane langfristig: Zoigl in einem Basis-20-Skill kostet 10.504 EP.

---

## Tod und Neubeginn

Wenn du stirbst:

- **Level-Zustand wird zurueckgesetzt:** Position, LP, PP, Karten-Seed
- **EP und Skills bleiben erhalten** — dein Fortschritt ist sicher
- **Tod-Zaehler** wird erhoeht (ehrliches Protokoll deines Leidens)
- Du startest am Anfang des **aktuellen Levels** (nicht beim allerersten Level)

Das ist das Roguelite-Versprechen: Der Tod kostet Zeit, nicht Fortschritt.


## Skill-Kategorien

Die verfügbaren Skills sind in zwölf Kategorie aufgeteilt.

### Körper

**Der Bierbauch der Brauerin ist ebenso wie ihre Zöpfe ihr Stolz** – Nur mit Training übersteht sie die Strapazen von Schroten, Maischen, Ausschlagen und Anstellen.

- Trinkfestigkeit: 

### Bewegung

**Agil und flink wie ein Wiesel ist sie Ninaksi, die zwei Ströme küsste** – Ausweichen von Angriffen, defekten Dampfventilen, Orientierung und Gewaltmärsche.

### Waffen und Angriff

**Ob Braupaddel, Milchrohrschlüssel oder mobile Keg-Anlage** – Wenn es beweglich ist, kann man es als Waffe verwenden (außer man kann es nicht tragen).

### Rüstung und Verteidigung

**Die Verteidigung umfasst physische, magische, Psi, chemische und biologische Resistenzen** – Rüstungen zu tragen muss trainiert werden, möchte man nicht vom langsamsten Schleim eingeholt werden, Amulette, Ohrringe, Diademe sind leichter zu tragen und bieten oft magischen/Psi-Schutz

### Bier-Magie

**Die Magie der Gaerung ist organisch, lebendig, unkontrollierbar** — Hefe tut was sie will, der Brauer lenkt sie nur. Bier-Magie wirkt auf (höhere) Lebewesen, Prozesse, Zufälle.

### Schnaps-Psi oder SchnaPsi

**Das Psi der Destillation präzise, konzentrierte Klarheit** – SchnaPsi wirkt auf (niedere) Lebewesen, Materie, Zahlen, Technik. Psi-Punkte sind die Waehrung beider Systeme; welches System mehr verbraucht ist offen (`?`).

### Brautechnologie

**Ohne ein gerüttelt Maß an Brauerwissen ist Hopfen und Malz verloren** – ohne das Wissen über Brauprozesse und Geräte wird man sin in den dunkleren Ecken der Brauerei nur schwer behaupten können

### Getreidetechnologie

**Das Wissen über Anbau, Ernte, Maelzen, Schroten ist eine eigene Form von Magie** – es erleichtert die Fortbewegung im Freien und den Kampf gegen viele Mikroorganismen

### Anlagentechnik

**Als Anlagenflüsterer nutzt man die Maschinenumgebung situativ zu seinen Gunsten** – Begünstigt auch das Sammeln von Materialien und pro Run Verbesserungen

### Verfahrenstechnik

**Als Meta-Skill-Tree holt sich Battle Ninkasi hier die letzten Optimierungen** – Prozessoptimierung, Effizienz, EP-Gewinn

### Naturwissenschaften

**Die absolute Basis für viele fortgeschrittene Skills** – Biologie, Chemie, Mikrobiologie

### Mathematik

**Die letzte Stufe der Magie, die kaum eine Brauerin je erreichen wird ...** – Berechnungen, Rezepturen, Psi-Effizienz?

### Gastronomie

**Brauereinnen sind soziale Wesen und wissen wann sie freundlich zu sein haben** - das könnte auch die Kategorie Sozial sein

### Handel und Marketin

### Logistik

### Offene Fragen

- `?` **Psi-Punkte und Mathematik:** Skills sind passiv, zur Erhöhung des Levels verbrauchen sie immer nur EP, SchnaPsi-Punkte werden von aktiven Fähigkeiten bzw. bei Psi-Angriffen verbraucht, bzw. zerstört, so wie "Malz-Punkte" (bessere Bezeichnung?) bei Magie
  ja, Mathematik rein passiv (Boni ohne Ressourcenkosten)?
- alle Skills arbeiten rein passiv, immer Boni
- `?` **Magie vs. Psi im Kampf:** beide wirken gegen Lebewesen (Psi - Schnaps - Desinfektion - gegen Mirkobiologie), Magie (organisch, gegen höhere Lebewesen - daneben Überschneidungen
- `?` **Umwelt:** Feld-Skills (Aussaat, Ernte) vs. Anlagen-Skills (Sudhaus) — aufgeteilt Umwelt kommt zu Rohstofftechnologie, Anlagen zu Verfahrenstechnik oder Brautechnologie

- `?` **Groesse:** 12 Kategorien x ~12 Skills = ~144 Skills ist sehr ambitioniert.
  JA, konkrete Skills folgen demnächst
