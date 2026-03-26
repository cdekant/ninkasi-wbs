"""Inventar-Logik: Hinzufuegen, Entfernen, Benutzen von Items."""


def hinzufuegen(inventar, item_id, item_def, anzahl=1):
    """Legt item_id ins Inventar.

    Stapelbare Items (item_def['stapelbar'] == True) werden nach anzahl gestapelt.
    Nicht-stapelbare (Waffen, Ruestungen) erzeugen eine Einzelinstanz mit
    voller Haltbarkeit je aufgehobenem Exemplar.
    """
    if item_def.get("stapelbar", True):
        for slot in inventar:
            if slot["id"] == item_id:
                slot["anzahl"] += anzahl
                return
        inventar.append({"id": item_id, "anzahl": anzahl})
    else:
        # Jede Instanz bekommt volle Haltbarkeit
        for _ in range(anzahl):
            ht = item_def.get("haltbarkeit_max")
            eintrag = {"id": item_id, "anzahl": 1}
            if ht is not None:
                eintrag["haltbarkeit"] = ht
            inventar.append(eintrag)


def entfernen(inventar, item_id, anzahl=1):
    """Entfernt anzahl Stueck von item_id. Gibt True zurueck wenn erfolgreich."""
    for slot in inventar:
        if slot["id"] == item_id:
            if slot["anzahl"] < anzahl:
                return False
            slot["anzahl"] -= anzahl
            if slot["anzahl"] == 0:
                inventar.remove(slot)
            return True
    return False


def benutzen(inventar, item_id, spieler, alle_items):
    """Benutzt ein verbrauchbares Item aus dem Inventar.

    Gibt (bool, meldung) zurueck.
    """
    item_def = alle_items.get(item_id)
    if item_def is None:
        return False, "Unbekanntes Item."

    kat = item_def["kategorie"]
    if kat in ("waffe", "schild", "ruestung"):
        return False, f"{item_def['name']}: Ausrüsten — noch nicht implementiert."
    if kat != "verbrauchbar":
        return False, f"{item_def['name']}: Nicht verwendbar."

    effekt = item_def.get("effekt")
    if effekt is None:
        return False, f"{item_def['name']}: Kein Effekt definiert."

    if effekt["typ"] == "heilen_lp":
        geheilt = min(effekt["wert"], spieler.lp_max - spieler.lp)
        if geheilt <= 0:
            return False, f"{item_def['name']}: LP bereits voll."
        spieler.hp += geheilt
        entfernen(inventar, item_id)
        return True, f"{item_def['name']}: +{geheilt} LP."

    elif effekt["typ"] == "heilen_pp":
        geheilt = min(effekt["wert"], spieler.pp_max - spieler.pp)
        if geheilt <= 0:
            return False, f"{item_def['name']}: PP bereits voll."
        spieler.pp += geheilt
        entfernen(inventar, item_id)
        return True, f"{item_def['name']}: +{geheilt} PP."

    elif effekt["typ"] == "heilen_mp":
        geheilt = min(effekt["wert"], spieler.mp_max - spieler.mp)
        if geheilt <= 0:
            return False, f"{item_def['name']}: MP bereits voll."
        spieler.mp += geheilt
        entfernen(inventar, item_id)
        return True, f"{item_def['name']}: +{geheilt} MP."

    elif effekt["typ"] == "eigenschaft_punkt_erhoehen":
        # Braucht Benutzereingabe — Aufrufer (game.py) oeffnet Auswahlbildschirm.
        # Item wird erst nach der Auswahl entfernt.
        return "auswahl_noetig", item_id

    return False, "Unbekannter Effekt-Typ."
