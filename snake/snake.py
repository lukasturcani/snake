"""
Holds

"""

from collections import deque
import random
import argparse
import time


class Snake:
    """
    Represents a snake in the :class:`.SnakeGame`.

    Attributes
    ----------
    body : :class:`collections.deque`
        A :class:`deque` of the following form

        .. code-block:: python

            body = deque([
                (0, 0),
                (0, 1),
                (0, 2)
            ])

        holding the coordinates of every body piece of the snake. The
        snake's head is at the index ``-1`` while its tail is at the
        index ``0``.

    velocity : :class:`tuple`
        A :class:`tuple` of the form ``(1, 0)``, which determines how
        the position of the snakes's head changes at every step.

    """

    def __init__(self):
        """
        Initializes a :class:`Snake`.

        """

        self.body = deque([(0, 0)])
        self.velocity = (1, 0)

    def take_step(self):
        """
        Make the snake take a step.

        Returns
        -------
        None : :class:`NoneType`

        """

        head_x, head_y = self.body[-1]
        velocity_x, velocity_y = self.velocity
        new_head = head_x + velocity_x, head_y + velocity_y
        self.body.append(new_head)
        self.body.popleft()

    def hit(self, walls):
        """
        Check if the snake has hit a wall.

        Parameters
        ----------
        walls : :class:`set`
            A :class:`set` of the form

            .. code-block:: python

                walls = {(0,2), (3, 4), (5,4)}

            holding the coordinates of each bit of the walls.

        Returns
        -------
        :class:`bool`
            ``True`` if the snake overlaps with any walls and
            ``False`` otherwise.

        """

        return any(piece in walls for piece in self.body)

    def bite(self):
        """
        Check if the snake has bitten itself.

        Returns
        -------
        :class:`bool`
            ``True`` if the snake has bitten itself and ``False``
            otherwise.

        """

        # If the snake has bitten itself, some of its body pieces
        # will overlap, which means duplicates will be present in
        # self.body.
        return len(set(self.body)) != len(self.body)

    def escape(self, board_size):
        """
        Check is the snake has escaped the board.

        Parameters
        ----------
        board_size : :class:`tuple`

        Returns
        -------
        :class:`bool`
            ``True`` if the snake has escaped the board and
            ``False`` otherwise.

        """

        min_x = min(self.body, key=lambda piece: piece[0])
        max_x = max(self.body, key=lambda piece: piece[0])
        min_y = min(self.body, key=lambda piece: piece[1])
        max_y = max(self.body, key=lambda piece: piece[1])

        board_x, board_y = board_size
        return (
            min_x < 0 or
            min_y < 0 or
            max_x > board_x or
            max_y > board_y
        )

    def eat(self, apple):
        """
        Make the snake eat the apple.

        The snake will only eat the `apple` if its head is at the
        same position as the `apple`.

        Parameters
        ----------
        apple : :class:`tuple`
            A :class:`tuple` of the form ``(21, 12)``, holding the
            coordinates of the apple the snake is meant to eat.

        Returns
        -------
        :class:`bool`
            ``True`` if the snake successfully ate the `apple` and
            ``False`` otherwise.

        """

        head_x, head_y = head = self.body[-1]

        ate = head == apple
        if ate:
            velocity_x, velocity_y = self.velocity
            new_head = head_x + velocity_x, head_y + velocity_y
            self.body.append(new_head)
        return ate


class SnakeGame:
    """
    Represent a game of snake.

    Attributes
    ----------
    board_size : :class:`tuple`
        A :class:`tuple` of the form ``(23, 12)`` which represents the
        size of the board in the x and y directions.

    snake : :class:`.Snake`
        Represents the snake.

    walls : :class:`set`
        A :class:`set` of the form

        .. code-block:: python

            walls = {(0,2), (3, 4), (5,4)}

        holding the coordinates of each bit of the walls.

    speed : :class:`float`
        The number of seconds between each step.

    apple : :class:`tuple`
        A :class:`tuple` of the form ``(21, 12)``, holding the
        coordinates of the apple the snake is meant to eat.

    """

    def __init__(self, board_size, walls, speed, random_seed):
        """
        Initializes a :class:`SnakeGame`.

        Parameters
        ----------
        board_size : :class:`tuple`
            A :class:`tuple` of the form ``(23, 12)`` which represents
            the size of the board in the x and y directions.

        walls : :class:`set`
            A :class:`set` of the form

            .. code-block:: python

                walls = {(0,2), (3, 4), (5,4)}

            holding the coordinates of each bit of the walls.

        speed : :class:`float`
            The number of seconds between each step.

        random_seed : :class:`int`
            The random seed to be used with the game. Used to generate
            random :attr:`apple` coordinates.

        """

        random.seed(random_seed)
        self.board_size = board_size
        self.snake = Snake()
        self.walls = walls
        self.speed = speed
        self.generate_new_apple()

    def generate_new_apple(self):
        """
        Generate new :attr:`apple` coordinates.

        Returns
        -------
        None : :class:`NoneType`

        """

        board_x, board_y = self.board_size
        apple_x = random.randint(0, board_x)
        apple_y = random.randint(0, board_y)
        self.apple = (apple_x, apple_y)

    def run(self):
        """
        Run the game.

        Returns
        -------
        None : :class:`NoneType`

        """

        while (
            not self.snake.hit(self.walls) and
            not self.snake.bite() and
            not self.snake.escape(self.board_size)
        ):

            time.sleep(self.speed)
            self.snake.take_step()

            if self.snake.eat(self.apple):
                self.generate_new_apple()


def main():
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
        default=1
    )

    args = parser.parse_args()

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

    game.run()


if __name__ == '__main__':
    main()
