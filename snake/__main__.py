"""


"""

import argparse
from threading import Thread
from game import SnakeGame
from game_io import GameIO


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--board_size',
        type=int,
        nargs=2,
        help='The size of the board in the x and y directions.',
        default=[25, 25]
    )
    parser.add_argument(
        '--random_seed',
        type=int,
        help='The random seed used to generate apple positions.',
        default=123

    )
    parser.add_argument(
        '--walls',
        type=int,
        nargs='+',
        help=(
            'The coordinates of any walls. The format should be '
            '"x1 y1 x2 y2 x3 y3" and so on.'
        ),
        default=[]
    )
    parser.add_argument(
        '--speed',
        type=float,
        help='The amount of seconds between each step.',
        default=0.5
    )
    return parser.parse_args()


def main():
    args = get_args()

    # Convert the walls from input format into coordinate tuples.
    walls = set()
    for i in range(0, len(args.walls)//2, 2):
        walls.add((args.walls[i], args.walls[i+1]))

    game = SnakeGame(
        board_size=tuple(args.board_size),
        walls=walls,
        speed=args.speed,
        random_seed=args.random_seed
    )

    game_thread = Thread(target=game.run)
    game_thread.start()
    GameIO(
        game=game,
        view_speed=0.2
    )
    game_thread.join()


if __name__ == '__main__':
    main()
