"""Menue-Rendering als Vollbild-Overlay auf der tcod-Konsole."""

import tcod
import src.systems.skills as skills_system
import src.systems.menus as menus_system

# ---------------------------------------------------------------------------
# Farbpalette
# ---------------------------------------------------------------------------
F_RAHMEN       = (100, 100, 180)
F_TITEL        = (255, 215,   0)   # Gold
F_TAB_AN       = (255, 255, 255)
F_TAB_AUS      = ( 90,  90,  90)
F_KATEGORIE    = (200, 140,  60)   # Malzbraun
F_NORMAL       = (200, 200, 200)
F_AUSGEWAEHLT  = (255, 255, 100)   # Gelb
F_KEIN_EP      = (180,  80,  80)   # Rot (kein Geld)
F_GESPERRT     = ( 70,  70,  70)   # Dunkelgrau
F_EP_INFO      = (100, 200, 120)   # Gruen
F_DETAIL       = (150, 150, 255)   # Hellblau
F_STATUS_OK    = ( 80, 210,  80)
F_STATUS_FAIL  = (210,  80,  80)
F_FOOTER       = ( 80,  80,  80)

BG_DUNKEL      = ( 12,  12,  25)
BG_AUSGEWAEHLT = ( 40,  40,  80)

# Seltenheits-Farben (fuer Item-Liste)
_SELTENHEIT_FARBE = {
    "gewoehnlich":   (200, 200, 200),
    "ungewoehnlich": ( 80, 200,  80),
    "selten":        ( 80, 150, 255),
}

# ---------------------------------------------------------------------------
# Oeffentliche Funktion
# ---------------------------------------------------------------------------

def zeichne_menue(console, menue_id, spieler, alle_skills, alle_items, auswahl,
                  status_meldung, verfuegbare_liste):
    """Zeichnet das aktive Menue als Vollbild-Overlay.

    console           -- tcod.console.Console
    menue_id          -- ID des aktiven Menues (str)
    spieler           -- Spieler-Objekt
    alle_skills       -- dict {skill_id: skill_def}
    auswahl           -- Index in auswaehlbare Skill-Liste (int)
    status_meldung    -- Feedback-Text (str); Prefix "!" = Fehler
    verfuegbare_liste -- Liste der Menue-Dicts fuer die Tab-Leiste
    """
    w = console.width
    h = console.height

    # Hintergrund
    console.draw_rect(0, 0, w, h, 32, bg=BG_DUNKEL)

    # Rahmen (doppelt)
    _rahmen(console, 0, 0, w, h)

    # Titel
    aktuell = next((m for m in verfuegbare_liste if m["id"] == menue_id), None)
    titel = aktuell["name"] if aktuell else menue_id
    console.print(w // 2, 1, titel, fg=F_TITEL, alignment=tcod.CENTER)

    # Tab-Leiste
    _tabs(console, menue_id, verfuegbare_liste, y=2)

    # Trennlinie unter Tabs
    _linie(console, y=3, w=w)

    # Inhalt (gibt Detail-Text fuer ausgewaehlten Eintrag zurueck)
    if menue_id == "skills":
        detail = _skills_inhalt(console, spieler, alle_skills, auswahl, w, h)
    elif menue_id == "inventar":
        detail = _inventar_inhalt(console, spieler, alle_items, auswahl, w, h)
    elif menue_id == "charakter":
        detail = _charakter_inhalt(console, spieler, w, h)
    else:
        detail = ""

    # Trennlinie vor Footer-Bereich (4 Zeilen vom unteren Rand)
    _linie(console, y=h - 5, w=w)

    # Detail-Zeile (naechster Effekt / Voraussetzung)
    if detail:
        console.print(2, h - 4, detail[: w - 4], fg=F_DETAIL)

    # Status-Meldung (Kauf-Feedback)
    if status_meldung:
        farbe = F_STATUS_OK if not status_meldung.startswith("!") else F_STATUS_FAIL
        console.print(2, h - 3, status_meldung.lstrip("!")[: w - 4], fg=farbe)

    # Steuerungshinweis
    if menue_id == "skills":
        footer = "[ENTER] kaufen   [TAB] naechstes   [Shift+TAB] vorheriges   [ESC] schliessen"
    elif menue_id == "inventar":
        footer = "[ENTER] benutzen   [TAB] naechstes   [Shift+TAB] vorheriges   [ESC] schliessen"
    elif menue_id == "charakter":
        footer = "[TAB] naechstes   [Shift+TAB] vorheriges   [ESC] schliessen"
    else:
        footer = "[TAB] naechstes   [Shift+TAB] vorheriges   [ESC] schliessen"
    console.print(2, h - 2, footer[: w - 4], fg=F_FOOTER)


# ---------------------------------------------------------------------------
# Inhalts-Renderer
# ---------------------------------------------------------------------------

def _skills_inhalt(console, spieler, alle_skills, auswahl, w, h):
    """Zeichnet die Skill-Liste. Gibt Detail-Text zurueck."""

    # EP-Zeile
    ep_text = (
        f"EP verfuegbar: {spieler.ep_verfuegbar:>6}   "
        f"Gesamt erhalten: {spieler.ep_gesamt:>6}"
    )
    console.print(2, 4, ep_text, fg=F_EP_INFO)

    items = menus_system.skill_flat_liste(alle_skills)
    skill_indices = [i for i, it in enumerate(items) if it["typ"] == "skill"]

    if not skill_indices:
        return ""

    auswahl = max(0, min(auswahl, len(skill_indices) - 1))
    ausgewaehlter_flat = skill_indices[auswahl]

    # Inhalt von Zeile 6 bis h-6 (Puffer vor Trennlinie)
    y = 6
    max_y = h - 6

    for flat_i, item in enumerate(items):
        if y >= max_y:
            break

        if item["typ"] == "header":
            console.print(2, y, f"\u2550\u2550 {item['text']} ", fg=F_KATEGORIE)
            y += 1

        elif item["typ"] == "leer":
            y += 1

        elif item["typ"] == "skill":
            ist_sel = (flat_i == ausgewaehlter_flat)
            sid = item["skill_id"]
            sd = alle_skills[sid]
            stufe = spieler.skill_stufe(sid)

            # Stufen-Punkte: z.B. "●●●○○○"
            punkte = "\u25cf" * stufe + "\u25cb" * (6 - stufe)

            # Kosten-Anzeige
            if stufe >= 6:
                kosten_str = "   ZOIGL"
            else:
                k = skills_system.naechste_kosten(spieler, sid, alle_skills)
                kosten_str = f"{k:>7} EP"

            # Zustand fuer Farbe
            erfuellt, _ = skills_system.voraussetzungen_erfuellt(spieler, sd)
            kann, _ = skills_system.kann_lernen(spieler, sid, alle_skills)

            if ist_sel:
                farbe = F_AUSGEWAEHLT
                console.draw_rect(1, y, w - 2, 1, 32, bg=BG_AUSGEWAEHLT)
                marker = "\u25ba"  # ►
            elif stufe >= 6 or not erfuellt:
                farbe = F_GESPERRT
                marker = " "
            elif not kann:
                farbe = F_KEIN_EP
                marker = " "
            else:
                farbe = F_NORMAL
                marker = " "

            name = sd["name"][:24]
            zeile = f"  {marker} {name:<24} {punkte}   {stufe}/6   {kosten_str}"
            console.print(1, y, zeile, fg=farbe)
            y += 1

    # Detail-Text ermitteln
    sd = alle_skills[items[ausgewaehlter_flat]["skill_id"]]
    stufe = spieler.skill_stufe(sd["id"])
    if stufe >= 6:
        return f"{sd['name']}: Maximalstufe (Zoigl) bereits erreicht."
    nst = stufe + 1
    effekt = sd["effekte"][nst - 1]["beschreibung"]
    erfuellt, fehl_msg = skills_system.voraussetzungen_erfuellt(spieler, sd)
    if not erfuellt:
        return f"Gesperrt \u2014 {fehl_msg}"
    return f"Stufe {nst}: {effekt}"




# Anzeige-Namen fuer die sechs Eigenschaften
_EIGENSCHAFT_ANZEIGE = {
    "koerperkraft":     "Körperkraft",
    "geschicklichkeit": "Geschicklichkeit",
    "wissen":           "Wissen",
    "weisheit":         "Weisheit",
    "charisma":         "Charisma",
    "geist":            "Geist",
}


def _charakter_inhalt(console, spieler, w, h):
    """Zeichnet Eigenschaften und Ausruestungsslots. Gibt leeren Detail-Text zurueck."""

    console.print(2, 4, "Eigenschaften:", fg=F_EP_INFO)

    y = 6
    for key, anzeige_name in _EIGENSCHAFT_ANZEIGE.items():
        punkte = spieler.eigenschaften.get(key, 0)
        balken = "\u2588" * punkte + "\u2591" * max(0, 10 - punkte)
        zeile = f"  {anzeige_name:<18} [{balken}]  {punkte:>2}"
        console.print(1, y, zeile, fg=F_NORMAL)
        y += 1

    y += 1
    console.print(2, y, "Ausrüstung:", fg=F_EP_INFO)
    y += 2

    slot_anzeige = [
        ("waffe_haupt",  "Waffe (Haupt)"),
        ("waffe_neben",  "Waffe (Neben) / Schild"),
        ("kopf",         "Kopf"),
        ("koerper",      "Körper"),
        ("beine",        "Beine"),
        ("accessoire_1", "Accessoire 1"),
        ("accessoire_2", "Accessoire 2"),
    ]
    for slot_key, slot_name in slot_anzeige:
        inhalt = spieler.ausruestung.get(slot_key)
        inhalt_str = inhalt["id"] if inhalt else "—"
        farbe = F_NORMAL if inhalt else F_GESPERRT
        zeile = f"  {slot_name:<24} {inhalt_str}"
        console.print(1, y, zeile, fg=farbe)
        y += 1

    return ""


# ---------------------------------------------------------------------------
# Zeichenhilfen
# ---------------------------------------------------------------------------

def _inventar_inhalt(console, spieler, alle_items, auswahl, w, h):
    """Zeichnet das Inventar. Gibt Detail-Text zurueck."""
    inventar = spieler.inventar

    # Kopfzeile
    gesamt = sum(s["anzahl"] for s in inventar)
    console.print(2, 4, f"Gegenstaende: {gesamt}   Slots: {len(inventar)}", fg=F_EP_INFO)

    if not inventar:
        console.print(2, 6, "Das Inventar ist leer.", fg=F_GESPERRT)
        return ""

    auswahl = max(0, min(auswahl, len(inventar) - 1))

    y = 6
    max_y = h - 6

    for i, slot in enumerate(inventar):
        if y >= max_y:
            break
        item_def = alle_items.get(slot["id"])
        if item_def is None:
            continue

        ist_sel = (i == auswahl)
        seltenheit = item_def.get("seltenheit", "gewoehnlich")
        farbe_sel = _SELTENHEIT_FARBE.get(seltenheit, (200, 200, 200))

        if ist_sel:
            console.draw_rect(1, y, w - 2, 1, 32, bg=BG_AUSGEWAEHLT)
            marker = "\u25ba"
            farbe = F_AUSGEWAEHLT
        else:
            marker = " "
            farbe = farbe_sel

        symbol = item_def["symbol"]
        name = item_def["name"][:26]

        # Menge oder Haltbarkeit
        if item_def.get("stapelbar", True):
            menge_str = f"x{slot['anzahl']}"
        else:
            ht = slot.get("haltbarkeit", item_def.get("haltbarkeit_max", "?"))
            ht_max = item_def.get("haltbarkeit_max", "?")
            menge_str = f"[{ht}/{ht_max}]"

        kat = item_def["kategorie"]
        zeile = f"  {marker} {symbol} {name:<26} {menge_str:>8}   {kat}"
        console.print(1, y, zeile, fg=farbe)
        y += 1

    # Detail-Text fuer ausgewaehltes Item
    sel_slot = inventar[auswahl]
    item_def = alle_items.get(sel_slot["id"])
    if not item_def:
        return ""
    return _item_detail(item_def)


def _item_detail(item_def):
    """Baut den Detail-Text fuer die Infozeile am unteren Rand."""
    beschreibung = item_def.get("beschreibung", "")
    kat = item_def["kategorie"]

    if kat == "verbrauchbar":
        effekt = item_def.get("effekt")
        if effekt:
            if effekt["typ"] == "eigenschaft_punkt_erhoehen":
                return f"{beschreibung}  |  +1 Eigenschaftspunkt (Auswahl beim Benutzen)"
            typ_map = {"heilen_lp": "LP", "heilen_pp": "PP", "heilen_mp": "MP"}
            ziel = typ_map.get(effekt["typ"], effekt["typ"])
            return f"{beschreibung}  |  +{effekt['wert']} {ziel}"
        return beschreibung

    if kat == "waffe":
        bonus = item_def.get("schaden_bonus", 0)
        typ   = item_def.get("schaden_typ", "nah")
        rw    = item_def.get("reichweite", 1)
        slot  = item_def.get("slot", "waffe_haupt")
        ht    = item_def.get("haltbarkeit_max", "?")
        return f"{beschreibung}  |  +{bonus} Schaden ({typ}), Reichweite {rw}, Slot: {slot}, Haltbarkeit: {ht}"

    if kat == "schild":
        block_w = item_def.get("block_wert", 0)
        block_c = int(item_def.get("block_chance", 0) * 100)
        ht      = item_def.get("haltbarkeit_max", "?")
        res     = item_def.get("resistenz_boni", {})
        res_str = ", ".join(f"{k} +{v}%" for k, v in res.items())
        detail = f"{beschreibung}  |  Block: {block_w} Schaden, {block_c}% Chance, Haltbarkeit: {ht}"
        if res_str:
            detail += f", Resistenzen: {res_str}"
        return detail

    if kat == "ruestung":
        bonus = item_def.get("verteidigung_bonus", 0)
        slot  = item_def.get("slot", "koerper")
        ht    = item_def.get("haltbarkeit_max", "?")
        res   = item_def.get("resistenz_boni", {})
        res_str = ", ".join(f"{k} +{v}%" for k, v in res.items())
        detail = f"{beschreibung}  |  +{bonus} Verteidigung, Slot: {slot}, Haltbarkeit: {ht}"
        if res_str:
            detail += f", Resistenzen: {res_str}"
        return detail

    return beschreibung


def _rahmen(console, x, y, w, h):
    """Zeichnet einen doppelten Rahmen."""
    # Ecken
    console.print(x,       y,       "\u2554", fg=F_RAHMEN)  # ╔
    console.print(x+w-1,   y,       "\u2557", fg=F_RAHMEN)  # ╗
    console.print(x,       y+h-1,   "\u255a", fg=F_RAHMEN)  # ╚
    console.print(x+w-1,   y+h-1,   "\u255d", fg=F_RAHMEN)  # ╝
    # Horizontale Kanten
    for i in range(1, w - 1):
        console.print(x+i, y,     "\u2550", fg=F_RAHMEN)    # ═
        console.print(x+i, y+h-1, "\u2550", fg=F_RAHMEN)
    # Vertikale Kanten
    for j in range(1, h - 1):
        console.print(x,     y+j, "\u2551", fg=F_RAHMEN)    # ║
        console.print(x+w-1, y+j, "\u2551", fg=F_RAHMEN)


def _linie(console, y, w):
    """Zeichnet eine horizontale Trennlinie (passend zum doppelten Rahmen)."""
    console.print(0,   y, "\u2560", fg=F_RAHMEN)            # ╠
    console.print(w-1, y, "\u2563", fg=F_RAHMEN)            # ╣
    for x in range(1, w - 1):
        console.print(x, y, "\u2550", fg=F_RAHMEN)          # ═


def _tabs(console, aktiv_id, verfuegbare, y):
    """Zeichnet die Tab-Leiste."""
    x = 2
    for m in verfuegbare:
        ist_an = m["id"] == aktiv_id
        if ist_an:
            text = f"[\u25ba {m['name']}]"              # [► Name]
            farbe = F_TAB_AN
        else:
            text = f"  {m['name']}  "
            farbe = F_TAB_AUS
        console.print(x, y, text, fg=farbe)
        x += len(text) + 1
