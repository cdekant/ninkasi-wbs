import tcod
import game
import config


def main():
    tileset = tcod.tileset.load_tilesheet(
        "assets/Cheepicus_16x16.png",
        columns=16, rows=16,
        charmap=tcod.tileset.CHARMAP_CP437,
    )
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
