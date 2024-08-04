from __future__ import annotations

import os
import pygame
from typing import Dict, List, Optional, Callable, Generic, TypeVar

T = TypeVar("T")


class Animation:
    def __init__(
        self,
        frames: Dict[str, List[pygame.Surface]],
        *,
        sprite: Optional[pygame.sprite.Sprite] = None,
        speed: int = 4,
        ignore_invalid_state: bool = True,
    ) -> None:
        self.frames = frames
        self.sprite = sprite
        self.speed = speed
        self.ignore_invalid_state = ignore_invalid_state

        self.status: Optional[str] = None
        # self.last_status: Optional[str] = None
        self.current_frame = 0
        self.max_frames = 0

    def get_frame(self, frame: int) -> pygame.Surface:
        return self.frames[self.status][frame]

    def set_status(self, animation: str) -> None:
        if not self.ignore_invalid_state:
            assert (
                animation in self.frames
            ), f"{animation} is not present in list of animations: {self.frames.keys()}"

        if animation in self.frames:
            # if animation != self.status:
            self.status = animation
            # self.current_frame = 0
            self.max_frames = len(self.frames[self.status]) - 1

    def play_status(self, dt: int) -> pygame.Surface:
        if not self.ignore_invalid_state:
            assert (
                self.ignore_invalid_state or self.status is not None
            ), "No animation state has been set to run"

        self.current_frame += self.speed * dt
        if self.current_frame > self.max_frames:
            self.current_frame = 0
        return self.frames[self.status][round(self.current_frame)]

    def play_status_ip(self, dt: int) -> None:
        assert (
            self.sprite is not None
        ), "No sprite has been passed to play the status in-place."
        self.current_frame += self.speed * dt
        if self.current_frame > self.max_frames:
            self.current_frame = 0
        self.sprite.image = self.frames[self.status][round(self.current_frame)]


class Timer:
    def __init__(self, duration: int, func: Optional[Callable] = None) -> None:
        self.duration = duration
        self.func = func
        self.start_time = 0
        self.active = False

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time >= self.duration:
            if self.func and self.start_time != 0:
                self.func()
            self.deactivate()


class ItemIterator(Generic[T]):
    def __init__(self, seq: List[T]) -> None:
        self.seq = seq
        self.index = 0
        self.selected = seq[0]
        self.max_index = len(seq) - 1
        self.inv: Dict[T, int] = {key: 1 for key in seq}

    def next(self) -> None:
        self.index += 1
        if self.index > self.max_index:
            self.index = 0
        self.selected = self.seq[self.index]

    def previous(self) -> None:
        self.index -= 1
        if self.index < 0:
            self.index = self.max_index
        self.selected = self.seq[self.index]

    def append(self, element: T) -> None:
        self.seq.append(element)
        self.inv[element] = 0
        self.max_index += 1

    def remove(self, element: T) -> None:
        self.seq.remove(element)
        self.seq = len(self.seq)
        del self.inv[element]

    def update_item(self, item: T, amount: int = 1) -> None:
        if item not in self.seq:
            self.append(item)
        self.inv[item] += amount

    def set_item(self, item: T, value: int) -> None:
        self.inv[item] = value


def import_folder(path: str) -> List[pygame.Surface]:
    surface_list = []
    for folder, _, image_files in os.walk(path):
        for image in image_files:
            full_path = f"{folder}/{image}"
            surface = pygame.image.load(full_path).convert_alpha()
            surface_list.append(surface)
    return surface_list


def import_folder_dict(path: str) -> dict:
    surface_dict = {}

    for _, __, img_files in os.walk(path):
        for image in img_files:
            full_path = path + "/" + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_dict[image.split(".")[0]] = image_surf

    return surface_dict
