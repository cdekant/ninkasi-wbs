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
    "karten_seed": None,
    "spieler_x": 2,
    "spieler_y": 2,
    "tod_zaehler": 0,
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
    """Setzt den Level-Zustand nach dem Tod zurueck.

    EP und Skills bleiben erhalten (Roguelite-Prinzip).
    LP, PP, Position und Karten-Seed werden zurueckgesetzt.
    Der Tod-Zaehler wird erhoeht.
    """
    spieler.lp = spieler.lp_max
    spieler.pp = spieler.pp_max

    tod_zaehler = aktuell_dict.get("tod_zaehler", 0) + 1
    neues_aktuell = dict(STANDARD_AKTUELL)
    neues_aktuell["level_index"] = aktuell_dict.get("level_index", 0)
    neues_aktuell["tod_zaehler"] = tod_zaehler
    # Karten-Seed neu wuerfeln beim naechsten Laden (None = zufaellig)
    neues_aktuell["karten_seed"] = None
    return neues_aktuell
