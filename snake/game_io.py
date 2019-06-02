from collections import deque
import time
import curses
from threading import Thread, Lock


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
