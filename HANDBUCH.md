---
lang: de-DE
---

# Ninkasi – Wiedergeburt der Bier-Schlächterin

Roguelite-Terminal-RPG. Du bist die als intoxierte Erynne auferstandene mesopotamische Biergöttin Ninkasi. Die Welt steht am Abgrund und wird beherrscht von durchgeknallten Anti-Alkoholikern, Zombie-Lobbyisten und jeder Menge mutierter Schleime. Am Ende musst du das Amok gelaufene vegane Konstrukt Prohibitus besiegen und der Welt durch Bier Frieden bringen.

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
8. [Inventar](#inventar)
9. [Tod und Neubeginn](#tod-und-neubeginn)
10. [Skill-Kategorien (Entwurf)](#skill-kategorien)

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

Das Menue ist nur im Hub verfuegbar, nicht mitten im Level. Waehrend eines Runs ist TAB wirkungslos.

### Menue oeffnen und wechseln

| Taste | Wirkung |
|---|---|
| **TAB** | Menue oeffnen (erstes verfuegbares) |
| **TAB** (im Menue) | Zum naechsten Tab wechseln |
| **Shift + TAB** | Zum vorherigen Tab wechseln |
| **ESC** | Menue schliessen |

Verfuegbarer Tab im Hub: **Skill-Baum**.

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

### Ausgang zurueck zum Hub

Das Dungeon hat einen Ausgang — eine hellblaue `<`-Kachel. Sie liegt immer am
Punkt der Karte, der am weitesten von deiner Startposition entfernt ist.
Bewege dich auf die Kachel um den Dungeon zu verlassen und in den Hub
zurueckzukehren. Dein Fortschritt im Hub bleibt erhalten; die Dungeon-Karte
wird beim naechsten Betreten neu generiert.

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


## Inventar

### Loot

Besiegte Gegner hinterlassen manchmal Gegenstaende auf dem Boden — erkennbar an
ihrem Symbol (`!` fuer Traenke, `*` fuer Materialien, `/` fuer Waffen, `[` fuer Ruestungen).
Tritt auf das Feld des gefallenen Gegners, um alles automatisch aufzuheben.

### Inventar oeffnen

**TAB** (im Hub, im Dungeon oder mitten im Kampf) oeffnet das Inventar-Menue.
Im Gegensatz zum Skill-Baum ist das Inventar ueberall zugaenglich — du kannst
also mitten im Kampf einen Heiltrank benutzen, ohne eine Kampfrunde zu opfern.

### Gegenstandstypen

| Kategorie | Symbol | Wirkung |
|---|---|---|
| **Verbrauchbar** | `!` | ENTER benutzt das Item sofort (z.B. LP/PP/MP heilen) |
| **Material** | `*` | Kann nicht direkt benutzt werden — Rohstoff fuer spaetere Systeme |
| **Waffe** | `/` | Ausrüsten — noch nicht implementiert |
| **Rüstung** | `[` | Ausrüsten — noch nicht implementiert |

### Seltenheit

Items sind farbkodiert nach Seltenheit:

| Farbe | Seltenheit |
|---|---|
| Weiss | Gewoehnlich |
| Gruen | Ungewoehnlich |
| Blau | Selten |

### Stapeln und Haltbarkeit

Verbrauchbare und Materialien stapeln — mehrere Exemplare belegen einen Slot.
Waffen und Ruestungen stapeln nicht: jedes Exemplar ist eine eigene Instanz mit
eigener Haltbarkeit `[aktuell/max]`. Der Haltbarkeits-Mechanismus
(Abbau, Reparatur) folgt mit dem Ausrüstungs-System.

### Steuerung im Inventar-Menue

| Taste | Wirkung |
|---|---|
| **W** / Pfeil oben | Auswahl nach oben |
| **S** / Pfeil unten | Auswahl nach unten |
| **ENTER** | Item benutzen |
| **TAB** | Zum naechsten Tab wechseln |
| **ESC** | Menue schliessen |


## Tod und Neubeginn

Wenn du stirbst:

- **Level-Zustand wird zurueckgesetzt:** Position, LP, PP, Karten-Seed
- **EP und Skills bleiben erhalten** — dein Fortschritt ist sicher
- **Tod-Zaehler** wird erhoeht (ehrliches Protokoll deines Leidens)
- Du startest am Anfang des **aktuellen Levels** (nicht beim allerersten Level)

Das ist das Roguelite-Versprechen: Der Tod kostet Zeit, nicht Fortschritt.


## Skill-Kategorien

Die verfügbaren Skills sind in 15 Kategorien aufgeteilt. Die Skills selbst sind keine Fähigkeiten, die der Charakter bekommt, es sind einerseits Modifier für die tatsächlichen Fähigkeiten (Level 5 in Hopfenmagie erhöht den Schaden aller Hopfen-Angriffszauber um 25 Prozent z.B.) und andererseits sind für bestimmte Fähigkeiten Mindestskill notwendig (für Hopfen-Creep braucht man mindestens Level 4 in Fortgeschrittene Hopfenmagie).

### Lebenskraft – Vitalität

**Der Bierbauch der Brauerin ist ebenso wie ihre Zöpfe ihr Stolz** – Nur mit Training übersteht sie die Strapazen von Schroten, Maischen, Ausschlagen und Anstellen.

- Trinkfestigkeit

- Saumagen

### Tennentänzerei – Beweglichkeit

**Agil und flink wie ein Wiesel ist sie Ninaksi, die zwei Ströme küsste** – Ausweichen von Angriffen, defekten Dampfventilen, Orientierung und Gewaltmärsche.

### Kesselzorn – Waffen und Angriff

**Ob Braupaddel, Milchrohrschlüssel oder mobile Keg-Anlage** – Wenn es beweglich ist, kann man es als Waffe verwenden (außer man kann es nicht tragen).

### Sudwall – Rüstung und Verteidigung

**Die Verteidigung umfasst physische, magische, Psi, chemische und biologische Resistenzen** – Rüstungen zu tragen muss trainiert werden, möchte man nicht vom langsamsten Schleim eingeholt werden, Amulette, Ohrringe, Diademe sind leichter zu tragen und bieten oft magischen/Psi-Schutz

### Kesselhexerei – Bier-Magie

**Die Magie der Gaerung ist organisch, lebendig, unkontrollierbar** — Hefe tut was sie will, der Brauer lenkt sie nur. Bier-Magie wirkt auf (höhere) Lebewesen, Prozesse, Zufälle.

### SchnaPsi – Psi-Kraft

**Das Psi der Destillation präzise, konzentrierte Klarheit** – SchnaPsi wirkt auf (niedere) Lebewesen, Materie, Zahlen, Technik. Psi-Punkte sind die Waehrung beider Systeme; welches System mehr verbraucht ist offen (`?`).

### Braukunde

**Ohne ein gerüttelt Maß an Brauerwissen ist Hopfen und Malz verloren** – ohne das Wissen über Brauprozesse und Geräte wird man sin in den dunkleren Ecken der Brauerei nur schwer behaupten können

### Kornkunde

**Das Wissen über Anbau, Ernte, Maelzen, Schroten ist eine eigene Form von Magie** – es erleichtert die Fortbewegung im Freien und den Kampf gegen viele Mikroorganismen

### Maschinenkunde

**Als Anlagenflüsterer nutzt man die Maschinenumgebung situativ zu seinen Gunsten** – Begünstigt auch das Sammeln von Materialien und pro Run Verbesserungen

### Meta-Braukunde – Verfahrenstechnik

**Als Meta-Skill-Tree holt sich Battle Ninkasi hier die letzten Optimierungen** – Prozessoptimierung, Effizienz, EP-Gewinn

### Naturkunde

**Die absolute Basis für viele fortgeschrittene Skills** – Biologie, Chemie, Mikrobiologie

### Zahlenkult

**Die letzte Stufe der Magie, die kaum eine Brauerin je erreichen wird ...** – Berechnungen, Rezepturen, Psi-Effizienz?

### Schankkunst – Gastronomie

**Brauereinnen sind soziale Wesen und wissen wann sie freundlich zu sein haben** - das könnte auch die Kategorie Sozial sein

### Marktschreierei – Handel und Marketing

### Nachschub





### Offene Fragen

- `?` **Psi-Punkte und Mathematik:** Skills sind passiv, zur Erhöhung des Levels verbrauchen sie immer nur EP, SchnaPsi-Punkte werden von aktiven Fähigkeiten bzw. bei Psi-Angriffen verbraucht, bzw. zerstört, so wie "Malz-Punkte" (bessere Bezeichnung?) bei Magie
  ja, Mathematik rein passiv (Boni ohne Ressourcenkosten)?
- alle Skills arbeiten rein passiv, immer Boni
- `?` **Magie vs. Psi im Kampf:** beide wirken gegen Lebewesen (Psi - Schnaps - Desinfektion - gegen Mirkobiologie), Magie (organisch, gegen höhere Lebewesen - daneben Überschneidungen
- `?` **Umwelt:** Feld-Skills (Aussaat, Ernte) vs. Anlagen-Skills (Sudhaus) — aufgeteilt Umwelt kommt zu Rohstofftechnologie, Anlagen zu Verfahrenstechnik oder Brautechnologie

- `?` **Groesse:** 12 Kategorien x ~12 Skills = ~144 Skills ist sehr ambitioniert.
  JA, konkrete Skills folgen demnächst


## Kampfsystem — Designdokument

### Übersicht

| Thema | Entscheidung |
|---|---|
| **Standardaktion** | Bump combat (Nahkampf) + Fernkampf wenn Fähigkeit vorhanden |
| **Welt-Takt im Kampf** | Andere Gegner bewegen sich alle 2 Kampfrunden (× eigene Geschwindigkeit) |
| **Entscheidung pro Zug** | Position + Ressource + Zielwahl |
| **Mehrere Gegner** | Möglich; Zielwahl per Kontextmenü |
| **Gelände** | Taktisch nutzbar, Komplexität als Grenze |
| **Gruppenbedrohung** | Status-Kombos, Schwarm+Königin, Flanking/Rückenangriff |
| **Bosse** | Phasen, Lösungszwang, Telegraphed Specials, Spawn, Umwelt |
| **Interface** | Festes Grundschema + Kontextmenü + Skill-Slots (nur im Hub bestücken) |
| **Kampf-Panel** | LP/PP/MP/Psi-Balken für Ninkasi; HP + Statuseffekte je Gegner |
| **Ressourcen** | LP, PP, MP (Magie) — Regeneration & MP-Name offen |
| **Zufall** | Schadensbandbreite + Crits + Trefferchance + Synergien |
| **Ausweichen** | Aktive Fähigkeit für Spieler und Gegner |
| **Blickrichtung** | Nötig für Rückenangriff-Mechanik |

## 2. Gebräuchliche Konzepte

### A. Klassischer Kontakt-Nahkampf

**Prinzip:**
Der Spieler bewegt sich in einen Gegner hinein oder greift angrenzend an.

**Typische Ausprägungen:**
- Bump combat: Gegen Gegner laufen = Angriff
- Expliziter Nahkampfbefehl
- Waffen mit Nahkampfreichweite 1
- Unterschiedliche Waffenprofile: Dolch, Schwert, Speer, Axt

**Warum es oft benutzt wird:**
- Sehr lesbar
- Schnell
- Ideal für Tastatursteuerung
- Passt gut zu engem Grid-Gameplay

**Varianten:**
- Fester Schaden
- Trefferwurf + Schadenswurf
- Waffen mit Bonus gegen bestimmte Rüstungen
- Gegenangriffe / Riposte

**Stärken:**
- Einfach zu verstehen
- Gute Verbindung von Bewegung und Kampf

**Schwächen:**
- Kann flach wirken, wenn nur Zahlen getauscht werden

### B. Fernkampf mit Sichtlinie

**Prinzip:**
Angriffe über Distanz, solange Ziel sichtbar ist.

**Typische Elemente:**
- Bögen, Armbrüste, Pistolen, Wurfmesser
- Reichweitenlimit
- Sichtlinie durch Wände blockiert
- Munition oder Nachladezeit

**Gebräuchliche Unterformen:**
- Soforttreffer auf Ziel
- Projektil fliegt Feld für Feld
- Richtungsfeuer statt Zielauswahl
- Streuung / Ungenauigkeit

**Interessant in Terminal-Roguelikes, weil:**
- Positionierung stark aufgewertet wird
- Deckung, Korridore und Türschwellen wichtig werden

**Häufige Balancer:**
- Munitionsknappheit
- Weniger Schaden im Nahkampf
- Vorbereitungszeit
- Geräusch zieht weitere Gegner an

### C. Magie als Ressourcen-Kampf

**Prinzip:**
Zauber sind spezialisierte Angriffe, Kontrolleffekte oder Utility mit eigener Kostenlogik.

**Sehr gebräuchliche Modelle:**
- Mana-Pool
- Spell Charges
- Cooldowns
- Verbrauchsrollen statt frei wirkbarer Magie
- HP als Magiekosten
- Vorbereitung vor dem Dungeon

**Typische Zauberarten:**
- Direktschaden
- Flächenschaden
- Debuffs
- Summons
- Teleport
- Wand erschaffen / zerstören
- Sicht, Licht, Unsichtbarkeit
- Crowd Control

**Warum beliebt:**
- Ermöglicht kreative Lösungen
- Bricht starres „ich haue zu“-Gameplay auf

### D. Spezielle Aktionen / Combat Abilities

**Prinzip:**
Neben Standardangriffen gibt es aktive Manöver.

**Sehr häufige Beispiele:**
- Stoßen / Knockback
- Sprint / Dash
- Cleave gegen mehrere Gegner
- Stun
- Disarm
- Defensive Haltung
- Überwachen / Opportunity Attack
- Warten / vorbereiteter Schlag

**Nutzen:**
- Macht Klassen oder Builds unterscheidbar
- Erzeugt Mikroentscheidungen
- Gibt Nahkampf mehr Tiefe

### E. Einzelziel vs. Mehrziel

#### Einzelziel
Klassisch bei:
- Nahkampf
- Präzisionsfernkampf
- Starken Debuffs
- Bossfights

**Gut für:**
- Prioritäten setzen
- Ressourcenmanagement
- Elite-Gegner

#### Mehrziel
Typische Formen:
- Kegel
- Linie
- Radius
- Ring
- Kettenblitz
- Spaltender Schlag
- „Trifft alle benachbarten Gegner“

**Gut für:**
- Schwarmgegner
- Raumkontrolle
- Positionsspiel

### F. Statussysteme

Sehr gebräuchlich in Roguelikes.

**Standardstatus:**
- Gift
- Brennen
- Blutung
- Verlangsamung
- Stun
- Freeze
- Blindheit
- Verwirrung
- Schlaf
- Silence
- Schwäche / Rüstungsbruch

**Starke Vorteile:**
- Macht Kampf nicht nur zu Schadensvergleich
- Gut für Build-Synergien
- Gut für Gegnertypen mit Identität

**Risiko:**
- Zu viele ähnliche Status werden unübersichtlich

### G. Gegnerauswahl per Zielcursor oder Richtung

In terminalbasierten Spielen sehr relevant.

**Gebräuchliche Modelle:**

#### 1. Automatisches Ziel
- Nächstgelegener Gegner
- Sichtbares Ziel in Richtung
- Schwächster / stärkster Gegner

**Plus:** schnell
**Minus:** weniger Kontrolle

#### 2. Richtungseingabe
- Pfeil/HJKL/Numpad bestimmt Angriffsrichtung

**Plus:** sehr terminalfreundlich
**Minus:** ungenau bei mehreren möglichen Zielen

#### 3. Zielcursor
- Cursor durch sichtbare Felder bewegen
- Enter bestätigt

**Plus:** präzise
**Minus:** langsamer

#### 4. Kontextsensitives Targeting
- System schlägt sinnvolles Ziel vor
- Tab schaltet weiter

**Oft sehr guter Kompromiss**

### H. Aktion-Ökonomie

Auch sehr gebräuchlich.

**Modelle:**
- Ein Zug = eine Aktion
- Bewegung und Angriff getrennt
- Aktionspunkte
- Zeitbasierte Systeme (schnelle Waffen handeln öfter)
- Initiativeleisten
- Energy-System

**Wirkung auf das Kampfgefühl:**
- Einfache Züge wirken sauber und roguelike-klassisch
- AP-Systeme erlauben feinere Taktik
- Zeitsysteme fühlen sich simulativer an

## 3. Weniger gebräuchliche, aber interessante Konzepte

### A. Reichweitenzonen im Nahkampf

Nicht nur angrenzend, sondern Waffenprofile über Distanz.

**Beispiele:**
- Speer trifft auf Distanz 2, nicht direkt angrenzend
- Peitsche trifft durch Verbündete hindurch
- Lanze braucht Anlauf
- Dolch ist stark nur bei Rückseite oder aus Stealth

**Effekt:**
- Macht Waffen wirklich verschieden
- Erhöht taktischen Wert von Positionen

### B. Facing / Blickrichtung

In klassischen Roguelikes seltener, aber spannend.

**Prinzip:**
- Einheit schaut in eine Richtung
- Rücken ist verwundbarer
- Schilde schützen nur frontal
- Cone-Angriffe orientieren sich an Blickrichtung

**Vorteile:**
- Taktisch reich
- Gut für Schleich- und Duellsysteme

**Nachteile:**
- Mehr Bedienaufwand
- Schwerer lesbar in ASCII

### C. Momentum / Combo-Systeme

Eher selten, aber stark.

**Ideen:**
- Treffer bauen Momentum auf
- Bewegen vor Angriff erhöht Schaden
- Wiederholte gleiche Aktion wird schwächer
- Verschiedene Aktionsfolgen erzeugen Spezialeffekte

**Beispiele:**
- Schlag → Stoß → Finisher
- Feuerstatus + Windstoß = Explosion
- Drei Nahkampftreffer laden Cleave

**Gut für:**
- Spielerische Tiefe ohne Echtzeit

### D. Geräusch als Kampfmechanik

In traditionellen Roguelikes vorhanden, aber oft nicht als volles Kampfsystem genutzt.

**Konzepte:**
- Schüsse erzeugen Lärm
- Zauber ziehen Gegner an
- Explosionen alarmieren Räume
- Leise Waffen haben strategischen Wert

**Sehr stark für:**
- Spannungsaufbau
- Entscheidung „diesen Kampf gewinne ich, aber was danach?“

### E. Gelände als aktive Waffe

Nicht nur Hindernis, sondern eigentlicher Kampfbestandteil.

**Beispiele:**
- Gegner in Feuer, Säure oder Abgründe stoßen
- Öl entzünden
- Türen blockieren
- Wasser leitet Blitz
- Eis macht Bewegung riskant
- Pflanzen brennen oder fesseln

**Besonders gut in Roguelikes, weil:**
- Grid-Systeme das klar abbilden
- ASCII/Terminal dafür reicht, wenn Symbole sauber sind

### F. Slot-basierte Spezialaktionen statt Mana

Weniger klassisch als Mana, aber oft eleganter.

**Modelle:**
- Pro Kampf 1–3 Charges
- Jede Fähigkeit belegt Ausrüstungsslot
- Karten-/Runen-Hand statt Zauberliste
- Nur vorbereitete Skills verfügbar
- Cooldowns, die an Kills oder Bewegung hängen

**Vorteil:**
- Weniger abstrakte Ressourcenverwaltung
- Entscheidungen bleiben kompakt

### G. Gegnertypen mit „Lösungszwang“

Ein Gegner ist nicht nur stärker, sondern verlangt eine andere Antwort.

**Beispiele:**
- Gepanzerter Feind: nur Stöße, Magie oder Rear-Attacks wirksam
- Beschwörer: Prioritätsziel
- Schwarm: AoE nötig
- Teleporter: Zonenkontrolle nötig
- Schildträger: frontal zäh, seitlich schwach
- Explodierender Feind: Distanz halten
- Heiler: Fokusfeuer wichtig

**Das ist extrem wertvoll**, weil daraus echte Taktik entsteht.

### H. Angriffsvorhersage / Telegraphed Turns

Eher bekannt aus modernen Taktik-Roguelites, in klassischen Roguelikes weniger Standard.

**Prinzip:**
- Gegner zeigen an, was sie nächste Runde tun
- Spieler reagiert mit Positionierung, Interrupt, Block oder Lockmittel

**Effekt:**
- Weniger Zufallsfrust
- Mehr Planung
- Sehr gut für schweres, aber faires Gameplay

### I. Simultane oder halb-simultane Auflösung

Seltener in Terminal-Roguelikes.

**Modelle:**
- Spieler und Gegner wählen Aktionen, dann werden alle aufgelöst
- Alle handeln nach Initiative fast gleichzeitig
- Befehle als „Programmierung“ für die nächsten Züge

**Spannend, aber schwierig:**
- Sehr tief
- Schwerer zu lesen
- Fehler fühlen sich härter an

### J. Körperteil- oder Trefferzonen-System

Eher selten, aber atmosphärisch stark.

**Beispiele:**
- Kopf, Torso, Arme, Beine
- Armverletzung senkt Trefferchance
- Beinverletzung reduziert Bewegung
- Auge zerstört Sicht
- Gegner verlieren Fähigkeiten durch Teilbeschädigung

**Gut für:**
- Simulation
- Horror / Survival
- sehr spezifische Build-Systeme

**Problem:**
- Hohe Komplexität

### K. Haltungssysteme / Stances

Weniger gebräuchlich, aber gut für Nahkampfklassen.

**Beispiele:**
- Offensive Haltung
- Defensive Haltung
- Reichweitenhaltung
- Konterhaltung
- Flächenhaltung

**Kann bewirken:**
- andere Reichweite
- andere AP-Kosten
- andere Verteidigung
- Spezialreaktionen

### L. Risiko-Zauber / instabile Magie

Interessant für Roguelites.

**Konzepte:**
- Magie erzeugt Korruption
- Überladung kann Explosion auslösen
- Zauber mutieren Gegner
- Mächtige Effekte haben unkontrollierbare Nebeneffekte
- Fail-Forward statt reines Scheitern

**Das gibt Magie Identität**, statt nur Fernkampfschaden in anderer Farbe zu sein.

## 4. Sehr brauchbare Muster für Gegnerauswahl

Weil das in Terminalspielen oft unterschätzt wird:

### Für schnelle Spiele
- Nahkampf: automatisch per Bewegung
- Fernkampf: Autoziel + Tab zum Wechseln
- Zauber: Richtung oder kleiner Zielcursor

### Für taktische Spiele
- Cursor für alles
- Vorschau: Trefferchance, Schaden, AoE, Kollateralschaden
- Markierung betroffener Felder

### Für viele Gegner gleichzeitig
- Zieltypen statt Einzelziel:
  - nächster Gegner
  - stärkster sichtbarer Gegner
  - Gegnergruppe
  - freie Kachel
  - Linie in Richtung

Das reduziert Interface-Reibung stark.

## 5. Gute Mehrziel-Formen für Terminal-Roguelikes

Einige Formen sind besonders lesbar:

- **Linie**
  Sehr gut für Blitz, Speerstoß, Laser

- **Kegel**
  Gut für Atemwaffen, Schrot, Furcht

- **Kreis/Radius**
  Klassisch für Feuerball, Bombe

- **Kette**
  Gut für Blitzmagie, Seuchen, Markierungen

- **Benachbarte Felder**
  Perfekt für Cleave, Wirbelangriff

- **Durchdringendes Projektil**
  Trifft alle Gegner in einer Reihe

- **Ziel + Splash**
  Hauptziel stark, Umfeld schwach

Lesbarkeit ist wichtiger als exotische Form.

## 6. Mischformen, die oft besonders gut funktionieren

### A. Bump-Nahkampf + gezielte Spezialaktionen
Sehr klassisch und robust.

- Standardkampf schnell
- Tiefe entsteht durch wenige aktive Skills
- Gut für klare Tastaturbedienung

### B. Fernkampf + Lärm + Munition
Sehr stark für Spannung.

- Fernkampf ist mächtig
- Aber nicht gratis
- Jeder Schuss hat Folgekosten

### C. Magie + Umweltinteraktion
Stärker als reine Schadenszauber.

- Eis friert Wasser
- Feuer entzündet Öl
- Blitz trifft nasse Gegner härter
- Wind verschiebt Gaswolken

### D. Einzelziel-Fokus + Schwarmkontrolle
Gute Build-Differenzierung.

- Assassin/Bogenschütze eliminiert Schlüsselziel
- Tank/Magier kontrolliert Gruppen

### E. Telegraphed Enemies + harte Specials
Fair und taktisch.

- Gegner kündigen Großangriffe an
- Spieler darf clever reagieren
- Schwierigkeit steigt, Frust sinkt

## 7. Konzepte, die oft problematisch sind

Nicht schlecht, aber in Terminal-Roguelikes schnell schwierig:

### Zu viele Trefferwürfe und Unterwürfe
Beispiel:
- Hit roll
- Crit roll
- Armor roll
- Dodge roll
- Block roll
- Status roll

Das kann Kampf undurchsichtig machen.

### Zu viele fast gleiche Fähigkeiten
- Slash I, Slash II, Heavy Slash, Strong Slash, Power Slash
Besser wenige Fähigkeiten mit klarer Identität.

### Präzisionszielung ohne gute UI
Ein tolles System scheitert schnell an umständlicher Cursorbedienung.

### Mehrziel-Systeme ohne klare Vorschau
Wenn der Spieler nicht sofort sieht, was betroffen ist, leidet Lesbarkeit.

## 8. Besonders interessante seltenere Ideen

Ein paar Konzepte mit viel Potenzial:

### 1. Kampf über Distanzkontrolle statt rohen Schaden
- Gegner binden
- Gegner trennen
- Gegner verschieben
- Türen schließen
- Räume aufteilen

### 2. „Soft Lock“-Kampf
Nicht töten, sondern:
- betäuben
- vertreiben
- umleiten
- verbannen
- isolieren

### 3. Reaktive Kämpfe
- Gegenangriffe
- Fallen im Zug des Gegners
- vorbereitete Schüsse
- Schildhaltung gegen Projektilrichtung

### 4. Intent-basierte AI-Kämpfe
Gegner haben lesbare Absichten:
- rush
- flank
- halten
- casten
- beschwören
- retreaten

### 5. Asymmetrische Ressourcen
- Nahkampf nutzt Stamina
- Fernkampf nutzt Munition
- Magie nutzt Hitze/Korruption/Fokus
- Spezialaktionen laden sich durch Risiko auf

Das macht Systeme differenzierter als „alles kostet Mana“.

## 9. Ein brauchbares Raster für die eigene Entwurfsarbeit

Wenn du so ein System entwerfen willst, helfen diese Fragen:

1. **Was ist die Standardaktion?**
   Bump, expliziter Angriff, Zielcursor?

2. **Was ist die Hauptentscheidung pro Zug?**
   Position, Ziel, Ressource, Timing?

3. **Wie wichtig ist Gelände?**
   Nur Hindernis oder zentrale Waffe?

4. **Wie werden Gruppen gefährlich?**
   Zahl, Flanking, Fernkampf, Status, Beschwörung?

5. **Wie werden Eliten/Bosse interessant?**
   Nur HP-Schwamm oder mit Mechanik?

6. **Wie viele aktive Fähigkeiten verträgt das Interface?**
   Terminalspiele profitieren meist von weniger, klareren Optionen.

7. **Ist der Kampf lesbar in 1–2 Sekunden Blickzeit?**
   Das ist oft wichtiger als Komplexität.

## 10. Kompakte System-Baukästen

### Sehr klassisch
- Bump-Nahkampf
- Fernkampf mit Munition
- Mana-Zauber
- Einzelziel + Radiuszauber
- Status wie Gift/Brennen
- Zielauswahl per Tab/Cursor

### Taktisch-modern
- Aktionspunkte
- Telegraphs
- Push/Pull
- Umweltgefahren
- Kegel/Linienangriffe
- klare Gegnerrollen

### Ungewöhnlich
- Facing
- Haltungssystem
- Geräuschsimulation
- Körperzonen
- Momentum/Combo
- instabile Magie
- simultane Auflösung

## 11. Empfehlenswerte Prioritäten für ein gutes Terminal-Kampfsystem

Wenn es nicht nur vollständig, sondern auch gut sein soll, sind diese Dinge meist am wichtigsten:

- **Lesbare Zielwahl**
- **starke Positionsrelevanz**
- **wenige, markante Spezialaktionen**
- **klare Gegnerrollen**
- **Mehrzieloptionen mit klarer Vorschau**
- **Umwelt oder Status als zweite Ebene**
- **Ressourcen, die Entscheidungen erzwingen**

Weniger wichtig sind meist:
- extrem viele Waffenwerte
- zu feine Schadenssimulation
- riesige Skilllisten ohne klaren Einsatzbereich

Ich kann daraus als Nächstes auch eine **systematische Taxonomie als Tabelle** bauen, etwa mit Spalten wie:
`Konzept | gebräuchlich? | Bedienaufwand | taktische Tiefe | gut für Terminal? | typische Probleme`.
