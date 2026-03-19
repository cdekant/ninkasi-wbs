import tcod
import numpy as np
from PIL import Image
import game
import config
from src.tiles import TILE_DATEIEN


def _lade_tile(pfad):
    """Laedt eine einzelne 16x16 RGBA-PNG als numpy-Array fuer set_tile()."""
    return np.array(Image.open(pfad).convert("RGBA"))


def main():
    # Basis: Cheepicus CP437-Tileset
    tileset = tcod.tileset.load_tilesheet(
        "assets/Cheepicus_16x16.png",
        columns=16, rows=16,
        charmap=tcod.tileset.CHARMAP_CP437,
    )

    # Eigene Tiles — ersetzen einzelne Positionen im Basis-Tileset.
    # Codepoint = Unicode-Wert des Zeichens das im Code verwendet wird.
    for codepoint, pfad in TILE_DATEIEN.items():
        tileset.set_tile(codepoint, _lade_tile(pfad))

    with tcod.context.new(
        columns=config.BREITE,
        rows=config.HOEHE,
        title="Battle Ninkasi",
        tileset=tileset,
        sdl_window_flags=config.SDL_FLAGS,
    ) as context:
        console = tcod.console.Console(config.BREITE, config.HOEHE, order="F")
        game.starte(console, context)


if __name__ == "__main__":
    main()
