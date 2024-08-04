from typing import Tuple, Union, Sequence, TypeAlias, Dict
from pygame import Vector2

ColourType: TypeAlias = Union[int, str, Sequence[int]]


class Display:
    SCREEN_RESOLUTION: Tuple[int, int] = (1280, 720)
    ALL_RESOLUTIONS: Tuple[Tuple[int, int], ...] = (
        (1920, 1080),  # recheck
        (1600, 900),  # ok
        (1366, 768),  # ok
        (1280, 720),  # ok
        (1024, 600),  # overlay check
    )
    FPS: int = 120


TILE_SIZE: int = 64
BACKGROUND_COLOUR: ColourType = "black"
LAYERS: Dict[str, int] = {
    "water": 0,
    "ground": 1,
    "soil": 2,
    "soil_water": 3,
    "rain_floor": 4,
    "house_bottom": 5,
    "ground_plant": 6,
    "main": 7,
    "house_top": 8,
    "fruit": 9,
    "rain_drops": 10,
}
PLAYER_TOOL_OFFSET: Dict[str, Vector2] = {
    "left": Vector2(-50, 40),
    "right": Vector2(50, 40),
    "up": Vector2(0, -10),
    "down": Vector2(0, 50),
}
APPLE_POS: Dict[str, Tuple[Tuple[int, int], ...]] = {
    "Small": ((18, 17), (30, 37), (12, 50), (30, 45), (20, 30), (30, 10)),
    "Large": ((30, 24), (50, 65), (50, 50), (16, 40), (45, 50), (42, 70)),
}
GROW_SPEED = {"corn": 1, "tomato": 0.7}
CHARACTER_ANIMATIONS: str = "graphics/images/character"
WATER_ANIMATIONS: str = "graphics/images/water"
