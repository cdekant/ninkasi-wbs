"""Gegner-Klasse und Lade-Funktion fuer Battle Ninkasi."""

import json
import os

from src.entities.entitaet import Entitaet
from src.tiles import TILE_NAMEN


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


class Gegner(Entitaet):
    """Repraesentiert einen einzelnen Gegner im Kampf (typ='einzel').

    Fuer Schwarm-Gegner (typ='schwarm') ist noch kein Code implementiert —
    aus_typ() gibt in diesem Fall None zurueck.
    """

    def __init__(self, typ_id, name, symbol, hp_max, verteidigung,
                 ep_beute, angriffe, resistenzen=None, regen_hp=0, loot_pool=None,
                 verhalten="statisch", sicht_radius=20,
                 flucht_hp_pct=None, geschwindigkeit=1.0):
        super().__init__(name=name, symbol=symbol)
        self.hp_max = hp_max
        self.hp = hp_max
        self.verteidigung = verteidigung
        self.angriffe = angriffe        # Liste von Angriffs-Dicts (schaden bereits skaliert)
        self.resistenzen = resistenzen if resistenzen is not None else {}
        # Gegner-eigene Felder
        self.typ_id = typ_id
        self.ep_beute = ep_beute
        self.regen_hp = regen_hp
        self.loot_pool = loot_pool if loot_pool is not None else []
        # KI-Felder (aus JSON)
        self.verhalten = verhalten
        self.sicht_radius = sicht_radius
        self.flucht_hp_pct = flucht_hp_pct    # None = flieht nie
        self.geschwindigkeit = geschwindigkeit
        # KI-Laufzeitzustand (nicht serialisiert)
        self.ki_zustand = "idle"              # "idle" | "aktiv"
        self.bewegungs_zaehler = 0.0          # akkumuliert geschwindigkeit pro Zug

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
            angriff["schaden"] = max(0, round(a["schaden"] * faktor))
            angriffe.append(angriff)

        roh_symbol = d["symbol"]
        symbol = TILE_NAMEN.get(roh_symbol, roh_symbol)

        return cls(
            typ_id=typ_id,
            name=d["name"],
            symbol=symbol,
            hp_max=hp_max,
            verteidigung=verteidigung,
            ep_beute=d["ep_beute"],
            angriffe=angriffe,
            resistenzen=dict(d.get("resistenzen", {})),
            regen_hp=d.get("regen_hp", 0),
            loot_pool=list(d.get("loot_pool", [])),
            verhalten=d.get("verhalten", "statisch"),
            sicht_radius=d.get("sicht_radius", 20),
            flucht_hp_pct=d.get("flucht_hp_pct", None),
            geschwindigkeit=d.get("geschwindigkeit", 1.0),
        )

    def als_dict(self):
        """Serialisiert den aktuellen Kampfzustand (fuer JSON-Spielstand)."""
        d = super().als_dict()
        d.update({
            "typ_id": self.typ_id,
            "ep_beute": self.ep_beute,
            "regen_hp": self.regen_hp,
            "loot_pool": self.loot_pool,
            "verhalten": self.verhalten,
            "sicht_radius": self.sicht_radius,
            "flucht_hp_pct": self.flucht_hp_pct,
            "geschwindigkeit": self.geschwindigkeit,
        })
        return d

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
        g.verhalten = daten.get("verhalten", "statisch")
        g.sicht_radius = daten.get("sicht_radius", 20)
        g.flucht_hp_pct = daten.get("flucht_hp_pct", None)
        g.geschwindigkeit = daten.get("geschwindigkeit", 1.0)
        return g
