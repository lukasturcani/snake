def test_take_step(snake):
    assert False


def test_valid_velocity(snake):
    assert False


def test_hit(snake):
    assert not snake.hit(frozenset())

    walls = frozenset({

    })

    assert snake.hit(walls)

    walls = frozenset({

    })

    assert not snake.hit(walls)


def test_bite(snake, bit_snake):
    assert not snake.bite()
    assert bit_snake.bite()


def test_escape(snake):
    max_x = max(x for x, y in snake.body)
    max_y = max(y for x, y in snake.body)

    assert not snake.escape((max_x-1, max_y-1))
    assert snake.escape((max_x-1, max_y))
    assert snake.escape((max_x, max_y-1))


def test_eat(snake):
    head = snake.body[-1]
    assert snake.eat(head)

    apple = (head[0]+1, head[1]+1)
    assert not snake.eat(apple)


def test_generate_new_apple(game):
    ...


def test_run(game):
    ...


def test_snake_velocity(game):
    ...


def test_queue_snake_movement_direction(game):
    ...


def test_get_snake(game):
    ...


def test_get_walls(game):
    ...


def test_get_apple(game):
    ...


def test_get_board_size(game):
    ...
