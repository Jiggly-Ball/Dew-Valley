"""
This file contains classes related to screen management / screen changing.
"""

from __future__ import annotations

import pygame
from typing import Dict, Optional, Generator
from core.errors import StateError, ExitStateError, ExitGameError


class State:
    window: Optional[pygame.Surface] = None
    manager: Optional[StateManager] = None

    def __init__(self) -> None:
        self.clock = pygame.time.Clock()

    def setup(self) -> None:
        """This method is only called once before `State.run` i.e when the class is being instantiated inside
        the StateManager. This method will  never be called ever again when changing / resetting States.
        """

    def run(self) -> None:
        """The main game loop method to be executed by the StateManager."""


class StateManager:
    __slots__ = (
        "__states",
        "__current_state",
        "__last_state",
    )

    def __init__(self, window: pygame.Surface, *states: State, **kwargs) -> None:
        for state in states:
            assert issubclass(
                state, State
            ), f"Expected subclass of `{State}` instead got `{state.__mro__[-2]}`."
        State.window = window
        State.manager = self

        self.__states: Dict[str, State] = {}
        for class_ in states:
            self.__states[class_.__name__] = class_(**kwargs)
            self.__states[class_.__name__].setup()

        self.__current_state: Optional[State] = None
        self.__last_state: Optional[State] = None

    def change_state(self, state_name: str) -> None:
        assert (
            state_name in self.__states
        ), f"State `{state_name}` isn't present from the available states: `{', '.join(self.get_all_states())}`."
        self.__last_state = self.__current_state
        self.__current_state = self.__states[state_name]

    def get_last_state(self) -> Optional[State]:
        return self.__last_state

    def get_state(self) -> Optional[State]:
        return self.__current_state

    def get_all_states(self) -> Generator[str]:
        return (state for state in self.__states.keys())

    def run_state(self) -> None:
        if self.__current_state is not None:
            self.__current_state.run()
        else:
            raise StateError("No state has been set to run.")

    def update_state(self) -> None:
        if self.__current_state is not None:
            raise ExitStateError(
                "State has successfully exited.", last_state=self.__last_state
            )
        else:
            raise StateError(
                "No state has been set to exit from.", last_state=self.__last_state
            )

    def exit_game(self) -> None:
        raise ExitGameError(
            "Game has successfully exited.", last_state=self.__last_state
        )
