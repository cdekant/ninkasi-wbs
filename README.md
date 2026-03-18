# Battle Ninkasi (bn)

Roguelite-Terminal-RPG. Du braust Bier. Es ist gefaehrlich.

## Spielprinzip

Kaempfe dich durch alle Stufen der Bierherstellung — von der Aussaat bis zum
Verkauf. Jedes Level ist eine andere Etappe der Braukette, mit zufaelliger
Karte und passenden Gegnern.

**Tod:** Neustart am Anfang des aktuellen Levels — EP und Skills bleiben
erhalten (Roguelite). Der Zoigl-Stern (Brauerstern) mit seinen 6 Stufen ist
das Fortschrittssymbol des Spiels.

## Voraussetzungen

- Python 3.13+
- tcod (`pip install tcod`)

## Starten

```
python main.py
```

## Steuerung

| Taste | Aktion |
|---|---|
| W / Pfeil oben | Hoch |
| S / Pfeil unten | Runter |
| A / Pfeil links | Links |
| D / Pfeil rechts | Rechts |
| LEERTASTE / ENTER | Kampfrunde ausfuehren (im Kampf) |
| TAB | Menue oeffnen/wechseln |
| ESC | Menue schliessen |
| Q | Beenden |

## Dokumentation

Siehe `HANDBUCH.md` fuer das vollstaendige Spieler-Handbuch.

## Status

Fruehe Entwicklung. Laeufig mit:

- Bewegung auf prozedural generierter Karte (BSP, Gaerkeller-Demo)
- EP-System und Skill-Menue (TAB)
- Gegner auf der Karte — Anlaufen startet rundenbasierten Kampf
- Kampf-Panel mit HP-Balken, Kampf-Log und Status-Effekten (DoT, Debuffs)
- Tod-Reset: LP/PP auf Maximum, neue Karte, neue Gegner
