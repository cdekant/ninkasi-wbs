"""Menue-Registry und State-Hilfsfunktionen.

MENUES definiert welche Menues an welchem Ort verfuegbar sind.
Ort:  "pilsstube" = Hub
      "dungeon"   = aktiver Run
"""

import src.systems.skills as skills_system

# Reihenfolge = TAB-Reihenfolge
MENUES = [
    {"id": "skills",    "name": "Skill-Baum", "verfuegbar": ["pilsstube", "dungeon"]},
    {"id": "inventar",  "name": "Inventar",   "verfuegbar": ["pilsstube", "dungeon"]},
    {"id": "charakter", "name": "Charakter",  "verfuegbar": ["pilsstube", "dungeon"]},
]

# Kategorie-Reihenfolge fuer die Skill-Liste (muss mit skills.json["kategorien"] uebereinstimmen)
KATEGORIE_REIHENFOLGE = [
    "Lebenskraft und Tennentänzerei",
    "Kesselzorn und Sudwall",
    "Natur-, Korn- und Braukunde",
    "Kessel-Magie und Meta-Braukunde",
    "Marktschreierei und Nachschub",
    "Brennblasen-Psi und Zahlenkult",
]


def verfuegbare_menues(ort):
    """Gibt Liste aller am aktuellen Ort freigeschalteten Menue-Definitionen zurueck."""
    return [m for m in MENUES if ort in m["verfuegbar"]]


def naechstes_menue(aktuelles_id, ort):
    """Gibt die ID des naechsten verfuegbaren Menues zurueck (zyklisch)."""
    ids = [m["id"] for m in verfuegbare_menues(ort)]
    if not ids:
        return None
    if aktuelles_id not in ids:
        return ids[0]
    return ids[(ids.index(aktuelles_id) + 1) % len(ids)]


def vorheriges_menue(aktuelles_id, ort):
    """Gibt die ID des vorherigen verfuegbaren Menues zurueck (zyklisch)."""
    ids = [m["id"] for m in verfuegbare_menues(ort)]
    if not ids:
        return None
    if aktuelles_id not in ids:
        return ids[-1]
    return ids[(ids.index(aktuelles_id) - 1) % len(ids)]


def skill_flat_liste(alle_skills):
    """Baut eine geordnete Flachliste aus Kategorie-Headern und Skill-Eintraegen.

    Jedes Element ist ein dict mit "typ": "header" | "skill" | "leer".
    Diese Liste ist die einzige Quelle fuer Reihenfolge in Navigation und Rendering.
    """
    gruppen = skills_system.skills_nach_kategorie(alle_skills)
    items = []
    for kat in KATEGORIE_REIHENFOLGE:
        gruppe = gruppen.get(kat, [])
        if not gruppe:
            continue
        items.append({"typ": "header", "text": kat.upper()})
        for sd in gruppe:
            items.append({"typ": "skill", "skill_id": sd["id"]})
        items.append({"typ": "leer"})
    return items


def ausgewaehlte_skill_id(alle_skills, auswahl):
    """Gibt die skill_id des aktuell ausgewaehlten Skills zurueck.

    auswahl  -- Index in die Liste der auswaehlbaren Skills (ohne Header/Leerzeilen)
    Gibt None zurueck wenn Liste leer oder Index ungueltig.
    """
    items = skill_flat_liste(alle_skills)
    skill_indices = [i for i, it in enumerate(items) if it["typ"] == "skill"]
    if not skill_indices:
        return None
    auswahl = max(0, min(auswahl, len(skill_indices) - 1))
    return items[skill_indices[auswahl]]["skill_id"]


def anzahl_auswaehlbar(alle_skills):
    """Anzahl auswaehlbarer Skills in der Flachliste (fuer Navigations-Grenzen)."""
    return sum(1 for it in skill_flat_liste(alle_skills) if it["typ"] == "skill")


def anzahl_auswaehlbar_fuer(menue_id, alle_skills, spieler):
    """Anzahl navigierbarer Eintraege fuer das aktive Menue."""
    if menue_id == "skills":
        return anzahl_auswaehlbar(alle_skills)
    if menue_id == "inventar":
        return len(spieler.inventar)
    if menue_id == "charakter":
        return 6  # 6 Eigenschaften
    return 0
