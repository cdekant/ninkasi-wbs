import tcod
import game

BREITE = 100
HOEHE  = 56


def main():
    tileset = tcod.tileset.load_tilesheet(
        "assets/Cheepicus_16x16.png",
        columns=16, rows=16,
        charmap=tcod.tileset.CHARMAP_CP437,
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
