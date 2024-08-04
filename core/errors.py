from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from core import State
else:

    class State: ...


class BaseError(Exception):
    """The base class to all errors in Snake Game."""

    def __init__(self, *args, last_state: Optional[State] = None) -> None:
        super().__init__(*args)
        self.last_state = last_state


class StateError(BaseError):
    """Raised when a operation is done over an invalid state."""

    def __init__(self, *args, last_state: Optional[State] = None) -> None:
        super().__init__(*args, last_state=last_state)


class ExitStateError(BaseError):
    """An error class used to exit the current state."""

    def __init__(self, *args, last_state: Optional[State] = None) -> None:
        super().__init__(*args, last_state=last_state)


class ExitGameError(BaseError):
    """An error class used to exit out of the game"""

    def __init__(self, *args, last_state: Optional[State] = None) -> None:
        super().__init__(*args, last_state=last_state)
