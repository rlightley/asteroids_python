from circleshape import CircleShape
from constants import ASTEROID_COLOR
from constants import ASTEROID_DARK_COLOR
from constants import ASTEROID_HIGHLIGHT_COLOR
from constants import ASTEROID_MIN_RADIUS
from constants import ASTEROID_SHADOW_COLOR
from logger import log_event
import math
import pygame
import random

class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.core_radius = radius
        self.profile = self._generate_profile()
        self.radius = self.core_radius * 1.22

    def _generate_profile(self):
        profile = []
        vertex_count = max(9, int(self.core_radius / 5) + 7)
        for index in range(vertex_count):
            angle = (360 / vertex_count) * index + random.uniform(-8, 8)
            magnitude = self.core_radius * random.uniform(0.78, 1.18)
            profile.append((angle, magnitude))
        return profile

    def outline_points(self):
        return [
            pygame.Vector2(0, 1).rotate(angle) * magnitude + self.position
            for angle, magnitude in self.profile
        ]

    def visual_bounds(self):
        points = self.outline_points()
        shadow_points = [
            point + pygame.Vector2(self.core_radius * 0.12, self.core_radius * 0.14)
            for point in points
        ]
        points.extend(shadow_points)

        min_x = min(point.x for point in points)
        max_x = max(point.x for point in points)
        min_y = min(point.y for point in points)
        max_y = max(point.y for point in points)

        highlight_rect = pygame.Rect(0, 0, self.core_radius * 1.5, self.core_radius * 1.15)
        highlight_rect.center = (self.position.x - self.core_radius * 0.08, self.position.y - self.core_radius * 0.1)
        min_x = min(min_x, highlight_rect.left)
        max_x = max(max_x, highlight_rect.right)
        min_y = min(min_y, highlight_rect.top)
        max_y = max(max_y, highlight_rect.bottom)

        return pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)

    def shift(self, delta):
        self.position += delta

    def draw(self, screen):
        points = self.outline_points()
        shadow_points = [point + pygame.Vector2(self.core_radius * 0.12, self.core_radius * 0.14) for point in points]
        pygame.draw.polygon(screen, ASTEROID_SHADOW_COLOR, shadow_points, width=0)
        pygame.draw.polygon(screen, ASTEROID_DARK_COLOR, points, width=0)
        pygame.draw.polygon(screen, ASTEROID_COLOR, points, width=2)

        highlight_arc_rect = pygame.Rect(0, 0, self.core_radius * 1.5, self.core_radius * 1.15)
        highlight_arc_rect.center = (self.position.x - self.core_radius * 0.08, self.position.y - self.core_radius * 0.1)
        pygame.draw.arc(screen, ASTEROID_HIGHLIGHT_COLOR, highlight_arc_rect, 3.6, 5.4, width=2)

        crater_positions = (
            pygame.Vector2(self.core_radius * 0.22, -self.core_radius * 0.18),
            pygame.Vector2(-self.core_radius * 0.18, self.core_radius * 0.12),
            pygame.Vector2(self.core_radius * 0.05, self.core_radius * 0.28),
        )
        for crater in crater_positions:
            crater_center = self.position + crater
            pygame.draw.circle(screen, ASTEROID_SHADOW_COLOR, crater_center, max(3, int(self.core_radius * 0.16)), width=0)
            pygame.draw.circle(screen, ASTEROID_COLOR, crater_center + pygame.Vector2(-1, -1), max(2, int(self.core_radius * 0.1)), width=1)

    def update(self, dt):
        self.position += self.velocity * dt
        self.wrap_position()

    def split(self):
        self.kill()
        if self.core_radius <= ASTEROID_MIN_RADIUS:
            return
        log_event("asteroid_split")
        angle = random.uniform(20, 50)
        new_radius = self.core_radius - ASTEROID_MIN_RADIUS
        v1 = self.velocity.rotate(angle)
        v2 = self.velocity.rotate(-angle)
        a1 = Asteroid(self.position.x, self.position.y, new_radius)
        a2 = Asteroid(self.position.x, self.position.y, new_radius)
        a1.velocity = v1 * 1.2
        a2.velocity = v2 * 1.2
