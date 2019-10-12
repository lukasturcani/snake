from collections import deque
import time
import curses
from threading import Thread, Lock
import os


class GameIO:
    """
    Controls the game's input and output.

    This class should simply be initialized, it won't return until the
    :class:`.SnakeGame` has finished, see example below.

    Examples
    --------

    .. code-block:: python

        # Create a game and run it in its own thread.
        game = SnakeGame(
            board_size=(25, 25),
            walls=(),
            random_seed=12,
        )

        # Take over IO.
        GameIO(
            game=game,
        )

    """

    def __init__(
        self,
        game,
        speed=0.1,
        player_name='player',
        score_file='scores'
    ):
        """
        Initialize an instance of :class:`GameIO`.

        Parameters
        ----------
        game : :class:`.SnakeGame`
            An instance of the snake game for which the io is being
            controlled.

        speed : :class:`float`
            The time between game steps.

        player_name : :class:`str`, optional
            The name of the player, used to write the name into the
            :attr:`_score_file`.

        score_file : :class:`str`, optional
            The path to a file which keeps track of scores.

        """

        self._game = game
        self._player_name = player_name
        self._speed = speed
        self._score_file = score_file
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
        self._stdscr = stdscr
        stdscr.keypad(True)
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)

        # Create the game window.
        self._create_game_window()

        # Create the score window.
        self._create_score_window()

        # Create the high scores window.
        self._create_high_scores_window()

        # Start capturing input from the user.
        input_thread = Thread(target=self._capture_inputs)
        input_thread.start()

        # While the game is running, render it.
        for step in self._game.run_stepwise():
            self._render()
            time.sleep(self._speed)

        # When the game stops, do a cleanup.
        self._cleanup()
        input_thread.join()

        # Write the score to the score file.
        score = self._game.get_snake_length()
        with open(self._score_file, 'a') as f:
            f.write(f'{self._player_name} {score}\n')

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

            # Write the score.
            score = self._game.get_snake_length()
            self._score_window.clear()
            self._score_window.refresh()
            self._score_window.addstr(0, 1, f'SCORE: {score}')
            self._score_window.refresh()

    def _cleanup(self):
        """
        Cleanup the screen.

        Returns
        -------
        None : :class:`NoneType`

        """

        self._capturing_inputs = False
        curses.nocbreak()
        self._stdscr.keypad(False)
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
                self._game.queue_snake_movement_direction('up')
            elif input_bytes == down:
                self._game.queue_snake_movement_direction('down')
            elif input_bytes == left:
                self._game.queue_snake_movement_direction('left')
            elif input_bytes == right:
                self._game.queue_snake_movement_direction('right')

    def _create_game_window(self):
        """
        Creates the window holding the game.

        Returns
        -------
        None : :class:`NoneType`

        """

        width, height = self._game.get_board_size()
        # Allow space for the border.
        width, height = width+2, height+2
        self._game_window = curses.newwin(height, width, 0, 0)

    def _create_score_window(self):
        """
        Creates the window holding the player's current score.

        Returns
        -------
        None : :class:`NoneType`

        """

        width, height = self._game.get_board_size()
        # Allow space for the border.
        width, height = width+2, height+2
        self._score_window = curses.newwin(4, width, height, 0)

    def _create_high_scores_window(self):
        """
        Creates the window holding the high scores.

        Returns
        -------
        None : :class:`NoneType`

        """

        # Create the game window.
        width, height = self._game.get_board_size()
        # Allow space for the border.
        width, height = width+2, height+2

        self._high_scores_window = curses.newwin(32, 32, 0, width)
        self._high_scores_window.border()
        self._high_scores_window.addstr(1, 10, 'HIGH SCORES')
        self._high_scores_window.addstr(2, 10, '-----------')

        if os.path.exists(self._score_file):
            scores = sorted(self._get_scores(), reverse=True)

            for i, (score, _, name) in enumerate(scores[:15]):
                self._high_scores_window.addstr(4+i, 1, f'{i+1}.')
                self._high_scores_window.addstr(4+i, 4, name)
                self._high_scores_window.addstr(4+i, 14, f'{score}')

        self._high_scores_window.refresh()

    def _get_scores(self):
        """
        Get the scores written in :attr:`_score_file`.

        Yields
        ------
        :class:`tuple`
            A :class:`tuple` holding the score, line number, and name,
            respectively.

        """

        with open(self._score_file, 'r') as f:
            for i, line in enumerate(f):
                name, score = line.split()
                yield int(score), i, name
