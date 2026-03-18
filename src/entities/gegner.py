"""Gegner-Klasse und Lade-Funktion fuer Battle Ninkasi."""

import json
import os


def typen_laden():
    """Laedt alle Gegner-Typ-Definitionen aus data/enemies.json.
    Prueft ob alle verwendeten Effekttypen in data/effekttypen.json bekannt sind.
    Gibt ein Dictionary {typ_id: definition} zurueck.
    """
    pfad_gegner = os.path.join(os.path.dirname(__file__), "..", "..", "data", "enemies.json")
    pfad_gegner = os.path.normpath(pfad_gegner)
    with open(pfad_gegner, encoding="utf-8") as f:
        daten = json.load(f)

    pfad_effekte = os.path.join(os.path.dirname(__file__), "..", "..", "data", "effekttypen.json")
    pfad_effekte = os.path.normpath(pfad_effekte)
    with open(pfad_effekte, encoding="utf-8") as f:
        bekannte_effekte = json.load(f)

    # Effekttypen aller Angriffe validieren
    for typ_id, gegner_def in daten.items():
        if typ_id.startswith("_"):
            continue
        for angriff in gegner_def.get("angriffe", []):
            for effekt in angriff.get("effekte", []):
                if effekt["typ"] not in bekannte_effekte:
                    raise ValueError(
                        f"Unbekannter Effekttyp '{effekt['typ']}' im Angriff "
                        f"'{angriff['id']}' von Gegner '{typ_id}'. "
                        f"Bitte in data/effekttypen.json eintragen."
                    )

    return {k: v for k, v in daten.items() if not k.startswith("_")}


class Gegner:
    """Repraesentiert einen einzelnen Gegner im Kampf (typ='einzel').

    Fuer Schwarm-Gegner (typ='schwarm') ist noch kein Code implementiert —
    aus_typ() gibt in diesem Fall None zurueck.
    """

    def __init__(self, typ_id, name, symbol, hp_max, verteidigung,
                 ep_beute, angriffe, resistenzen=None, regen_hp=0, loot_pool=None):
        self.typ_id = typ_id
        self.name = name
        self.symbol = symbol
        self.hp_max = hp_max
        self.hp = hp_max
        self.verteidigung = verteidigung
        self.ep_beute = ep_beute
        self.angriffe = angriffe        # Liste von Angriffs-Dicts (schaden bereits skaliert)
        self.resistenzen = resistenzen if resistenzen is not None else {}
        self.regen_hp = regen_hp
        self.loot_pool = loot_pool if loot_pool is not None else []

    @property
    def lebt(self):
        """True solange der Gegner noch HP hat."""
        return self.hp > 0

    @classmethod
    def aus_typ(cls, typ_id, alle_typen, staerke=1.0):
        """Erstellt eine Gegner-Instanz aus einer Typ-Definition.

        staerke: 0.0 (schwach) bis 1.0 (stark).
        Skaliert HP, Verteidigung und Angriffs-Schaden linear:
            0.0 → 50% der Basis-Werte
            1.0 → 100% der Basis-Werte

        Gibt None zurueck fuer Schwarm-Gegner (noch nicht implementiert).
        Wirft ValueError bei unbekanntem typ_id.
        """
        if typ_id not in alle_typen:
            raise ValueError(f"Unbekannter Gegner-Typ: '{typ_id}'")

        d = alle_typen[typ_id]

        if d.get("typ") == "schwarm":
            return None  # Schwarm-Logik folgt spaeter

        faktor = 0.5 + staerke * 0.5

        hp_max = max(1, round(d["hp_basis"] * faktor))
        verteidigung = max(0, round(d["verteidigung_basis"] * faktor))

        # Schaden in jedem Angriff skalieren; restliche Felder unveraendert uebernehmen
        angriffe = []
        for a in d.get("angriffe", []):
            angriff = dict(a)
            angriff["schaden"] = max(0, round(a["schaden_basis"] * faktor))
            angriffe.append(angriff)

        return cls(
            typ_id=typ_id,
            name=d["name"],
            symbol=d["symbol"],
            hp_max=hp_max,
            verteidigung=verteidigung,
            ep_beute=d["ep_beute"],
            angriffe=angriffe,
            resistenzen=dict(d.get("resistenzen", {})),
            regen_hp=d.get("regen_hp", 0),
            loot_pool=list(d.get("loot_pool", [])),
        )

    def als_dict(self):
        """Serialisiert den aktuellen Kampfzustand (fuer JSON-Spielstand)."""
        return {
            "typ_id": self.typ_id,
            "name": self.name,
            "symbol": self.symbol,
            "hp_max": self.hp_max,
            "hp": self.hp,
            "verteidigung": self.verteidigung,
            "ep_beute": self.ep_beute,
            "angriffe": self.angriffe,
            "resistenzen": self.resistenzen,
            "regen_hp": self.regen_hp,
            "loot_pool": self.loot_pool,
        }

    @classmethod
    def aus_dict(cls, daten):
        """Erstellt einen Gegner aus einem gespeicherten Zustand (aus JSON)."""
        g = cls(
            typ_id=daten["typ_id"],
            name=daten["name"],
            symbol=daten["symbol"],
            hp_max=daten["hp_max"],
            verteidigung=daten["verteidigung"],
            ep_beute=daten["ep_beute"],
            angriffe=daten.get("angriffe", []),
            resistenzen=daten.get("resistenzen", {}),
            regen_hp=daten.get("regen_hp", 0),
            loot_pool=daten.get("loot_pool", []),
        )
        g.hp = daten.get("hp", daten["hp_max"])  # gespeicherte HP wiederherstellen
        return g
