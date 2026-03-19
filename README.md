# Ninkasi – Wiedergeburt der Bier-Schlächterin

Roguelite-Terminal-RPG. Du bist die als intoxierte Erynne auferstandene mesopotamische Biergöttin Ninkasi. Die Welt ist verrückt geworden und du musst dich gegen verrückte Anti-Alkoholiker, Zombie-Lobbyisten und jede Menge mutierte Schleime zur Wehr setzen. Am Ende musst du das Amok gelaufene vegane Konstrukt Nüchternikum besiegen und der Welt durch Bier Frieden bringen.

Kaempfe dich durch alle Stufen der Wertschöpfungskette — von der Aussaat bis zum
Getränkefachgroßhandel. Jedes Level ist eine andere Etappe der Braukette, mit zufälliger Karte und passenden (und unpassenden) Gegnern.

## Spielprinzip

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
- Sichtfeld (FOV, Radius 8) und Fog of War — nur Erkundetes bleibt sichtbar
- Gegner-KI: territorial, verfolgen, flucht; Geschwindigkeit und flucht_hp_pct je Typ
- Tod-Reset: LP/PP auf Maximum, neue Karte, neue Gegner
- Speichern/Laden: automatisch beim Hub-Eintritt, nach Tod und beim Beenden; Startbildschirm erkennt Speicherstand ("Weiter spielen" / "Neues Spiel")
