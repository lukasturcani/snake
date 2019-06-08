from snake.age import Snake
from collections import deque
import pytest


@pytest.fixture(scope='session')
def snake():
    s = Snake()
    s.body = deque([
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 3),
        (2, 3),
        (3, 3),
        (4, 3)
    ])
    return s


def bit_snake():
    s = Snake()
    s.body = deque([
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 3),
        (2, 3),
        (3, 3),
        (4, 3)
    ])
    return s
