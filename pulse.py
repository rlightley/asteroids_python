import math

import pygame

from circleshape import CircleShape
from constants import PULSE_COLOR
from constants import PULSE_CORE_COLOR
from constants import PULSE_GROWTH_SPEED
from constants import PULSE_LIFETIME_SECONDS
from constants import PULSE_MAX_RADIUS_FACTOR


class PulseWave(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, 1)
        self.elapsed = 0.0
        surface = pygame.display.get_surface()
        if surface is None:
            width, height = 1280, 720
        else:
            width, height = surface.get_size()
        diagonal = math.hypot(width, height)
        self.max_radius = diagonal * PULSE_MAX_RADIUS_FACTOR
        self.radius = 1

    def draw(self, screen):
        glow_radius = int(self.radius + 18)
        glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        center = pygame.Vector2(glow_radius, glow_radius)
        pygame.draw.circle(glow_surface, (*PULSE_COLOR, 30), center, glow_radius, width=16)
        pygame.draw.circle(glow_surface, (*PULSE_CORE_COLOR, 80), center, max(1, int(self.radius)), width=4)
        screen.blit(glow_surface, (self.position.x - glow_radius, self.position.y - glow_radius))

        pygame.draw.circle(screen, PULSE_COLOR, self.position, int(self.radius), width=6)
        pygame.draw.circle(screen, PULSE_CORE_COLOR, self.position, max(1, int(self.radius * 0.72)), width=2)

    def update(self, dt):
        self.elapsed += dt
        self.radius = min(self.max_radius, self.radius + PULSE_GROWTH_SPEED * dt)
        if self.elapsed >= PULSE_LIFETIME_SECONDS or self.radius >= self.max_radius:
            self.kill()