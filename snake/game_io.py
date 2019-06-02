from collections import deque
import time
import curses
from threading import Thread, Lock


class GameIO:
    """
    Controls the game's input and output.

    This class should simply by initialized, it won't return until the
    :class:`.SnakeGame` has finished, see example below.

    Attributes
    ----------
    _game : :class:`.SnakeGame`
        An instance of the snake game for which the io is being
        controlled.

    _view_speed : :class:`float`
        The time in seconds between each render.

    _lock : :class:`threading.Lock`
        Because input and output is handled by separate threads but
        in both cases through :mod:`curses`, this lock prevents race
        conditions between the input and output.

    Examples
    --------

    .. code-block:: python

        # Create a game and run it in its own thread.
        game = SnakeGame(
            board_size=(25, 25),
            walls=frozenset(),
            speed=0.2,
            random_seed=12
        )

        game_thread = Thread(target=game.run)
        game_thread.start()

        # Take over IO.
        GameIO(
            game=game,
            view_speed=0.2
        )

        # Game should be finished now.
        game_thread.join()

    """

    def __init__(self, game, view_speed):
        """
        Initializes an instance of :class:`GameIO`.

        Parameters
        ----------
        game : :class:`.SnakeGame`
            An instance of the snake game for which the io is being
            controlled.

        view_speed : :class:`float`
            The time in seconds between each render.

        """

        self._game = game
        self._view_speed = view_speed
        self._lock = Lock()
        curses.wrapper(self._run)

    def _run(self, stdscr):
        """
        Starts the IO.

        Parameters
        ----------
        stdscr : :class:`curses.window`
            A :class:`curses.window` which represents the entire
            terminal screen.

        Returns
        -------
        None : :class:`NoneType`

        """

        # Set up curses.
        self.stdscr = stdscr
        stdscr.keypad(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        # Create the game window.
        width, height = self._game.get_board_size()
        self._game_window = curses.newwin(height+2, width+2, 0, 0)

        # Start capturing input from the user.
        input_thread = Thread(target=self._capture_inputs)
        input_thread.start()

        # While the game is running, render it.
        while self._game.running:
            self._render()
            time.sleep(self._view_speed)

        # When the game stops, do a cleanup.
        self._end()
        input_thread.join()

    def _render(self):
        """
        Render the game.

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

    def _cleanup(self):
        """
        Cleanup the screen.

        Returns
        -------
        None : :class:`NoneType`

        """

        self._capturing_inputs = False
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def _capture_inputs(self):
        """
        Capture inputs from the keyboard and send them to the game.

        Returns
        -------
        None : :class:`NoneType`

        """

        # The keyboard sends the input as a stream of numbers. These
        # numbers represent the respctive arrow keys being pressed.
        down = deque([27, 91, 65])
        up = deque([27, 91, 66])
        right = deque([27, 91, 67])
        left = deque([27, 91, 68])

        input_bytes = deque(maxlen=3)
        self._capturing_inputs = True
        while self._capturing_inputs:
            with self._lock:
                # Don't wait for the user to send a keypress. If
                # you do, the game will likely hang at the end.
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
