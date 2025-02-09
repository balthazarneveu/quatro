from quatro.games.flappy_butterfly_interactive_pipe import launch_flappy_pipe
from quatro.games.flappy_butterfly import launch_flappy_butterfly
from quatro.games.running_bunny import launch_running_bunny
from quatro.system.quit import QUIT
import pygame
import argparse
import sys

GAMES_LIST = {
    "flappy": launch_flappy_butterfly,
    "flappy_pipe": launch_flappy_pipe,
    "bunny": launch_running_bunny,
}
GAMES_NAMES = list(GAMES_LIST.keys())


def populate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--game", type=str, default="bunny", choices=GAMES_NAMES)
    parser.add_argument("-r", "--resolution", type=int, nargs=2, default=None)
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-m", "--mute", action="store_true")
    return parser


if __name__ == "__main__":
    parser = populate_parser()
    args = parser.parse_args(sys.argv[1:])
    game_to_launch = args.game
    assert game_to_launch is not None, f"Game {game_to_launch} not found in GAMES_LIST"
    game_func = GAMES_LIST.get(game_to_launch, None)
    assert game_func is not None, f"Game {game_to_launch} not found in GAMES_LIST"
    context = {}
    while not context.get(QUIT, False):
        context = game_func(
            resolution=args.resolution, debug=args.debug, audio=not args.mute
        )
    pygame.quit()
