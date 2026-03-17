import tcod
import game

BREITE = 80
HOEHE = 40


def main():
    tileset = tcod.tileset.load_truetype_font(
        "assets/IBMPlexMono-Regular.ttf", tile_width=14, tile_height=24
    )
    with tcod.context.new(
        columns=BREITE,
        rows=HOEHE,
        title="Battle Ninkasi",
        tileset=tileset,
    ) as context:
        console = tcod.console.Console(BREITE, HOEHE, order="F")
        game.starte(console, context)


if __name__ == "__main__":
    main()
