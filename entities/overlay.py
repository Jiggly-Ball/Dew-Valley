import pygame
from entities.player import Player
from core.settings import Display


class Overlay:
    def __init__(self, player: Player, display: pygame.Surface) -> None:
        self.display_surface = display
        self.player = player

        overlay_path = "graphics/images/overlay"
        fruit_path = "graphics/images/fruit"
        self.tools_surf = {
            tool: pygame.image.load(f"{overlay_path}/{tool}.png").convert_alpha()
            for tool in player.inventory.seq
        }
        self.tools_surf["apple"] = pygame.image.load(
            f"{fruit_path}/apple.png"
        ).convert_alpha()

    def draw(self) -> None:
        tool_surf = self.tools_surf[self.player.inventory.selected]
        tool_rect = tool_surf.get_rect(
            center=(
                Display.SCREEN_RESOLUTION[0] / 1.2,
                Display.SCREEN_RESOLUTION[1] / 1.3,
            )
        )
        self.display_surface.blit(tool_surf, tool_rect)
