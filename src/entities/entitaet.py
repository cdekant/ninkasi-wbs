"""Basis-Entitaet fuer alle Kaempfer in Battle Ninkasi.

Spieler und Gegner erben von dieser Klasse. Alle kampfrelevanten
Grundwerte sind hier zentralisiert, damit KampfZustand mit beiden
Typen gleichartig arbeiten kann.
"""


class Entitaet:
    """Gemeinsame Basis fuer Spieler und Gegner.

    Kampfrelevante Felder:
        hp / hp_max    -- Trefferpunkte
        pp / pp_max    -- Psi-Punkte (fuer Faehigkeiten)
        verteidigung   -- flacher Schadensabzug
        basis_schaden  -- Rohschaden ohne Waffe/Angriff
        resistenzen    -- {schadenstyp: 0.0..1.0}
        angriffe       -- Liste von Angriffs-Dicts (aus JSON)
    """

    def __init__(self, name="", symbol="?"):
        self.name = name
        self.symbol = symbol
        self.hp = 0
        self.hp_max = 0
        self.pp = 0
        self.pp_max = 0
        self.verteidigung = 0
        self.basis_schaden = 0
        self.resistenzen = {}
        self.angriffe = []

    @property
    def lebt(self):
        """True solange hp > 0."""
        return self.hp > 0

    def als_dict(self):
        """Gibt Basisfelder als Dict zurueck. Unterklassen erweitern via super()."""
        return {
            "name": self.name,
            "symbol": self.symbol,
            "hp": self.hp,
            "hp_max": self.hp_max,
            "pp": self.pp,
            "pp_max": self.pp_max,
            "verteidigung": self.verteidigung,
            "basis_schaden": self.basis_schaden,
            "resistenzen": dict(self.resistenzen),
            "angriffe": list(self.angriffe),
        }
