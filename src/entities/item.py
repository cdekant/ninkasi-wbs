"""Item-Lader fuer Battle Ninkasi."""

import json
import os


def typen_laden(pfad="data/items.json"):
    """Laedt alle Item-Definitionen aus der JSON-Datei.
    Gibt ein Dictionary {item_id: definition} zurueck.
    """
    pfad = os.path.normpath(pfad)
    with open(pfad, encoding="utf-8") as f:
        daten = json.load(f)
    return {k: v for k, v in daten.items() if not k.startswith("_")}
