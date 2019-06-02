"""
A very simple snake game.

"""

from collections import deque
import random
import argparse
import time
import curses
import itertools as it
from threading import Thread, Lock


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

    velocity_queue : :class:`tuple`
        A :class:`tuple` of the form ``(1, 0)``, which determines the
        :attr:`velocity` the snake will have the next time
        :meth:`take_step` is called. This provides a buffer the user
        can modify instead of modifying :attr:`velocity` directly. The
        reason :attr:`velocity` cannot be modified directly is because
        if the current velocity is going up the user is not allowed to
        change it to down in 1 game tick. If the user was allowed to
        modify :attr:`velocity`, they could first overwrite the
        :attr:`velocity` to right or left and then to down.
        This could happen within 1 game tick, as the user inputs
        commands outside of the game loop and multiple commands can
        be issued within 1 tick. If the user was allowed to change
        :attr:`velocity` it would effectively allow them to go from up
        to down within 1 game tick as they could do this by pressing
        left or right first.


    """

    def __init__(self):
        """
        Initializes a :class:`Snake`.

        """

        self.body = deque([(0, 0)])
        self.velocity = (1, 0)
        self.velocity_queue = deque([])

    def take_step(self):
        """
        Make the snake take a step.

        Returns
        -------
        None : :class:`NoneType`

        """

        if self.velocity_queue:
            new_velocity = self.velocity_queue.popleft()
            if self._valid_velocity(new_velocity):
                self.velocity = new_velocity

        head_x, head_y = self.body[-1]
        velocity_x, velocity_y = self.velocity
        new_head = head_x + velocity_x, head_y + velocity_y
        self.body.append(new_head)
        self.body.popleft()

    def _valid_velocity(self, velocity):
        invalid = {
            frozenset({(0, 1), (0, -1)}),
            frozenset({(1, 0), (-1, 0)})
        }
        velocities = frozenset({velocity, self.velocity})
        return velocities not in invalid

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

        min_x = min(x for x, y in self.body)
        max_x = max(x for x, y in self.body)
        min_y = min(y for x, y in self.body)
        max_y = max(y for x, y in self.body)

        board_x, board_y = board_size
        return (
            min_x < 0 or
            min_y < 0 or
            max_x >= board_x or
            max_y >= board_y
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
    running : :class:`bool`
        ``True`` if a game is running else ``False``.

    _board_size : :class:`tuple`
        A :class:`tuple` of the form ``(23, 12)`` which represents the
        size of the board in the x and y directions.

    _snake : :class:`.Snake`
        Represents the snake.

    _walls : :class:`set`
        A :class:`set` of the form

        .. code-block:: python

            walls = {(0,2), (3, 4), (5,4)}

        holding the coordinates of each bit of the walls.

    _speed : :class:`float`
        The number of seconds between each step.

    _apple : :class:`tuple`
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
            random :attr:`_apple` coordinates.

        """

        random.seed(random_seed)
        self.running = False
        self._board_size = board_size
        self._snake = Snake()
        self._walls = walls
        self._speed = speed
        self.generate_new_apple()

    def generate_new_apple(self):
        """
        Generate new :attr:`_apple` coordinates.

        Returns
        -------
        None : :class:`NoneType`

        """

        # This is a terrible implementation performance-wise but it's
        # pretty robust. It prevents the generation of the apple at the
        # location of any walls or where snake currently is.
        board_x, board_y = self._board_size
        positions = it.product(range(0, board_x), range(0, board_y))
        invalid_positions = self._walls | set(self._snake.body)
        valid_positions = [
            pos for pos in positions if pos not in invalid_positions
        ]
        self._apple = random.choice(valid_positions)

    def run(self):
        """
        Run the game.

        Returns
        -------
        None : :class:`NoneType`

        """

        self.running = True
        while (
            not self._snake.hit(self._walls) and
            not self._snake.bite() and
            not self._snake.escape(self._board_size)
        ):
            time.sleep(self._speed)
            self._snake.take_step()

            if self._snake.eat(self._apple):
                self.generate_new_apple()
        self.running = False

    def get_snake_velocity(self):
        """

        """

        return self._snake.velocity

    def queue_snake_velocity(self, x, y):
        """

        """

        self._snake.velocity_queue.append((x, y))

    def get_snake(self):
        """

        """

        return self._snake.body

    def get_walls(self):
        """

        """

        return self._walls

    def get_apple(self):
        """

        """

        return self._apple

    def get_board_size(self):
        """

        """

        return self._board_size


class GameIO:
    """
    Controls the game's input and output.

    Attributes
    ----------

    """

    def __init__(self, game, view_speed):
        """

        """

        self._game = game
        self._view_speed = view_speed
        self._lock = Lock()
        curses.wrapper(self._run)

    def _run(self, stdscr):
        """

        """

        self.stdscr = stdscr
        stdscr.keypad(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        width, height = self._game.get_board_size()
        self._game_window = curses.newwin(height+2, width+2, 0, 0)

        input_thread = Thread(target=self._capture_inputs)
        input_thread.start()

        while self._game.running:
            self._view()
            time.sleep(self._view_speed)

        self._end()
        input_thread.join()

    def _view(self):
        """
        Generate a new game view.

        Returns
        -------
        None : :class:`NoneType`

        """

        with self._lock:
            self._game_window.clear()
            self._game_window.refresh()
            self._game_window.border()

            for x, y in self._game.get_walls():
                self._game_window.addch(y+1, x+1, '█')

            for x, y in self._game.get_snake():
                self._game_window.addch(y+1, x+1, 'X')

            apple_x, apple_y = self._game.get_apple()
            self._game_window.addch(apple_y+1, apple_x+1, 'O')

            self._game_window.refresh()

    def _end(self):
        self._capturing_inputs = False
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def _capture_inputs(self):
        """

        """

        down = deque([27, 91, 65])
        up = deque([27, 91, 66])
        right = deque([27, 91, 67])
        left = deque([27, 91, 68])

        input_bytes = deque(maxlen=3)
        self._capturing_inputs = True
        while self._capturing_inputs:
            with self._lock:
                self._game_window.nodelay(True)
                key = self._game_window.getch()
                self._game_window.nodelay(False)

            input_bytes.append(key)

            if input_bytes == up:
                self._game.queue_snake_velocity(0, 1)
            elif input_bytes == down:
                self._game.queue_snake_velocity(0, -1)
            elif input_bytes == left:
                self._game.queue_snake_velocity(-1, 0)
            elif input_bytes == right:
                self._game.queue_snake_velocity(1, 0)


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
        default=0.5
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

    game_thread = Thread(target=game.run)
    game_thread.start()
    GameIO(
        game=game,
        view_speed=0.2
    )
    game_thread.join()


if __name__ == '__main__':
    main()
