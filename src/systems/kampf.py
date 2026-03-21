"""Kampfsystem: rundenbasierter Kampf fuer Battle Ninkasi.

Ablauf einer Runde (runde_ausfuehren):
    1. Regeneration des Gegners
    2. Status-Effekte ticken (DoT-Schaden, Dauer reduzieren)
    3. Spieler greift an
    4. Gegner greift an (zufaelliger Angriff aus seiner Liste)
    5. Sieg/Niederlage pruefen

Status-Effekte (z.B. dot_biologisch, psi_malus_pct) werden in KampfZustand
als Listen von Dicts gespeichert: {"typ": "...", "wert": X, "runden": N}
DoT-Effekte (Typ beginnt mit "dot_") ziehen pro Runde Schaden ab.
Andere Effekte (Debuffs) werden nur mitgezaehlt — auswertende Systeme
(z.B. Psi-System) lesen sie bei Bedarf aus spieler_effekte.

AoE-Angriffe werden vorerst wie Einzelangriffe behandelt — das aendert sich
wenn Positionierung und Schwarm-Logik implementiert sind.
"""

import random


# ---------------------------------------------------------------------------
# Kampfzustand
# ---------------------------------------------------------------------------

class KampfZustand:
    """Haelt den gesamten Zustand eines laufenden Kampfes."""

    def __init__(self, spieler, gegner):
        self.spieler = spieler
        self.gegner = gegner
        self.spieler_effekte = []  # Aktive Status-Effekte auf dem Spieler
        self.gegner_effekte = []   # Aktive Status-Effekte auf dem Gegner
        self.log = []              # Texte der aktuellen Runde (fuer Anzeige)
        self.runde = 0
        self.beendet = False
        self.ergebnis = None       # "sieg" oder "niederlage" nach Kampfende


# ---------------------------------------------------------------------------
# Schaden
# ---------------------------------------------------------------------------

def schaden_berechnen(roh_schaden, verteidigung, resistenzen, schadenstyp):
    """Berechnet effektiven Schaden nach Verteidigung und Resistenz.

    Verteidigung: flacher Abzug vom Rohschaden (mindestens 0).
    Resistenz:    prozentuale Reduktion je Schadenstyp (0.0 = keine, 1.0 = immun).
                  Werte aus gegner.resistenzen, z.B. {"biologisch": 0.5}.
    """
    nach_verteidigung = max(0, roh_schaden - verteidigung)
    resistenz = resistenzen.get(schadenstyp, 0.0)
    return max(0, round(nach_verteidigung * (1.0 - resistenz)))


# ---------------------------------------------------------------------------
# Status-Effekte
# ---------------------------------------------------------------------------

def _effekt_hinzufuegen(effekte_liste, effekt_def):
    """Fuegt einen Status-Effekt zur Effekte-Liste hinzu.

    effekt_def muss "typ", "wert" und "dauer" enthalten (aus Angriffs-JSON).
    Stapelbarkeit wird hier vereinfacht: alle Effekte werden gestapelt.
    Nicht-stapelbare Effekte (spaetere Erweiterung): Dauer auffrischen statt stapeln.
    """
    effekte_liste.append({
        "typ": effekt_def["typ"],
        "wert": effekt_def["wert"],
        "runden": effekt_def["dauer"],
    })


def _effekte_tick(effekte_liste, ziel_ist_spieler, zst):
    """Wendet alle aktiven Status-Effekte an und verringert ihre Dauer um 1.

    DoT-Effekte (Typ beginnt mit "dot_"): ziehen Schaden ab.
    Andere Effekte (Debuffs): nur Dauer reduzieren, keine direkte Aktion.

    Gibt True zurueck wenn das Ziel durch DoT-Schaden auf 0 LP/HP faellt.
    """
    verbleibend = []
    for e in effekte_liste:
        if e["typ"].startswith("dot_"):
            schaden = e["wert"]
            if ziel_ist_spieler:
                zst.spieler.lp = max(0, zst.spieler.lp - schaden)
                zst.log.append(
                    f"  {e['typ']}: {schaden} Schaden "
                    f"(LP {zst.spieler.lp}/{zst.spieler.lp_max})"
                )
            else:
                zst.gegner.hp = max(0, zst.gegner.hp - schaden)
                zst.log.append(
                    f"  {e['typ']}: {schaden} Schaden "
                    f"({zst.gegner.name} HP {zst.gegner.hp}/{zst.gegner.hp_max})"
                )

        e["runden"] -= 1
        if e["runden"] > 0:
            verbleibend.append(e)
        else:
            zst.log.append(f"  {e['typ']} klingt ab.")

    effekte_liste[:] = verbleibend

    if ziel_ist_spieler:
        return zst.spieler.lp <= 0
    else:
        return zst.gegner.hp <= 0


def aktiver_effekt_wert(effekte_liste, typ):
    """Summiert den Gesamtwert aller aktiven Effekte eines bestimmten Typs.

    Nuetzlich fuer Debuff-Auswertung ausserhalb des Kampfsystems,
    z.B.: aktiver_effekt_wert(zst.spieler_effekte, "psi_malus_pct") -> 30
    Gibt 0 zurueck wenn kein solcher Effekt aktiv ist.
    """
    return sum(e["wert"] for e in effekte_liste if e["typ"] == typ)


# ---------------------------------------------------------------------------
# Angriffe
# ---------------------------------------------------------------------------

def _spieler_greift_an(zst):
    """Spieler fuehrt seinen Basisangriff aus.

    Platzhalter bis das Waffensystem existiert.
    Dann wird hier der ausgewaehlte Waffen-Angriff eingesetzt.
    """
    schaden = schaden_berechnen(
        zst.spieler.basis_schaden,
        zst.gegner.verteidigung,
        zst.gegner.resistenzen,
        "nah",
    )
    zst.gegner.hp = max(0, zst.gegner.hp - schaden)
    zst.log.append(
        f"{zst.spieler.name} greift an: {schaden} Schaden "
        f"({zst.gegner.name} HP {zst.gegner.hp}/{zst.gegner.hp_max})"
    )


def _gegner_greift_an(zst):
    """Gegner waehlt zufaellig einen Angriff und fuehrt ihn aus.

    AoE-Angriffe (ziel != "einzel") werden vorerst wie Einzelangriffe behandelt.
    Schwarm-Logik folgt spaeter.
    """
    if not zst.gegner.angriffe:
        return

    angriff = random.choice(zst.gegner.angriffe)
    schaden = schaden_berechnen(
        angriff["schaden"],
        zst.spieler.verteidigung,
        {},
        angriff["typ"],
    )
    zst.spieler.lp = max(0, zst.spieler.lp - schaden)
    zst.log.append(
        f"{zst.gegner.name}: {angriff['name']} - {schaden} Schaden "
        f"(LP {zst.spieler.lp}/{zst.spieler.lp_max})"
    )

    for e in angriff.get("effekte", []):
        if "dauer" in e:
            _effekt_hinzufuegen(zst.spieler_effekte, e)
            zst.log.append(f"  -> {e['typ']} fuer {e['dauer']} Runden")


# ---------------------------------------------------------------------------
# Sieg / Niederlage
# ---------------------------------------------------------------------------

def _sieg(zst):
    zst.beendet = True
    zst.ergebnis = "sieg"
    zst.spieler.ep_hinzufuegen(zst.gegner.ep_beute)
    zst.log.append(f"{zst.gegner.name} ist besiegt! +{zst.gegner.ep_beute} EP")


def _niederlage(zst):
    zst.beendet = True
    zst.ergebnis = "niederlage"
    zst.log.append(f"{zst.spieler.name} ist besiegt.")


# ---------------------------------------------------------------------------
# Runde
# ---------------------------------------------------------------------------

def abschlag_ausfuehren(zst):
    """Gegner fuehrt einen Abschlagsangriff aus, wenn der Spieler flieht.

    Gibt True zurueck wenn der Spieler dabei stirbt.
    """
    zst.log.clear()
    zst.log.append("--- Abschlag ---")
    _gegner_greift_an(zst)
    return zst.spieler.lp <= 0


def runde_ausfuehren(zst):
    """Fuehrt eine vollstaendige Kampfrunde aus und aktualisiert zst.

    Reihenfolge:
      1. Regeneration (Gegner heilt sich um regen_hp)
      2. Status-Effekte ticken — DoT schadet, Dauer sinkt, abgelaufene fallen weg
      3. Spieler greift an
      4. Gegner greift an
    Nach jedem toedlichen Schritt wird sofort abgebrochen (zst.beendet = True).
    """
    if zst.beendet:
        return

    zst.runde += 1
    zst.log.clear()
    zst.log.append(f"--- Runde {zst.runde} ---")

    # 1. Regeneration
    if zst.gegner.regen_hp > 0 and zst.gegner.hp > 0:
        geheilt = min(zst.gegner.regen_hp, zst.gegner.hp_max - zst.gegner.hp)
        zst.gegner.hp += geheilt
        if geheilt > 0:
            zst.log.append(f"  {zst.gegner.name} regeneriert {geheilt} HP.")

    # 2. Status-Effekte
    if _effekte_tick(zst.gegner_effekte, False, zst):
        zst.log.append(f"{zst.gegner.name} stirbt an Status-Effekten.")
        _sieg(zst)
        return

    if _effekte_tick(zst.spieler_effekte, True, zst):
        zst.log.append(f"{zst.spieler.name} stirbt an Status-Effekten.")
        _niederlage(zst)
        return

    # 3. Spieler greift an
    _spieler_greift_an(zst)
    if zst.gegner.hp <= 0:
        _sieg(zst)
        return

    # 4. Gegner greift an
    _gegner_greift_an(zst)
    if zst.spieler.lp <= 0:
        _niederlage(zst)
