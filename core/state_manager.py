"""
This file contains classes related to screen management / screen changing.
"""

from __future__ import annotations

import os
import pygame
import importlib

from typing import Dict, Optional, Iterable, List
from core.errors import StateError, StateLoadError, ExitStateError, ExitGameError


class State:
    window: Optional[pygame.Surface] = None
    manager: Optional[StateManager] = None

    def __init__(self) -> None:
        self.clock = pygame.time.Clock()

    def setup(self) -> None:
        """This method is only called once before `State.run`, i.e right after the class
        has been instantiated inside the StateManager. This method will never be called
        ever again when changing / resetting States.
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
        """
        Parameters
        ----------
        window: :class:`pygame.Surface`
            The main game window.
        """

        State.window = window
        State.manager = self

        self.__states: Dict[str, State] = {}
        self.__current_state: Optional[State] = None
        self.__last_state: Optional[State] = None

    def connect_state_hook(self, path: str, **kwargs) -> None:
        """Calls the hook function of the state file.

        Parameters
        ----------
        path: :class:`str`
            The path to the State file containing the hook function to be called.

        **kwargs:
            The keyword arguments to be passed to the hook function.

        Raises
        ------
        :exc:`StateError`
            Raised when the hook function was not found in the state file to be loaded.
        """

        state = importlib.import_module(path)
        if "hook" not in state.__dict__:
            raise StateError(
                "\nAn error occurred in loading State Path-\n"
                f"`{path}`\n"
                "`hook` function was not found in state file to load.\n",
                last_state=self.__last_state,
                **kwargs,
            )

        state.__dict__["hook"](**kwargs)

    def load_states(self, *states: type[State], force: bool = False, **kwargs) -> None:
        """Loads the States into the StateManager.

        Parameters
        ----------
        *states: :type:`State`
            The `State`s to be loaded into the manager.

        force: :class:`bool`, default `False`
            Loads the State regardless of whether the State has already been loaded or not
            without raising any internal error.

        **kwargs:
            The keyword arguments to be passed to the `State`'s subclass on instantiation.

        Raises
        ------
        :exc:`StateLoadError`
            Raised when the state has already been loaded.
            Only raised when `force` is set to `False`.
        """

        for state in states:
            if not force and state.__name__ in self.__states:
                raise StateLoadError(
                    f"State: {state.__name__} has already been loaded.",
                    last_state=self.__last_state,
                    **kwargs,
                )

            self.__states[state.__name__] = state(**kwargs)
            self.__states[state.__name__].setup()

    def unload_state(
        self, state_name: str, force: bool = False, **kwargs
    ) -> type[State]:
        """Loads the `State`s into the StateManager.

        Parameters
        ----------
        *states: :type:`State`
            The `State`s to be loaded into the manager.

        force: :class:`bool`, default `False`
            Unloads the State even if it's an actively running State without raising any
            internal error.
            **WARNING: If set to `True` it may lead to unexpected behavior.**

        **kwargs:
            The keyword arguments to be passed on to the raised errors.

        Returns
        --------
        type[:class:`State`]
            The :class:`State` class of the deleted State name.

        Raises
        ------
        :exc:`StateLoadError`
            Raised when the state doesn't exist in the manager to be unloaded.

        :exc:`StateError`
            Raised when trying to unload an actively running State.
            Only raised when `force` is set to `False`.
        """

        if state_name not in self.__states:
            raise StateLoadError(
                f"State: {state_name} doesn't exist to be unloaded.",
                last_state=self.__last_state,
                **kwargs,
            )

        elif (
            not force 
            and self.__current_state is not None
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

    def reload_state(self, state_name: str, force: bool = False, **kwargs) -> State:
        """Reloads the specified State. A short hand to `StateManager.unload_state` &
        `StateManager.load_state`.

        Parameters
        ----------
        *states: :type:`State`
            The `State`s to be loaded into the manager.

        force: :class:`bool`, default `False`
            Reloads the State even if it's an actively running State without raising any
            internal error.
            **WARNING: If set to `True` it may lead to unexpected behavior.**

        **kwargs:
            The keyword arguments to be passed to the `State`'s subclass on instantiation.

        Returns
        --------
        :class:`State`
            Returns the newly made :class:`State` instance.

        Raises
        ------
        :exc:`StateLoadError`
            Raised when the state has already been loaded.
        """

        deleted_cls = self.unload_state(state_name=state_name, force=force, **kwargs)
        self.load_states(deleted_cls, force=force, **kwargs)
        return self.__states[state_name]

    def get_current_state(self) -> Optional[State]:
        """Gets the current State instance.

        Returns
        --------
        Optional[:class:`State`]
            Returns the current State instance.
        """

        return self.__current_state

    def get_last_state(self) -> Optional[State]:
        """Gets the previous State instance.

        Returns
        --------
        Optional[:class:`State`]
            Returns the previous State instance.
        """

        return self.__last_state

    def get_state_map(self) -> Dict[str, State]:
        """Gets the dictionary copy of all states.

        Returns
        --------
        Dict[:class:`str`, :class:`State`]
            Returns the dictionary copy of all states.
        """

        return self.__states.copy()

    def change_state(self, state_name: str) -> None:
        """Changes the current state and updates the last state.

        Parameters
        ----------
        state_name: :class:`str`
            The name of the State you want to switch to.

        Raises
        ------
        :exc:`AssertionError`
            Raised when the state name doesn't exist in the manager.
        """

        assert (
            state_name in self.__states
        ), f"State `{state_name}` isn't present from the available states: "
        f"`{', '.join(self.get_state_map().keys())}`."

        self.__last_state = self.__current_state
        self.__current_state = self.__states[state_name]

    def update_state(self, **kwargs) -> None:
        """Updates the changed State to take in place.

        Parameters
        ----------
        **kwargs:
            The keyword arguments to be passed on to the raised errors.

        Raises
        ------
        :exc:`ExitStateError`
            Raised when the state has successfully exited.

        :exc:`StateError`
            Raised when the current state is `None` i.e having no State to update to.
        """

        if self.__current_state is not None:
            raise ExitStateError(
                "State has successfully exited.", last_state=self.__last_state, **kwargs
            )
        raise StateError(
            "No state has been set to exit from.",
            last_state=self.__last_state,
            **kwargs,
        )

    def run_state(self, **kwargs) -> None:
        """The entry point to running the StateManager. To be only called once. For
        changing `State`s use `StateManager.change_state` & `StateManager.update_state`

        Parameters
        ----------
        **kwargs:
            The keyword arguments to be passed on to the raised errors.

        Raises
        ------
        :exc:`StateError`
            Raised when the current state is `None` i.e having no State to run.
        """

        if self.__current_state is not None:
            self.__current_state.run()
        else:
            raise StateError(
                "No state has been set to run.", last_state=self.__last_state, **kwargs
            )

    def exit_game(self, **kwargs) -> None:
        """Exits the entire game.

        Parameters
        ----------
        **kwargs:
            The keyword arguments to be passed on to the raised errors.

        Raises
        ------
        :exc:`ExitStateError`
            Raised when the state has successfully exited.

        :exc:`StateError`
            Raised when the current state is `None` i.e having no State to update to.
        """

        raise ExitGameError(
            "Game has successfully exited.", last_state=self.__last_state, **kwargs
        )


def get_nested_paths(
    folder_dir: str,
    ignore_files: Iterable[str] = ("__init__.py",),
    ignore_folders: Iterable[str] = ("__pycache__",),
) -> List[str]:
    """Gets the paths of all python files in a nested directory.

    Parameters
    ----------
    folder_dir: :class:`str`
        The directory to where the nested files.

    ignore_files: :class:`Iterable[str]`, default `("__init__.py",)`
        Ignores these files from the final list of paths.

    ignore_folders: :class:`Iterable[str]`, default `("__pycache__",)`
        Ignores files present in these folders.

    Returns
    --------
    List[:class:`str`]
        Returns a list containing the paths of all nested python files.
    """

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


def get_paths(
    folder_dir: str, ignore_files: Iterable[str] = ("__init__.py",)
) -> List[str]:
    """Gets the paths of all python files in a directory.

    Parameters
    ----------
    folder_dir: :class:`str`
        The directory to where the nested files.

    ignore_files: :class:`Iterable[str]`, default `("__init__.py",)`
        Ignores these files from the final list of paths.

    Returns
    --------
    List[:class:`str`]
        Returns a list containing the paths of all python files.
    """

    paths = []

    for dirpath, _, filenames in os.walk(folder_dir):
        for file in filenames:
            if file not in ignore_files and file.endswith(".py"):
                paths.append(
                    rf"{dirpath + file[:-3]}".replace("/", ".").replace("\\", ".")
                )
        break
    return paths
