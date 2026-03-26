"""Skill-Logik: laden, pruefen, kaufen."""

import json
import os

# Kategorie-Definitionen aus skills.json (primaer/sekundaer-Eigenschafts-Mapping).
# Wird von lade_skills() befuellt und von kosten_fuer_stufe() genutzt.
_alle_kategorien = []


def lade_effekttypen():
    """Laedt alle bekannten Effekttypen aus data/effekttypen.json.
    Gibt ein Dictionary {typ: definition} zurueck.
    """
    pfad = os.path.join(os.path.dirname(__file__), "..", "..", "data", "effekttypen.json")
    pfad = os.path.normpath(pfad)
    with open(pfad, encoding="utf-8") as f:
        return json.load(f)


def lade_skills():
    """Laedt alle Skill-Definitionen aus data/skills.json.
    Gibt ein Dictionary {skill_id: skill_definition} zurueck.
    Prueft ob alle verwendeten Effekttypen in effekttypen.json bekannt sind.
    """
    pfad = os.path.join(os.path.dirname(__file__), "..", "..", "data", "skills.json")
    pfad = os.path.normpath(pfad)
    with open(pfad, encoding="utf-8") as f:
        daten = json.load(f)

    bekannte_typen = lade_effekttypen()
    for skill in daten["skills"]:
        for effekt in skill["effekte"]:
            for w in effekt.get("werte", []):
                if w["typ"] not in bekannte_typen:
                    raise ValueError(
                        f"Unbekannter Effekttyp '{w['typ']}' in Skill '{skill['id']}' "
                        f"(Stufe {effekt['stufe']}). Bitte in data/effekttypen.json eintragen."
                    )
            w = effekt.get("wert")
            if w and w["typ"] not in bekannte_typen:
                raise ValueError(
                    f"Unbekannter Effekttyp '{w['typ']}' in Skill '{skill['id']}' "
                    f"(Stufe {effekt['stufe']}). Bitte in data/effekttypen.json eintragen."
                )

    global _alle_kategorien
    _alle_kategorien = daten.get("kategorien", [])
    return {skill["id"]: skill for skill in daten["skills"]}


def eigenschafts_reduktion(punkte, stufen_config):
    """Berechnet die prozentuale Reduktion (0.0 bis 1.0) fuer eine Eigenschaftspunktzahl.

    punkte        -- int: Punkte in der Eigenschaft
    stufen_config -- Liste aus config.py (EIGENSCHAFT_REDUKTION_PRIMAER o. SEKUNDAER)
    """
    gesamt_pct = 0.0
    bisher = 0
    for stufe in stufen_config:
        grenze   = stufe["bis_punkt"]
        rate     = stufe["pct_pro_punkt"]
        in_stufe = max(0, min(punkte, grenze) - bisher)
        gesamt_pct += in_stufe * rate
        bisher = grenze
        if punkte <= grenze:
            break
    return gesamt_pct / 100.0


def kosten_fuer_stufe(basis_kosten, stufe, kategorie_name, spieler):
    """Berechnet EP-Kosten nach Basis-Formel und Eigenschafts-Reduktion.

    Faellt auf stufen_kosten() zurueck wenn keine Kategorie-Definition gefunden wird
    oder kein Spieler uebergeben wurde.
    """
    import config
    basis = stufen_kosten(basis_kosten, stufe)
    if spieler is None:
        return basis
    kat_def = next((k for k in _alle_kategorien if k["name"] == kategorie_name), None)
    if kat_def is None:
        return basis
    p_prim = spieler.eigenschaften.get(kat_def["primaer"], 0)
    p_sek  = spieler.eigenschaften.get(kat_def["sekundaer"], 0)
    reduktion = (
        eigenschafts_reduktion(p_prim, config.EIGENSCHAFT_REDUKTION_PRIMAER)
        + eigenschafts_reduktion(p_sek,  config.EIGENSCHAFT_REDUKTION_SEKUNDAER)
    )
    reduktion = min(reduktion, config.EIGENSCHAFT_REDUKTION_MAX)
    minimum   = basis * (1.0 - config.EIGENSCHAFT_REDUKTION_MAX)
    return int(max(basis * (1.0 - reduktion), minimum) + 0.5)


def stufen_kosten(basis_kosten, stufe):
    """Berechnet die EP-Kosten fuer eine bestimmte Stufe.
    Formel: basis * 3,5^(stufe-1), gerundet
    Stufe 1: basis, Stufe 2: basis*3,5, ..., Stufe 6: basis*3,5^5
    """
    return int(basis_kosten * (3.5 ** (stufe - 1)) + 0.5)


def voraussetzungen_erfuellt(spieler, skill_def):
    """Prueft ob alle Voraussetzungen eines Skills erfuellt sind.
    Gibt (True, '') oder (False, Meldungstext) zurueck.
    """
    for vorraussetzung in skill_def.get("voraussetzungen", []):
        benoetigt_id = vorraussetzung["id"]
        benoetigt_stufe = vorraussetzung["stufe"]
        aktuelle_stufe = spieler.skill_stufe(benoetigt_id)
        if aktuelle_stufe < benoetigt_stufe:
            return False, f"Benoetigt: {benoetigt_id} Stufe {benoetigt_stufe} (du hast Stufe {aktuelle_stufe})"
    return True, ""


def kann_lernen(spieler, skill_id, alle_skills):
    """Prueft ob ein Skill gelernt werden kann.
    Gibt (True, '') oder (False, Meldungstext) zurueck.
    """
    if skill_id not in alle_skills:
        return False, f"Unbekannter Skill: {skill_id}"

    skill_def = alle_skills[skill_id]
    aktuelle_stufe = spieler.skill_stufe(skill_id)

    if aktuelle_stufe >= 6:
        return False, f"{skill_def['name']} ist bereits auf Maximalsstufe (Zoigl)."

    naechste_stufe = aktuelle_stufe + 1
    kosten = kosten_fuer_stufe(skill_def["basis_kosten"], naechste_stufe, skill_def["kategorie"], spieler)

    if spieler.ep_verfuegbar < kosten:
        return False, (
            f"Nicht genug EP. Benoetigt: {kosten}, vorhanden: {spieler.ep_verfuegbar}"
        )

    erfuellt, meldung = voraussetzungen_erfuellt(spieler, skill_def)
    if not erfuellt:
        return False, meldung

    return True, ""


def skill_lernen(spieler, skill_id, alle_skills):
    """Kauft die naechste Stufe eines Skills.
    Gibt (True, Erfolgsmeldung) oder (False, Fehlermeldung) zurueck.
    """
    erlaubt, meldung = kann_lernen(spieler, skill_id, alle_skills)
    if not erlaubt:
        return False, meldung

    skill_def = alle_skills[skill_id]
    aktuelle_stufe = spieler.skill_stufe(skill_id)
    naechste_stufe = aktuelle_stufe + 1
    kosten = kosten_fuer_stufe(skill_def["basis_kosten"], naechste_stufe, skill_def["kategorie"], spieler)

    spieler.ep_verfuegbar -= kosten
    spieler.skills[skill_id] = naechste_stufe

    effekt = skill_def["effekte"][naechste_stufe - 1]["beschreibung"]
    return True, f"{skill_def['name']} ist jetzt Stufe {naechste_stufe}: {effekt}"


def effekt_summe(spieler, typ, alle_skills):
    """Summiert alle Effekte eines bestimmten Typs ueber alle gelernten Skills.
    Beispiel: effekt_summe(spieler, 'alkohol_negativ_pct', alle_skills)
    Gibt 0 zurueck wenn kein Skill diesen Effekttyp hat.
    """
    summe = 0
    for skill_id, stufe in spieler.skills.items():
        if skill_id not in alle_skills:
            continue
        stufe_def = alle_skills[skill_id]["effekte"][stufe - 1]
        for w in stufe_def.get("werte", []):
            if w["typ"] == typ:
                summe += w["wert"]
        w = stufe_def.get("wert")
        if w and w["typ"] == typ:
            summe += w["wert"]
    return summe


def naechste_kosten(spieler, skill_id, alle_skills):
    """Gibt die EP-Kosten fuer die naechste Stufe zurueck (0 wenn max)."""
    if skill_id not in alle_skills:
        return 0
    stufe = spieler.skill_stufe(skill_id)
    if stufe >= 6:
        return 0
    sd = alle_skills[skill_id]
    return kosten_fuer_stufe(sd["basis_kosten"], stufe + 1, sd["kategorie"], spieler)


def skills_nach_kategorie(alle_skills):
    """Gruppiert Skills nach Kategorie.
    Gibt {kategorie: [skill_def, ...]} zurueck.
    """
    ergebnis = {}
    for skill_def in alle_skills.values():
        kat = skill_def["kategorie"]
        if kat not in ergebnis:
            ergebnis[kat] = []
        ergebnis[kat].append(skill_def)
    return ergebnis
