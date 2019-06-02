.. snake documentation master file, created by
   sphinx-quickstart on Mon Jun  3 00:23:56 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to snake's documentation!
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:


This is a simple snake game. The original purpose was to create a game
for use with reinforcement learning, but the game can be played
in the terminal by humans. If you want to use the game for
reinforcement learning you only need :class:`.SnakeGame`. This will
create a self-contained instance of a game of snake which can be
interacted with programatically.

When the game is run in the terminal it is wrapped by :class:`.GameIO`,
which captures keyboard input and sends it to :class:`.SnakeGame` and
also writes the state of the game to the screen.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
