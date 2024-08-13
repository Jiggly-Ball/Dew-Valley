from typing import Tuple

from states.game import Game
from core import State

GAME_STATES: Tuple[type[State], ...] = (Game,)
