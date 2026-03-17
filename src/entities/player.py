"""Spieler-Klasse mit EP- und Skill-System."""

import src.systems.skills as skills_system


class Spieler:
    """Repraesentiert den Spieler mit EP, Skills und Grundwerten."""

    def __init__(self, name="Brauer"):
        self.name = name
        self.ep_gesamt = 0        # Alle je verdienten EP (nie zurueckgesetzt)
        self.ep_verfuegbar = 0    # Ausgebbare EP
        self.skills = {}          # {skill_id: stufe} — nur gekaufte Skills
        self.runden = 0           # Gesamte gespielte Runden

    # ------------------------------------------------------------------
    # EP
    # ------------------------------------------------------------------

    def ep_hinzufuegen(self, menge):
        """Addiert EP zum Gesamt- und Verfuegbar-Konto."""
        self.ep_gesamt += menge
        self.ep_verfuegbar += menge

    # ------------------------------------------------------------------
    # Skills
    # ------------------------------------------------------------------

    def skill_stufe(self, skill_id):
        """Gibt die aktuelle Stufe eines Skills zurueck (0 = nicht gelernt)."""
        return self.skills.get(skill_id, 0)

    def kann_lernen(self, skill_id, alle_skills):
        """Prueft ob ein Skill lernbar ist. Gibt (bool, meldung) zurueck."""
        return skills_system.kann_lernen(self, skill_id, alle_skills)

    def skill_lernen(self, skill_id, alle_skills):
        """Kauft die naechste Stufe eines Skills. Gibt (bool, meldung) zurueck."""
        return skills_system.skill_lernen(self, skill_id, alle_skills)

    # ------------------------------------------------------------------
    # Serialisierung
    # ------------------------------------------------------------------

    def als_dict(self):
        """Gibt den Spieler als Dictionary zurueck (fuer JSON-Speicherung)."""
        return {
            "name": self.name,
            "ep_gesamt": self.ep_gesamt,
            "ep_verfuegbar": self.ep_verfuegbar,
            "skills": dict(self.skills),
            "runden": self.runden,
        }

    @classmethod
    def aus_dict(cls, daten):
        """Erstellt einen Spieler aus einem Dictionary (aus JSON geladen)."""
        spieler = cls(name=daten.get("name", "Brauer"))
        spieler.ep_gesamt = daten.get("ep_gesamt", 0)
        spieler.ep_verfuegbar = daten.get("ep_verfuegbar", 0)
        spieler.skills = daten.get("skills", {})
        spieler.runden = daten.get("runden", 0)
        return spieler
