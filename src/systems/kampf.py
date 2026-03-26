"""Kampfberechnungen fuer Battle Ninkasi.

Dieses Modul ist zustandslos: Funktionen erhalten Entitaet-Objekte
und geben Log-Zeilen als Liste zurueck. Spielzustand liegt in game.py.

    schaden_berechnen        -- Schaden nach Verteidigung und Resistenz
    effekt_anwenden          -- Status-Effekt auf Entitaet eintragen
    effekte_tick             -- Effekte einer Entitaet abarbeiten (DoT, Dauer -1)
    regen_tick               -- HP-Regeneration einer Entitaet
    aktiver_effekt_wert      -- Summe aktiver Effekte eines Typs
    nahkampf_angriff         -- Angreifer schlaegt Ziel im Nahkampf
    spieler_fernkampf_angriff -- Spieler greift Ziel aus der Ferne an
    gegner_fernkampf_angriff  -- Gegner greift Ziel aus der Ferne an
"""

import random


# ---------------------------------------------------------------------------
# Schaden
# ---------------------------------------------------------------------------

def schaden_berechnen(roh_schaden, verteidigung, resistenzen, schadenstyp):
    """Berechnet effektiven Schaden nach Verteidigung und Resistenz.

    Verteidigung: flacher Abzug vom Rohschaden (mindestens 0).
    Resistenz:    prozentuale Reduktion je Schadenstyp (0.0 = keine, 1.0 = immun).
    """
    nach_verteidigung = max(0, roh_schaden - verteidigung)
    resistenz = resistenzen.get(schadenstyp, 0.0)
    return max(0, round(nach_verteidigung * (1.0 - resistenz)))


# ---------------------------------------------------------------------------
# Status-Effekte
# ---------------------------------------------------------------------------

def effekt_anwenden(entitaet, effekt_def):
    """Fuegt einen Status-Effekt zur aktive_effekte-Liste der Entitaet hinzu.

    effekt_def muss 'typ', 'wert' und 'dauer' enthalten (aus Angriffs-JSON).
    """
    entitaet.aktive_effekte.append({
        "typ":    effekt_def["typ"],
        "wert":   effekt_def["wert"],
        "runden": effekt_def["dauer"],
    })


def effekte_tick(entitaet):
    """Wendet alle aktiven Effekte der Entitaet an und verringert Dauer um 1.

    DoT-Effekte (Typ beginnt mit 'dot_'): ziehen HP ab.
    Andere Effekte (Debuffs): nur Dauer reduzieren.
    Gibt Liste von Log-Zeilen zurueck.
    """
    log = []
    verbleibend = []
    for e in entitaet.aktive_effekte:
        if e["typ"].startswith("dot_"):
            schaden = e["wert"]
            entitaet.hp = max(0, entitaet.hp - schaden)
            log.append(
                f"  {e['typ']}: {schaden} Schaden "
                f"({entitaet.name} {entitaet.hp}/{entitaet.hp_max} HP)"
            )
        e["runden"] -= 1
        if e["runden"] > 0:
            verbleibend.append(e)
        else:
            log.append(f"  {e['typ']} klingt ab.")
    entitaet.aktive_effekte[:] = verbleibend
    return log


def regen_tick(entitaet):
    """Regeneriert HP gemaess regen_hp-Attribut der Entitaet.

    Gibt eine Log-Zeile zurueck wenn geheilt wurde, sonst None.
    """
    regen = getattr(entitaet, "regen_hp", 0)
    if regen > 0 and entitaet.lebt and entitaet.hp < entitaet.hp_max:
        geheilt = min(regen, entitaet.hp_max - entitaet.hp)
        entitaet.hp += geheilt
        return f"  {entitaet.name} regeneriert {geheilt} HP."
    return None


def aktiver_effekt_wert(entitaet, typ):
    """Summiert den Gesamtwert aller aktiven Effekte eines bestimmten Typs.

    Nuetzlich fuer Debuff-Auswertung, z.B. psi_malus_pct.
    Gibt 0 zurueck wenn kein solcher Effekt aktiv ist.
    """
    return sum(e["wert"] for e in entitaet.aktive_effekte if e["typ"] == typ)


# ---------------------------------------------------------------------------
# Angriff
# ---------------------------------------------------------------------------

def nahkampf_angriff(angreifer, ziel):
    """Angreifer schlaegt Ziel im Nahkampf.

    Hat der Angreifer Angriffs-Definitionen (Gegner), wird einer zufaellig
    gewaehlt. Hat er keine (unbewaffneter Spieler), wird basis_schaden mit
    Schadenstyp 'nah' verwendet.
    Gibt Liste von Log-Zeilen zurueck.
    """
    log = []
    resistenzen = getattr(ziel, "resistenzen", {})

    if angreifer.angriffe:
        nah_angriffe = [a for a in angreifer.angriffe if a.get("reichweite", 1) <= 1]
        angriff = random.choice(nah_angriffe if nah_angriffe else angreifer.angriffe)
        schaden = schaden_berechnen(
            angriff["schaden"], ziel.verteidigung, resistenzen, angriff["typ"]
        )
        ziel.hp = max(0, ziel.hp - schaden)
        log.append(
            f"{angreifer.name}: {angriff['name']} \u2014 {schaden} Schaden "
            f"({ziel.name} {ziel.hp}/{ziel.hp_max} HP)"
        )
        for e in angriff.get("effekte", []):
            if "dauer" in e:
                effekt_anwenden(ziel, e)
                log.append(f"  {e['typ']} fuer {e['dauer']} Runden")
    else:
        schaden = schaden_berechnen(
            angreifer.basis_schaden, ziel.verteidigung, resistenzen, "nah"
        )
        ziel.hp = max(0, ziel.hp - schaden)
        log.append(
            f"{angreifer.name} greift an \u2014 {schaden} Schaden "
            f"({ziel.name} {ziel.hp}/{ziel.hp_max} HP)"
        )
    return log


def spieler_fernkampf_angriff(spieler, ziel, angriff_eintrag):
    """Spieler greift ein Ziel aus der Ferne an.

    angriff_eintrag enthaelt schon berechnete Felder:
        name, schaden_wert, schaden_typ, typ, (item_def nur fuer wurfwaffe)
    Ressourcen-Abzug erfolgt in game.py.
    Gibt Liste von Log-Zeilen zurueck.
    """
    log = []
    resistenzen = getattr(ziel, "resistenzen", {})
    schaden = schaden_berechnen(
        angriff_eintrag["schaden_wert"],
        ziel.verteidigung,
        resistenzen,
        angriff_eintrag["schaden_typ"],
    )
    ziel.hp = max(0, ziel.hp - schaden)
    log.append(
        f"{spieler.name} [{angriff_eintrag['name']}] \u2192 {schaden} Schaden "
        f"({ziel.name} {ziel.hp}/{ziel.hp_max} HP)"
    )
    # Effekte der Wurfwaffe (falls vorhanden)
    item_def = angriff_eintrag.get("item_def")
    if item_def:
        for e in item_def.get("effekte", []):
            if "dauer" in e:
                effekt_anwenden(ziel, e)
                log.append(f"  {e['typ']} fuer {e['dauer']} Runden")
    return log


def gegner_fernkampf_angriff(angreifer, ziel):
    """Gegner greift Ziel aus der Ferne an.

    Waehlt zufaellig einen Angriff mit reichweite > 1.
    Gibt Liste von Log-Zeilen zurueck.
    """
    log = []
    fern_angriffe = [a for a in angreifer.angriffe if a.get("reichweite", 1) > 1]
    if not fern_angriffe:
        return log
    angriff = random.choice(fern_angriffe)
    resistenzen = getattr(ziel, "resistenzen", {})
    schaden = schaden_berechnen(
        angriff["schaden"], ziel.verteidigung, resistenzen, angriff["typ"]
    )
    ziel.hp = max(0, ziel.hp - schaden)
    log.append(
        f"{angreifer.name}: {angriff['name']} (Fern) \u2014 {schaden} Schaden "
        f"({ziel.name} {ziel.hp}/{ziel.hp_max} HP)"
    )
    for e in angriff.get("effekte", []):
        if "dauer" in e:
            effekt_anwenden(ziel, e)
            log.append(f"  {e['typ']} fuer {e['dauer']} Runden")
    return log
