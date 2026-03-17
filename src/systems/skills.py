"""Skill-Logik: laden, pruefen, kaufen."""

import json
import os


def lade_skills():
    """Laedt alle Skill-Definitionen aus data/skills.json.
    Gibt ein Dictionary {skill_id: skill_definition} zurueck.
    """
    pfad = os.path.join(os.path.dirname(__file__), "..", "..", "data", "skills.json")
    pfad = os.path.normpath(pfad)
    with open(pfad, encoding="utf-8") as f:
        daten = json.load(f)
    return {skill["id"]: skill for skill in daten["skills"]}


def stufen_kosten(basis_kosten, stufe):
    """Berechnet die EP-Kosten fuer eine bestimmte Stufe.
    Formel: basis * 4^(stufe-1)
    Stufe 1: basis, Stufe 2: basis*4, ..., Stufe 6: basis*4^5
    """
    return basis_kosten * (4 ** (stufe - 1))


def voraussetzungen_erfuellt(spieler, skill_def):
    """Prueft ob alle Voraussetzungen eines Skills erfuellt sind.
    Gibt (True, '') oder (False, Meldungstext) zurueck.
    """
    for vorraussetzung in skill_def.get("voraussetzungen", []):
        benoetigt_id = vorraussetzung["skill_id"]
        benoetigt_stufe = vorraussetzung["min_stufe"]
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
    kosten = stufen_kosten(skill_def["basis_kosten"], naechste_stufe)

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
    kosten = stufen_kosten(skill_def["basis_kosten"], naechste_stufe)

    spieler.ep_verfuegbar -= kosten
    spieler.skills[skill_id] = naechste_stufe

    effekt = skill_def["effekte"][naechste_stufe - 1]["beschreibung"]
    return True, f"{skill_def['name']} ist jetzt Stufe {naechste_stufe}: {effekt}"


def skill_wert(spieler, skill_id, alle_skills):
    """Gibt den aktuellen Effektwert eines Skills zurueck (0 wenn nicht gelernt)."""
    stufe = spieler.skill_stufe(skill_id)
    if stufe == 0:
        return 0
    skill_def = alle_skills[skill_id]
    return skill_def["effekte"][stufe - 1]["wert"]


def naechste_kosten(spieler, skill_id, alle_skills):
    """Gibt die EP-Kosten fuer die naechste Stufe zurueck (0 wenn max)."""
    if skill_id not in alle_skills:
        return 0
    stufe = spieler.skill_stufe(skill_id)
    if stufe >= 6:
        return 0
    basis = alle_skills[skill_id]["basis_kosten"]
    return stufen_kosten(basis, stufe + 1)


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
