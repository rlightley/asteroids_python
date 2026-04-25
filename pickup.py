import math

import pygame

from circleshape import CircleShape
from constants import PICKUP_GLOW_COLOR
from constants import PICKUP_COLOR
from constants import PICKUP_METAL_COLOR
from constants import PULSE_PICKUP_COLOR
from constants import PULSE_PICKUP_GLOW_COLOR
from constants import ROCKET_PICKUP_DURATION_SECONDS
from constants import ROCKET_PICKUP_RADIUS


class SupplyPickup(CircleShape):
    def __init__(self, x, y, amount, body_color, glow_color):
        super().__init__(x, y, ROCKET_PICKUP_RADIUS)
        self.amount = amount
        self.timer = ROCKET_PICKUP_DURATION_SECONDS
        self.phase = 0.0
        self.body_color = body_color
        self.glow_color = glow_color

    def draw(self, screen):
        pulse = 1.0 + math.sin(self.phase * 4) * 0.12
        radius = int(self.radius * pulse)
        glow_surface = pygame.Surface((radius * 5, radius * 5), pygame.SRCALPHA)
        glow_center = pygame.Vector2(glow_surface.get_width() / 2, glow_surface.get_height() / 2)
        pygame.draw.circle(glow_surface, (*self.glow_color, 42), glow_center, radius + 8)
        screen.blit(glow_surface, (self.position.x - glow_surface.get_width() / 2, self.position.y - glow_surface.get_height() / 2))

        body = pygame.Rect(0, 0, radius * 1.8, radius * 1.15)
        body.center = self.position
        pygame.draw.rect(screen, PICKUP_METAL_COLOR, body, border_radius=6)
        pygame.draw.rect(screen, self.body_color, body, width=2, border_radius=6)
        pygame.draw.rect(screen, (245, 250, 255), body.inflate(-body.width * 0.5, -body.height * 0.46), border_radius=4)
        pygame.draw.line(screen, (94, 102, 124), body.midleft, body.midright, width=2)
        pygame.draw.line(screen, (94, 102, 124), body.center + pygame.Vector2(0, -body.height * 0.35), body.center + pygame.Vector2(0, body.height * 0.35), width=2)

        cap_radius = max(3, int(radius * 0.24))
        pygame.draw.circle(screen, self.body_color, body.midleft, cap_radius)
        pygame.draw.circle(screen, self.body_color, body.midright, cap_radius)

    def update(self, dt):
        self.timer -= dt
        self.phase += dt
        if self.timer <= 0:
            self.kill()


class RocketPickup(SupplyPickup):
    def __init__(self, x, y, amount):
        super().__init__(x, y, amount, PICKUP_COLOR, PICKUP_GLOW_COLOR)


class PulsePickup(SupplyPickup):
    def __init__(self, x, y, amount):
        super().__init__(x, y, amount, PULSE_PICKUP_COLOR, PULSE_PICKUP_GLOW_COLOR)