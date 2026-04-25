import pygame
import random
from asteroid import Asteroid
from constants import *

class AsteroidField(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.spawn_timer = 0.0
        self.level = 1
        self.spawn_enabled = False

    def _playfield_size(self):
        surface = pygame.display.get_surface()
        if surface is None:
            return SCREEN_WIDTH, SCREEN_HEIGHT
        return surface.get_size()

    def _spawn_origin(self, radius):
        width, height = self._playfield_size()
        visual_radius = radius * 1.35
        inset = visual_radius + 18
        edge = random.choice(("left", "right", "top", "bottom"))

        min_x = min(inset, width / 2)
        max_x = max(min_x, width - inset)
        min_y = min(inset, height / 2)
        max_y = max(min_y, height - inset)

        if edge == "left":
            return pygame.Vector2(1, 0), pygame.Vector2(min_x, random.uniform(min_y, max_y))
        if edge == "right":
            return pygame.Vector2(-1, 0), pygame.Vector2(max_x, random.uniform(min_y, max_y))
        if edge == "top":
            return pygame.Vector2(0, 1), pygame.Vector2(random.uniform(min_x, max_x), min_y)
        return pygame.Vector2(0, -1), pygame.Vector2(random.uniform(min_x, max_x), max_y)

    def spawn(self, radius, position, velocity):
        asteroid = Asteroid(position.x, position.y, radius)
        asteroid.velocity = velocity
        bounds = asteroid.visual_bounds()
        width, height = self._playfield_size()

        shift_x = 0
        shift_y = 0

        if bounds.left < 0:
            shift_x = -bounds.left
        elif bounds.right > width:
            shift_x = width - bounds.right

        if bounds.top < 0:
            shift_y = -bounds.top
        elif bounds.bottom > height:
            shift_y = height - bounds.bottom

        if shift_x != 0 or shift_y != 0:
            asteroid.shift(pygame.Vector2(shift_x, shift_y))

    def spawn_wave(self, wave_number):
        self.spawn_enabled = False
        self.spawn_timer = -ASTEROID_WAVE_START_DELAY_SECONDS
        wave_count = ASTEROID_WAVE_BASE_COUNT + max(0, wave_number - 1) * ASTEROID_WAVE_GROWTH
        for _ in range(wave_count):
            kind = random.randint(1, ASTEROID_KINDS)
            radius = ASTEROID_MIN_RADIUS * kind
            direction, position = self._spawn_origin(radius)
            speed = random.randint(60, 140 + wave_number * 10)
            velocity = direction * speed
            velocity = velocity.rotate(random.randint(-45, 45))
            self.spawn(radius, position, velocity)

    def set_level(self, level):
        self.level = max(1, level)

    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer < 0:
            return

        self.spawn_enabled = True
        spawn_rate = max(0.25, ASTEROID_SPAWN_RATE_SECONDS - (self.level - 1) * 0.05)
        if self.spawn_enabled and self.spawn_timer > spawn_rate:
            self.spawn_timer = 0

            kind = random.randint(1, ASTEROID_KINDS)
            radius = ASTEROID_MIN_RADIUS * kind
            direction, position = self._spawn_origin(radius)
            speed = random.randint(40, 100)
            velocity = direction * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            self.spawn(radius, position, velocity)
