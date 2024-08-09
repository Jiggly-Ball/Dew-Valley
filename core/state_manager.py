"""
This file contains classes related to screen management / screen changing.
"""

from __future__ import annotations

import os
import pygame
import importlib

from typing import Dict, Optional, Generator, Iterable, List
from core.errors import StateError, StateLoadError, ExitStateError, ExitGameError


class State:
    window: Optional[pygame.Surface] = None
    manager: Optional[StateManager] = None

    def __init__(self) -> None:
        self.clock = pygame.time.Clock()

    def setup(self) -> None:
        """This method is only called once before `State.run`, i.e right after the class has been instantiated
        inside the StateManager. This method will never be called ever again when changing / resetting States.
        """

    def run(self) -> None:
        """The main game loop method to be executed by the StateManager."""


class StateManager:
    __slots__ = (
        "__states",
        "__current_state",
        "__last_state",
    )

    def __init__(self, window: pygame.Surface) -> None:
        State.window = window
        State.manager = self

        self.__states: Dict[str, State] = {}
        self.__current_state: Optional[State] = None
        self.__last_state: Optional[State] = None

    def connect_state_hook(self, path: str, **kwargs) -> None:
        """Calls the hook function of the state file."""

        state = importlib.import_module(path)
        if "hook" not in state.__dict__:
            raise StateError(
                "\nAn error occurred in loading State Path-\n"
                f"`{path}`\n"
                "`hook` function was not found in state file to load.\n"
            )

        state.__dict__["hook"](**kwargs)

    def load_states(self, *states: type[State], **kwargs) -> None:
        for state in states:
            if state.__name__ in self.__states:
                raise StateLoadError(
                    f"State: {state.__name__} has already been loaded.",
                    last_state=self.__last_state,
                    **kwargs,
                )

            self.__states[state.__name__] = state(**kwargs)
            self.__states[state.__name__].setup()

    def unload_state(self, state_name: str, **kwargs) -> type[State]:
        if state_name not in self.__states:
            raise StateLoadError(
                f"State: {state_name} doesn't exist to be unloaded.",
                last_state=self.__last_state,
                **kwargs,
            )

        elif (
            self.__current_state is not None
            and state_name == self.__current_state.__name__
        ):
            raise StateError(
                "Cannot unload an actively running state.",
                last_state=self.__last_state,
                **kwargs,
            )

        cls_ref = self.__states[state_name].__class__
        del self.__states[state_name]
        return cls_ref

    def reload_state(self, state_name: str, **kwargs) -> None:
        deleted_cls = self.unload_state(state_name=state_name, **kwargs)
        self.load_states(deleted_cls, **kwargs)

    def get_current_state(self) -> Optional[State]:
        return self.__current_state

    def get_last_state(self) -> Optional[State]:
        return self.__last_state

    def get_all_states(self) -> Generator[str]:
        return (state for state in self.__states.keys())

    def get_state_map(self) -> Dict[str, State]:
        return self.__states.copy()

    def change_state(self, state_name: str) -> None:
        assert (
            state_name in self.__states
        ), f"State `{state_name}` isn't present from the available states: `{', '.join(self.get_all_states())}`."
        self.__last_state = self.__current_state
        self.__current_state = self.__states[state_name]

    def run_state(self, **kwargs) -> None:
        if self.__current_state is not None:
            self.__current_state.run()
        else:
            raise StateError(
                "No state has been set to run.", last_state=self.__last_state, **kwargs
            )

    def update_state(self, **kwargs) -> None:
        if self.__current_state is not None:
            raise ExitStateError(
                "State has successfully exited.", last_state=self.__last_state, **kwargs
            )
        raise StateError(
            "No state has been set to exit from.",
            last_state=self.__last_state,
            **kwargs,
        )

    def exit_game(self, **kwargs) -> None:
        raise ExitGameError(
            "Game has successfully exited.", last_state=self.__last_state, **kwargs
        )


def get_nested_state_paths(
    folder_dir: str,
    ignore_files: Iterable[str] = ("__init__.py",),
    ignore_folders: Iterable[str] = ("__pycache__",),
) -> List[str]:
    paths = []
    next_dir = None

    for dirpath, dirnames, filenames in os.walk(folder_dir):
        if next_dir in ignore_folders:
            continue
        if len(dirnames) > 0:
            next_dir = dirnames[0]

        for file in filenames:
            if file not in ignore_files and file.endswith(".py"):
                paths.append(
                    rf"{dirpath}/{file[:-3]}".replace("//", ".")
                    .replace("/", ".")
                    .replace("\\", ".")
                    .replace("\\\\", ".")
                )
    return paths


def get_state_paths(
    folder_dir: str, ignore_files: Iterable[str] = ("__init__.py",)
) -> List[str]:
    paths = []

    for dirpath, _, filenames in os.walk(folder_dir):
        for file in filenames:
            if file not in ignore_files and file.endswith(".py"):
                paths.append(
                    rf"{dirpath + file[:-3]}".replace("/", ".").replace("\\", ".")
                )
        break
    return paths
