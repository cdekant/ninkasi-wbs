---
lang: de-DE
---

# Ninkasi – Wiedergeburt der Bier-Schlächterin

Roguelite-Terminal-RPG. Du bist die als intoxierte Erynne auferstandene mesopotamische Biergöttin Ninkasi. Die Welt ist verrückt geworden und du musst dich gegen verrückte Anti-Alkoholiker, Zombie-Lobbyisten und jede Menge mutierte Schleime zur Wehr setzen. Am Ende musst du das Amok gelaufene vegane Konstrukt Nüchternikum besiegen und der Welt durch Bier Frieden bringen.

Kaempfe dich durch alle Stufen der Wertschöpfungskette — von der Aussaat bis zum
Getränkefachgroßhandel. Jedes Level ist eine andere Etappe der Braukette, mit zufälliger Karte und passenden (und unpassenden) Gegnern.

## Inhalt

1. [Erfahrungspunkte (EP)](#erfahrungspunkte)
2. [Der Brauerstern — Sechs Stufen, ein Zoigl](#der-brauerstern)
3. [Skill-Menue bedienen](#skill-menue)
4. [Kostentabelle](#kostentabelle)
5. [Erkundung](#erkundung)
6. [Gegner](#gegner)
7. [Kampf](#kampf)
8. [Tod und Neubeginn](#tod-und-neubeginn)
9. [Skill-Kategorien (Entwurf)](#skill-kategorien)

## Spielprinzip

**Tod:** Neustart am Anfang des aktuellen Levels — EP und Skills bleiben
erhalten (Roguelite). Der Zoigl-Stern (Brauerstern) mit seinen 6 Stufen ist
das Fortschrittssymbol des Spiels.

## Ethanol-Punkte

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


## Der Brauerstern

Der Brauerstern — auch Zoigl-Stern oder Brauerstern genannt — ist das
Hexagramm der Brauerzunft. Zwei ineinander verschraenkte Dreiecke: eines zeigt
nach oben (Feuer, Hopfen, Gerste), eines nach unten (Wasser, Hefe, Malz). Die
sechs Zacken stehen fuer die sechs Grundzutaten und die sechs Stufen der
Meisterschaft.

**Jeder Skill hat genau 6 Stufen.** Stufe 6 heisst Zoigl — die volle
Beherrschung einer Kunst. Den Zoigl erreicht man nicht zufaellig; er kostet
viele EP und ist das Ziel langfristiger Planung.


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


## Erkundung

Die Karte wird prozedural generiert — jeder Run sieht anders aus. Du startest
in einem zufaelligen Raum; der Rest liegt im Dunkeln.

### Sichtfeld (FOV)

Ninkasi sieht alles innerhalb eines Radius von **8 Kacheln**. Was ausserhalb
liegt, bleibt schwarz. Waende blockieren die Sichtlinie — um die Ecke siehst
du nicht.

### Fog of War

| Darstellung | Bedeutung |
|---|---|
| **Hell** (volle Helligkeit) | Gerade im Sichtfeld |
| **Dunkel** (abgedunkelt) | Schon erkundet, aber nicht mehr im Blickfeld |
| **Schwarz** | Noch nie betreten oder gesehen |

Erkundetes bleibt erkundigt — auch nach dem Tod verschwindet das Wissen
nicht sofort. Neue Karte bei Tod bedeutet: neues Dunkel, neues Erkunden.

### Gegner und Sichtfeld

Gegner sind nur sichtbar wenn sie sich in deinem Sichtfeld befinden.
Ein Gegner ausserhalb des Radius ist unsichtbar — du hoerst ihn nicht kommen.
Erst wenn er ins Licht tritt (oder du nah genug rangehst), erscheint er.


## Gegner

Jeder Gegner-Typ verhaelt sich anders. Manche warten auf dich, andere jagen
dich unerbittlich — und wieder andere kehren um sobald du ausser Reichweite bist.

### Verhalten

| Verhalten | Beschreibung |
|---|---|
| **Statisch** | Bewegt sich nie. Steht immer am selben Fleck. |
| **Territorial** | Reagiert nur wenn du in seinen Radius eintrittst. Gibt die Verfolgung auf sobald du wieder weit genug weg bist. |
| **Verfolgen** | Beginnt die Jagd sobald er dich einmal gesehen hat — und hoert nicht mehr auf. |
| **Flucht** | Weicht dir aktiv aus. |

### Geschwindigkeit

Nicht alle Gegner bewegen sich jeden Zug. Langsame Gegner (z.B. Schimmel)
brauchen zwei Spielerzuege fuer einen eigenen Schritt — traeger, aber nicht
harmloser.

### Flucht bei Verletzung

Manche Gegner fliehen wenn ihre HP einen bestimmten Schwellwert unterschreiten,
unabhaengig von ihrem normalen Verhalten. Ein Schimmel der eigentlich territorial
ist, kehrt bei 30 % HP um und sucht das Weite.

### Aktuelle Gegner (Gaerkeller)

| Symbol | Name | Verhalten | Besonderheit |
|---|---|---|---|
| `m` | Gaerkeller-Schimmel | Territorial (Radius 5) | Flieht unter 30 % HP; bewegt sich langsam |
| `K` | Lebensmittelkontrolleur | Verfolgen (Radius 15) | Gibt nie auf |


## Kampf

Laeuft ein Gegner-Symbol deinen Weg, beginnt der Kampf automatisch sobald du
dich auf sein Feld bewegst. Ein Kampf-Panel erscheint am unteren Bildschirmrand.

### Kampf-Panel

```
----------------------------------------------------------
m Gaerkeller-Schimmel          @ Ninkasi
HP [######..........] 6/12     LP [############....] 15/20
  Gaerkeller-Schimmel: Sporenausstoss - 2 Schaden (LP 15/20)
  dot_biologisch -> 1 Schaden (LP 14/20)
  dot_biologisch klingt ab.
  Ninkasi greift an: 3 Schaden (Gaerkeller-Schimmel HP 3/12)
[LEERTASTE] Angreifen
----------------------------------------------------------
```

- **Links:** Gegner mit HP-Balken
- **Rechts:** Ninkasi mit LP-Balken
- **Mitte:** Kampf-Log der letzten vier Ereignisse
- **Unten:** Aktuelle Aktion oder Ergebnis

### Kampfablauf pro Runde

1. Gegner regeneriert (falls er Regeneration hat)
2. Status-Effekte wirken — DoT zieht Schaden ab, Dauer sinkt
3. Ninkasi greift an
4. Gegner greift an (zufaelliger Angriff aus seiner Liste)

### Steuerung im Kampf

| Taste | Aktion |
|---|---|
| **LEERTASTE** oder **ENTER** | Naechste Kampfrunde ausfuehren |
| **LEERTASTE** (nach Ende) | Ergebnis bestaetigen und weiterspielen |

Andere Tasten (Bewegung, TAB) sind waehrend des Kampfes gesperrt.

### Status-Effekte

Manche Angriffe hinterlassen **Status-Effekte** fuer mehrere Runden:

| Typ | Wirkung |
|---|---|
| `dot_biologisch` | Biologischer Schaden pro Runde (Sporen, Wildhefen) |
| `dot_chemisch` | Chemischer Schaden pro Runde |
| `psi_malus_pct` | Reduziert Psi-Effektivitaet um X % |

Status-Effekte klingen nach ihrer Dauer automatisch ab.

### Resistenzen

Manche Gegner sind gegen bestimmte Schadenstypen resistent. Resistenzwerte
sind in `data/enemies.json` hinterlegt und werden im Kampf automatisch
berechnet — ihr bemerkt sie daran, dass weniger Schaden angezeigt wird als
erwartet.

### Sieg und Niederlage

- **Sieg:** Gegner faellt auf 0 HP — ihr erhaltet EP und kehrt zur Erkundung zurueck.
- **Niederlage:** Ninkasi faellt auf 0 LP — Tod-Reset (siehe naechstes Kapitel).


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

- Trinkfestigkeit

- Saumagen

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
