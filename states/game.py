import os
import pygame
import random
from pytmx.util_pygame import load_pygame

from core import State
from core.settings import (
    Display,
    BACKGROUND_COLOUR,
    LAYERS,
    TILE_SIZE,
    CHARACTER_ANIMATIONS,
)
from core.utils import Animation, import_folder, get_path
from entities.player import Player, CameraGroup
from entities.overlay import Overlay
from entities.sprites import BaseSprite, Particle, Interaction, Water, Wildflower, Tree
from entities.transition import Transition
from entities.soil import SoilLayer
from entities.sky import Rain, Sky
from entities.trader import Trader


class Game(State):
    def __init__(self) -> None:
        super().__init__()

        self.all_sprites = CameraGroup(State.window)  # type: ignore
        self.collision_sprites = pygame.sprite.Group()
        self.tree_sprites = pygame.sprite.Group()
        self.interaction_sprites = pygame.sprite.Group()

        self.sky = Sky(State.window)
        self.rain = Rain(self.all_sprites)
        self.raining = random.randint(0, 10) > 7
        self.soil_layer = SoilLayer(
            self.all_sprites, self.collision_sprites, self.raining
        )

        self.player_animation = Animation(
            {
                animation: import_folder(f"{CHARACTER_ANIMATIONS}/{animation}/")
                for animation in os.listdir(CHARACTER_ANIMATIONS)
            }
        )
        self.player_animation.set_status("down_idle")
        self.player = Player(
            (0, 0),
            self.player_animation,
            self.all_sprites,
            self.collision_sprites,
            self.tree_sprites,
            self.interaction_sprites,
            self.soil_layer,
        )
        self.trader = Trader(self.player)

        self.transition = Transition(self.reset, self.player, State.window)
        self.overlay = Overlay(self.player, State.window)  # type: ignore
        self.tmx_data = load_pygame(get_path("../graphics/data/map.tmx"))

    def setup(self) -> None:
        # World Map
        BaseSprite(
            (0, 0),
            pygame.image.load("graphics/images/world/ground.png").convert_alpha(),
            self.all_sprites,
            LAYERS["ground"],
        )

        for obj in self.tmx_data.get_layer_by_name("Player"):
            if obj.name == "Start":
                self.player.position.x = obj.x
                self.player.position.y = obj.y

            elif obj.name == "Bed":
                Interaction(
                    (obj.x, obj.y),
                    (obj.width, obj.height),
                    self.interaction_sprites,
                    LAYERS["main"],
                    obj.name,
                )

            elif obj.name == "Trader":
                Interaction(
                    (obj.x, obj.y),
                    (obj.width, obj.height),
                    self.interaction_sprites,
                    LAYERS["main"],
                    obj.name,
                )

        # Collision tiles
        for x, y, _ in self.tmx_data.get_layer_by_name("Collision").tiles():
            BaseSprite(
                (x * TILE_SIZE, y * TILE_SIZE),
                pygame.Surface((TILE_SIZE, TILE_SIZE)),
                self.collision_sprites,
                LAYERS["main"],
            )

        # House furnitures
        for layer in ("HouseFloor", "HouseFurnitureBottom"):
            for x, y, surface in self.tmx_data.get_layer_by_name(layer).tiles():
                BaseSprite(
                    (x * TILE_SIZE, y * TILE_SIZE),
                    surface,
                    self.all_sprites,
                    LAYERS["house_bottom"],
                )
        for layer in ("HouseWalls", "HouseFurnitureTop", "Fence"):
            for x, y, surface in self.tmx_data.get_layer_by_name(layer).tiles():
                BaseSprite(
                    (x * TILE_SIZE, y * TILE_SIZE),
                    surface,
                    (
                        self.all_sprites
                        if layer != "Fence"
                        else [self.all_sprites, self.collision_sprites]
                    ),
                    LAYERS["main"],
                )

        for obj in self.tmx_data.get_layer_by_name("Trees"):
            Tree(
                (obj.x, obj.y),
                obj.image,
                [self.all_sprites, self.collision_sprites, self.tree_sprites],
                LAYERS["main"],
                obj.name,
                self.all_sprites,
                self.player,
            )

        # Decorations
        for obj in self.tmx_data.get_layer_by_name("Decoration"):
            Wildflower(
                (obj.x, obj.y),
                obj.image,
                [self.all_sprites, self.collision_sprites],
                LAYERS["main"],
            )

        # Water
        for x, y, surface in self.tmx_data.get_layer_by_name("Water").tiles():
            Water(
                (x * TILE_SIZE, y * TILE_SIZE),
                self.all_sprites,
                LAYERS["water"],
            )

    def plant_collision(self) -> None:
        if self.soil_layer.plant_sprites:
            for plant in self.soil_layer.plant_sprites.sprites():
                if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
                    self.player.inventory.update_item(plant.plant_type, 2)
                    plant.kill()
                    Particle(
                        plant.rect.topleft,
                        plant.image,
                        self.all_sprites,
                        z=LAYERS["main"],
                    )

                    x = plant.rect.centerx // TILE_SIZE
                    y = plant.rect.centery // TILE_SIZE
                    self.soil_layer.grid[y][x].remove("P")

    def reset(self) -> None:
        self.soil_layer.update_plants()

        self.raining = random.randint(0, 10) > 7
        self.soil_layer.raining = self.raining

        if self.raining:
            self.soil_layer.water_all()
        else:
            self.soil_layer.remove_water()

        for tree in self.tree_sprites.sprites():
            for apple in tree.apple_sprites.sprites():
                apple.kill()
            tree.create_apple()

        self.sky.start_color = [255, 255, 255]

    def run(self) -> None:
        while True:
            dt = self.clock.tick(Display.FPS) / 1000
            self.window.fill(BACKGROUND_COLOUR)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.manager.exit_game()

            self.all_sprites.draw(self.player)
            self.overlay.draw(dt=dt)
            self.sky.display(dt=dt)

            if self.player.toggle_active:
                self.trader.update()
            else:
                self.all_sprites.update(dt)
                self.plant_collision()
                if self.raining:
                    self.rain.update()

                if self.player.sleep:
                    self.transition.run()

            pygame.display.update()
