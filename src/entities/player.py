"""Spieler-Klasse mit EP- und Skill-System."""

import src.systems.skills as skills_system
from src.entities.entitaet import Entitaet


class Spieler(Entitaet):
    """Repraesentiert den Spieler mit EP, Skills und Grundwerten."""

    def __init__(self, name="Brauer"):
        super().__init__(name=name, symbol="@")
        self.hp_max = 20
        self.hp = 20
        self.pp_max = 10
        self.pp = 10
        self.mp_max = 10
        self.mp = 10
        self.basis_schaden = 5
        # Spieler-eigene Felder
        self.ep_gesamt = 0        # Alle je verdienten EP (nie zurueckgesetzt)
        self.ep_verfuegbar = 0    # Ausgebbare EP
        self.skills = {}          # {skill_id: stufe} — nur gekaufte Skills
        self.runden = 0           # Gesamte gespielte Runden

    # ------------------------------------------------------------------
    # Alias-Properties: lp / lp_max als Anzeige-Namen fuer hp / hp_max.
    # Kampfsystem, UI und Speichern koennen weiter .lp / .lp_max nutzen.
    # ------------------------------------------------------------------

    @property
    def lp(self):
        return self.hp

    @lp.setter
    def lp(self, value):
        self.hp = value

    @property
    def lp_max(self):
        return self.hp_max

    @lp_max.setter
    def lp_max(self, value):
        self.hp_max = value

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
        d = super().als_dict()
        # hp/hp_max als lp/lp_max speichern (Anzeige-Konvention + Save-Compat)
        d["lp"] = d.pop("hp")
        d["lp_max"] = d.pop("hp_max")
        # Spieler-eigene Felder
        d["ep_gesamt"] = self.ep_gesamt
        d["ep_verfuegbar"] = self.ep_verfuegbar
        d["skills"] = dict(self.skills)
        d["runden"] = self.runden
        return d

    @classmethod
    def aus_dict(cls, daten):
        """Erstellt einen Spieler aus einem Dictionary (aus JSON geladen)."""
        spieler = cls(name=daten.get("name", "Brauer"))
        # lp/lp_max (aktuelles Format) mit Fallback auf hp/hp_max
        spieler.hp_max = daten.get("lp_max", daten.get("hp_max", 20))
        spieler.hp     = daten.get("lp",     daten.get("hp", spieler.hp_max))
        spieler.pp_max = daten.get("pp_max", 10)
        spieler.pp     = daten.get("pp", spieler.pp_max)
        spieler.mp_max = daten.get("mp_max", 10)
        spieler.mp     = daten.get("mp", spieler.mp_max)
        spieler.verteidigung  = daten.get("verteidigung", 0)
        spieler.basis_schaden = daten.get("basis_schaden", 5)
        spieler.resistenzen   = dict(daten.get("resistenzen", {}))
        spieler.angriffe      = list(daten.get("angriffe", []))
        spieler.ep_gesamt     = daten.get("ep_gesamt", 0)
        spieler.ep_verfuegbar = daten.get("ep_verfuegbar", 0)
        spieler.skills        = daten.get("skills", {})
        spieler.runden        = daten.get("runden", 0)
        return spieler
