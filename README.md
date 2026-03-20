# Ninkasi – Wiedergeburt der Bier-Schlächterin

Roguelite-Terminal-RPG. Du bist die als intoxierte Erynne auferstandene mesopotamische Biergöttin Ninkasi. Die Welt ist verrückt geworden und du musst dich gegen verrückte Anti-Alkoholiker, Zombie-Lobbyisten und jede Menge mutierte Schleime zur Wehr setzen. Am Ende musst du das Amok gelaufene vegane Konstrukt Prohibitus besiegen und der Welt durch Bier Frieden bringen.

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
| TAB | Menue oeffnen/wechseln (auch im Kampf: Inventar) |
| ESC | Menue schliessen |
| Q | Beenden |

## Dokumentation

Siehe `HANDBUCH.md` fuer das vollstaendige Spieler-Handbuch.

## Status

Fruehe Entwicklung. Laeufig mit:

- Level 1 Pflanzenzuechtung: Raster-Karte (3×2-Gitter, Gewaechshaus-Anmutung)
- Zonen-System: 5–7 Zonen pro Level-Run, jede Zone etwas schwieriger (+5 % Staerke, +2 Gegner)
- HP/PP/MP werden bei Hub-Rueckkehr vollstaendig aufgefuellt
- EP-System und Skill-Menue (TAB im Hub); 15 Skill-Kategorien (Entwurf)
- Gegner auf der Karte — Anlaufen startet rundenbasierten Kampf
- UI-Layout: Statuszeile oben (LP/PP/MP-Balken + EP), Spielkarte (59 Zeilen), Nachrichtenlog unten (5 Zeilen), kontextsensitive Shortcuts — Fenster 1920×1080 (120×67 Kacheln, 16 px)
- Schwebendes Kampffenster (80×20 Kacheln, zentriert): HP-Balken, scrollender Kampf-Log (13 Zeilen), Status-Effekte (DoT, Debuffs)
- Sichtfeld (FOV, Radius 8) und Fog of War — nur Erkundetes bleibt sichtbar
- Gegner-KI: territorial, verfolgen, flucht; Geschwindigkeit und flucht_hp_pct je Typ
- Tod-Reset: LP/PP auf Maximum, neue Karte, neue Gegner
- Speichern/Laden: automatisch beim Hub-Eintritt, nach Tod und beim Beenden
- Inventar-System: Loot-Drop nach Kampf, Auto-Pickup, TAB → Inventar (Hub + Dungeon + im Kampf)
- Custom-Tile-System: eigene 16×16 PNG-Sprites (Braukessel, Pflanze, Fenster, Fenstergitter); `src/tiles.py` ist einzige Quelle der Wahrheit für Tile-Codepoints
- Pflanzenzuechtung: Wände vollständig mit Fenster-/Fenstergitter-Tiles gefüllt (Gewächshaus-Optik), FENSTER_GITTER grünlich eingefärbt
