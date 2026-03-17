"""Spieler-Klasse mit EP- und Skill-System."""

import src.systems.skills as skills_system


class Spieler:
    """Repraesentiert den Spieler mit EP, Skills und Grundwerten."""

    # Basis-Werte ohne Skills
    BASIS_LP = 30
    BASIS_PP = 10
    BASIS_ANGRIFF = 5

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
    # Abgeleitete Werte
    # ------------------------------------------------------------------

    def max_lp(self, alle_skills):
        """Maximale Lebenspunkte inkl. Skill-Bonus."""
        bonus = skills_system.skill_wert(self, "lebenspunkte", alle_skills)
        return self.BASIS_LP + bonus

    def max_pp(self, alle_skills):
        """Maximale Psi-Punkte inkl. Skill-Bonus."""
        bonus = skills_system.skill_wert(self, "psi_punkte", alle_skills)
        return self.BASIS_PP + bonus

    def angriff(self, alle_skills):
        """Angriffswert inkl. Darrtechnik-Bonus."""
        bonus = skills_system.skill_wert(self, "darrtechnik", alle_skills)
        return self.BASIS_ANGRIFF + bonus

    def ep_pro_runde(self, alle_skills):
        """EP-Gewinn pro gueltigem Spielzug (1 + Verfahrenstechnik-Bonus)."""
        bonus = skills_system.skill_wert(self, "verfahrenstechnik", alle_skills)
        return 1 + bonus

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
