from core import State


class Menu(State):
    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None: ...


def hook(**kwargs) -> None:
    Menu.manager.load_states(Menu, **kwargs)
