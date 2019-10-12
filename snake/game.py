"""
Holds the snake game.

The only thing necessary to run a game of snake is :class:`.SnakeGame`.

"""

from collections import deque
import random
import itertools as it


class _Snake:
    """
    Represents a snake in the :class:`.SnakeGame`.

    """

    def __init__(self):
        """
        Initializes a :class:`_Snake`.

        """

        self._body = deque([(0, 0)])
        self._velocity = (1, 0)
        self._velocity_queue = deque([])

    def get_body(self):
        """
        Yield the positions occupied by the snake.

        Yields
        ------
        :class:`tuple`
            The position of a segment of the snake's body.

        """

        yield from self._body

    def take_step(self):
        """
        Make the snake take a step.

        Returns
        -------
        None : :class:`NoneType`

        """

        if self._velocity_queue:
            new_velocity = self._velocity_queue.popleft()
            if self._is_valid_velocity(new_velocity):
                self._velocity = new_velocity

        head_x, head_y = self._body[-1]
        velocity_x, velocity_y = self._velocity
        new_head = head_x + velocity_x, head_y + velocity_y
        self._body.append(new_head)
        self._body.popleft()

    def _is_valid_velocity(self, velocity):
        """
        Check if `velocity` is valid.

        A snake velocity is invalid if the snake is going up and the
        `velocity` is down, or vice versa. Equally, `velocity` is
        invalid if the snake is going left and `velocity` is right and
        vice versa.

        Parameters
        ----------
        velocity : :class:`tuple`
            A :class:`tuple` of the form ``(1, 0)`` representing a
            possible snake velocity.

        Returns
        -------
        :class:`bool`
            ``True`` if `velocity` is valid and ``False`` otherwise.

        """

        invalid = {
            frozenset({(0, 1), (0, -1)}),
            frozenset({(1, 0), (-1, 0)})
        }
        valid = {
            (0, 1), (0, -1), (1, 0), (-1, 0)
        }
        velocities = frozenset({velocity, self._velocity})
        return velocities not in invalid and velocity in valid

    def hit(self, walls):
        """
        Check if the snake has hit a wall.

        Parameters
        ----------
        walls : :class:`frozenset`
            A :class:`frozenset` of the form

            .. code-block:: python

                walls = {(0,2), (3, 4), (5,4)}

            holding the coordinates of each bit of the walls.

        Returns
        -------
        :class:`bool`
            ``True`` if the snake overlaps with any walls and
            ``False`` otherwise.

        """

        return any(piece in walls for piece in self._body)

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
        return len(set(self._body)) != len(self._body)

    def is_escaped(self, board_size):
        """
        Check is the snake has escaped the board.

        Parameters
        ----------
        board_size : :class:`tuple`
            A :class:`tuple` of the form ``(21, 33)`` represting the
            size of the board in the x and y directions.

        Returns
        -------
        :class:`bool`
            ``True`` if the snake has escaped the board and
            ``False`` otherwise.

        """

        min_x = min(x for x, y in self._body)
        max_x = max(x for x, y in self._body)
        min_y = min(y for x, y in self._body)
        max_y = max(y for x, y in self._body)

        board_x, board_y = board_size
        return (
            min_x < 0
            or min_y < 0
            or max_x >= board_x
            or max_y >= board_y
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

        head_x, head_y = head = self._body[-1]
        ate = head == apple
        if ate:
            velocity_x, velocity_y = self._velocity
            new_head = head_x + velocity_x, head_y + velocity_y
            self._body.append(new_head)
        return ate

    def queue_velocity(self, velocity):
        """
        Queue a future snake velocity.

        Parameters
        ----------
        velocity : :class:`tuple`
            The velocity the snake should have.

        Returns
        -------
        None : :class:`NoneType`

        """

        self._velocity_queue.append(velocity)

    def get_num_queued_velocities(self):
        """
        Return the numbered of queued velocities.

        Returns
        -------
        :class:`int`
            The number of queued velocities.

        """

        return len(self._velocity_queue)

    def get_velocity(self, step=0):
        """
        Get the velocity of the snake a step.

        Parameters
        ----------
        step : :class:`int`, optional
            The velocity at a given step. If ``0``then the current
            velocity is returned.

        Returns
        -------
        :class:`tuple
            The velocity.

        """

        if step == 0:
            return self._velocity

        return self._velocity_queue[step-1]


class SnakeGame:
    """
    Represents a game of snake.

    The game can be run with :meth:`run`, or stepwise with
    :meth:`run_stepwise`. The game runs in a self
    contained loop and will not take input from the keyboard or
    display itself on the screen. The game is interacted with purely
    programatically. However, you can write code that captures keyboard
    input and sends it to the game. You can also write code that looks
    at the state of the game, as contained in this class, and writes
    it to the screen. :class:`.GameIO` does both of these things.

    The snake is controlled by setting its movement direction. This can
    be done with :meth:`queue_snake_movement_direction`. The user will
    use this method to queue which direction the snake will move, the
    next time the snake takes a step. The queue allows the user
    to queue several steps ahead, which results in the game feeling
    more responsive when played.

    :class:`SnakeGame` can be initialized with walls, allowing the
    user to create a level.

    If you want to interact with the game in an automated way
    you can do something like

    .. code-block:: python

        def get_next_direction(game):
            # This is a user-defined function which decides on the
            # direction the snake should take on the next turn.

            ...


        def apply_action(game):
            # This is a user-defined function which looks at the
            # state of the game an decides on sending actions to it.

            direction = get_next_direction(game)
            game.queue_snake_movement_direction(direction)

        game = SnakeGame(
            board_size=(23, 34),
            walls=((1, 1), (2, 2), (3, 3)),
            random_seed=12,
        )

        for step_number in game.run_stepwise():
            apply_action(game)

    """

    def __init__(self, board_size, walls, random_seed):
        """
        Initialize a :class:`SnakeGame`.

        Parameters
        ----------
        board_size : :class:`tuple`
            A :class:`tuple` of the form ``(23, 12)`` which represents
            the size of the board in the x and y directions.

        walls : :class:`iterable` of :class:`tuple`
            An :class:`iterable` holding the position of every
            wall segment.

        random_seed : :class:`int`
            The random seed to be used with the game. Used to generate
            apple locations.

        """

        self._generator = random.Random(random_seed)
        self._board_size = board_size
        self._snake = _Snake()
        self._walls = frozenset(walls)
        self._apple = self._get_new_apple()

    def _get_new_apple(self):
        """
        Generate new :attr:`_apple` coordinates.

        Returns
        -------
        :class:`tuple`
            The position of a new apple.

        """

        snake_body = self._snake.get_body()
        board_x, board_y = self._board_size
        board_positions = it.product(
            range(0, board_x),
            range(0, board_y),
        )
        valid_positions = (
            pos for pos in board_positions
            if pos not in set(snake_body) and pos not in self._walls
        )
        # The number of valid apple positions is given
        # by the total board size minus the walls and the length of the
        # snake, as each bit of the snake and each wall must occupy an
        # empty position.
        board_size = board_x * board_y
        max_index = board_size-len(self._walls)-len(snake_body)-1
        # Avoid looping through all the valid apple positions by
        # generating the index of the chosen position ahead of time
        # and returning as soon as the position with that index is
        # found.
        index = self._generator.randint(0, max_index)
        for i, position in enumerate(valid_positions):
            if i == index:
                return position

    def _take_step(self):
        """
        Take a single game step.

        Returns
        -------
        None : :class:`NoneType`

        """

        self._snake.take_step()
        if self._snake.eat(self._apple):
            self._apple = self._generate_new_apple()

    def run(self):
        """
        Run the game.

        Returns
        -------
        None : :class:`NoneType`

        """

        while (
            not self._snake.hit(self._walls) and
            not self._snake.bite() and
            not self._snake.is_escaped(self._board_size)
        ):
            self._take_step()

    def run_stepwise(self):
        """
        Run the game, but yield after every step.

        Yields
        ------
        :class:`int`
            The step number.

        """

        step_number = 0
        while (
            not self._snake.hit(self._walls) and
            not self._snake.bite() and
            not self._snake.is_escaped(self._board_size)
        ):
            self._take_step()
            step_number += 1
            yield step_number

    def get_snake_velocity(self, step=0):
        """
        Return the step the snake will take.

        Parameters
        ----------
        step : :class:`int`, optional
            The step for which the velocity is returned. ``0`` is the
            current step.

        Returns
        -------
        :class:`tuple`
            The :class:`tuple` can be one of ``(0, 1)``, ``(0, -1)``,
            ``(1, 0)`` or ``(-1, 0)``, representing the step the
            snake will take.

        """

        return self._snake.get_velocity(step)

    def queue_snake_movement_direction(self, direction):
        """
        Queue a movement direction for the snake.

        When this method is called multiple times between snake steps,
        it allows the caller to queue multiple directions, which will
        be resolved at a rate of one per step.

        Parameters
        ----------
        direction : :class:`str`
            Can be ``'up'``, ``'down'``, ``'right'`` or ``'left'`` to
            signify the movement direction the snake will have the
            when it moves.

        Returns
        -------
        :class:`bool`
            ``True`` if a movement direction was successfully queued
            and ``False`` otherwise.

        """

        if direction == 'up':
            velocity = (0, 1)
        elif direction == 'down':
            velocity = (0, -1)
        elif direction == 'right':
            velocity = (1, 0)
        elif direction == 'left':
            velocity = (-1, 0)

        if self._snake.get_num_queued_velocities() < 5:
            self._snake.queue_velocity(velocity)
            return True

        return False

    def get_snake(self):
        """
        Yield the positions occupied by the snake.

        Yields
        ------
        :class:`tuple`
            The position of a segment of the snake's body.

        """

        yield from self._snake.get_body()

    def get_walls(self):
        """
        Yield the coordinates of the walls.

        Yields
        ------
        :class:`tuple`
            The position of a wall segment.

        """

        yield from self._walls

    def get_apple(self):
        """
        Return the coordinates of the apple.

        Returns
        -------
        :class:`tuple`
            A :class:`tuple` of the form ``(21, 12)``, holding the
            coordinates of the apple the snake is meant to eat.

        """

        return self._apple

    def get_board_size(self):
        """
        Return the board size.

        Returns
        -------
        :class:`tuple`
            A :class:`tuple` of the form ``(23, 12)`` which represents
            the size of the board in the x and y directions.

        """

        return self._board_size
