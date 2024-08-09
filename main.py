__version__ = "1.0"

import pygame

from pygame import QUIT, KEYDOWN, MOUSEBUTTONDOWN
from pygame.locals import DOUBLEBUF, FULLSCREEN

from core import StateManager, get_state_paths
from core.settings import Display
from core.errors import ExitGameError, ExitStateError


# icon = pygame.image.load("assets/icon.ico")
# pygame.display.set_icon(icon)
pygame.mixer.init()
pygame.init()
pygame.display.init()
pygame.display.set_caption("Dew Valley v" + __version__)
pygame.event.set_allowed((QUIT, KEYDOWN, MOUSEBUTTONDOWN))


class Main:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode(Display.SCREEN_RESOLUTION, DOUBLEBUF)
        self.screen.set_alpha(None)
        self.state_manager = StateManager(self.screen)

        state_paths = get_state_paths("states/")
        for state_path in state_paths:
            self.state_manager.connect_state_hook(state_path)

    def run(self) -> None:
        self.state_manager.change_state("Game")

        while True:
            try:
                self.state_manager.run_state()
            except ExitStateError:
                # Stuff you can do before a state is going to be changed / reset.
                pass


if __name__ == "__main__":
    try:
        game = Main()
        game.run()
    except ExitGameError:
        pygame.quit()
