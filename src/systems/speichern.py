"""Speichern, Laden und Tod-Reset des Spielstands."""

import json
import os
from datetime import datetime

from src.entities.player import Spieler

SPEICHER_PFAD = os.path.join(os.path.dirname(__file__), "..", "..", "saves", "savegame.json")
SPEICHER_PFAD = os.path.normpath(SPEICHER_PFAD)

VERSION = 1

# Startwerte fuer den Level-Zustand
STANDARD_AKTUELL = {
    "level_index": 0,
    "level_name":  "pflanzenzuechtung",
    "zone_index":  0,     # Aktuelle Zone (0-basiert) innerhalb des Levels
    "zonen_gesamt": 1,    # Gesamtzahl Zonen fuer diesen Run (gewuerfelt beim Dungeon-Eintritt)
    "karten_seed": None,
    "spieler_x": 2,
    "spieler_y": 2,
    "tod_zaehler": 0,
    "bodenloot": [],   # [{x, y, id}] — Items auf dem Dungeon-Boden
}


def speichern(spieler, aktuell_dict):
    """Speichert den aktuellen Spielstand als JSON.

    spieler     -- Spieler-Objekt
    aktuell_dict -- dict mit Level-Zustand (level_index, x, y, lp, ...)
    """
    os.makedirs(os.path.dirname(SPEICHER_PFAD), exist_ok=True)
    daten = {
        "meta": {
            "version": VERSION,
            "gespeichert_am": datetime.now().isoformat(timespec="seconds"),
        },
        "charakter": {
            "eigenschaften": dict(spieler.eigenschaften),
        },
        "spieler": spieler.als_dict(),
        "aktuell": aktuell_dict,
    }
    with open(SPEICHER_PFAD, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=2)


def laden():
    """Laedt den Spielstand. Gibt (spieler, aktuell_dict) oder (None, None) zurueck."""
    if not os.path.exists(SPEICHER_PFAD):
        return None, None
    try:
        with open(SPEICHER_PFAD, encoding="utf-8") as f:
            daten = json.load(f)
        spieler = Spieler.aus_dict(daten["spieler"])
        # charakter-Ebene ist massgeblich (spieler.aus_dict hat bereits Fallback auf {alle 0})
        charakter_daten = daten.get("charakter", {})
        eigenschaften   = charakter_daten.get("eigenschaften", {})
        if eigenschaften:
            spieler.eigenschaften.update(eigenschaften)
        aktuell = daten.get("aktuell", dict(STANDARD_AKTUELL))
        return spieler, aktuell
    except (json.JSONDecodeError, KeyError):
        # Kaputte Speicherdatei — wie kein Spielstand behandeln
        return None, None


def lade_oder_neu():
    """Laedt vorhandenen Spielstand oder erstellt neues Spiel.
    Gibt immer (spieler, aktuell_dict) zurueck.
    """
    spieler, aktuell = laden()
    if spieler is None:
        spieler = Spieler()
        aktuell = dict(STANDARD_AKTUELL)
    return spieler, aktuell


def tod_reset(spieler, aktuell_dict):
    """Setzt Spieler und Level-Zustand nach dem Tod vollstaendig zurueck (Roguelike).

    Erhalten bleiben: ep_gesamt und runden (Statistik), tod_zaehler.
    Alles andere wird geleert — Eigenschaften werden danach neu in der
    Charaktererstellung vergeben.
    """
    spieler.lp = spieler.lp_max
    spieler.pp = spieler.pp_max
    spieler.mp = spieler.mp_max
    spieler.ep_verfuegbar = 0
    spieler.skills = {}
    spieler.inventar = []
    spieler.ausruestung = {
        "waffe_haupt":  None,
        "waffe_neben":  None,
        "kopf":         None,
        "koerper":      None,
        "beine":        None,
        "accessoire_1": None,
        "accessoire_2": None,
    }
    spieler.eigenschaften = {
        "koerperkraft":     0,
        "geschicklichkeit": 0,
        "wissen":           0,
        "weisheit":         0,
        "charisma":         0,
        "geist":            0,
    }

    neues_aktuell = dict(STANDARD_AKTUELL)
    neues_aktuell["tod_zaehler"] = aktuell_dict.get("tod_zaehler", 0) + 1
    return neues_aktuell
