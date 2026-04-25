from circleshape import CircleShape
from constants import ROCKET_CORE_COLOR
from constants import ROCKET_LIFETIME_SECONDS
from constants import ROCKET_TRAIL_COLOR
from constants import SHOT_GLOW_COLOR
from constants import SHOT_LIFETIME_SECONDS
import pygame


def _draw_glow_circle(screen, color, position, radius, alpha):
    size = radius * 4
    glow_surface = pygame.Surface((size, size), pygame.SRCALPHA)
    center = pygame.Vector2(size / 2, size / 2)
    pygame.draw.circle(glow_surface, (*color, alpha), center, radius)
    pygame.draw.circle(glow_surface, (*color, alpha // 3), center, int(radius * 1.55), width=3)
    screen.blit(glow_surface, (position.x - size / 2, position.y - size / 2))


def _draw_glow_polygon(screen, color, points, padding):
    min_x = min(point.x for point in points) - padding
    max_x = max(point.x for point in points) + padding
    min_y = min(point.y for point in points) - padding
    max_y = max(point.y for point in points) + padding
    glow_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    glow_surface = pygame.Surface((max(1, int(glow_rect.width)), max(1, int(glow_rect.height))), pygame.SRCALPHA)
    translated_points = [pygame.Vector2(point.x - glow_rect.x, point.y - glow_rect.y) for point in points]
    pygame.draw.polygon(glow_surface, (*color, 48), translated_points, width=6)
    pygame.draw.polygon(glow_surface, (*color, 20), translated_points, width=12)
    screen.blit(glow_surface, glow_rect.topleft)


class Shot(CircleShape):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius)
        self.color = color
        self.lifetime = SHOT_LIFETIME_SECONDS

    def draw(self, screen):
        direction = self.velocity.normalize() if self.velocity.length_squared() > 0 else pygame.Vector2(0, 1)
        tail = self.position - direction * (self.radius * 2.6)
        _draw_glow_circle(screen, SHOT_GLOW_COLOR, self.position, self.radius + 3, 52)
        pygame.draw.line(screen, SHOT_GLOW_COLOR, tail, self.position, width=max(2, self.radius + 2))
        pygame.draw.circle(screen, self.color, self.position, self.radius)
        pygame.draw.circle(screen, (255, 255, 255), self.position, max(1, self.radius - 2))

    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0 or self.is_offscreen():
            self.kill()

    def is_offscreen(self):
        surface = pygame.display.get_surface()
        if surface is None:
            width, height = 1280, 720
        else:
            width, height = surface.get_size()

        margin = self.radius * 2
        return (
            self.position.x < -margin
            or self.position.x > width + margin
            or self.position.y < -margin
            or self.position.y > height + margin
        )

class RocketShot(Shot):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius, color)
        self.color = color
        self.lifetime = ROCKET_LIFETIME_SECONDS

    def draw(self, screen):
        direction = self.velocity.normalize() if self.velocity.length_squared() > 0 else pygame.Vector2(0, 1)
        right = direction.rotate(90)
        nose = self.position + direction * (self.radius * 1.3)
        left_front = self.position + right * (self.radius * 0.42)
        right_front = self.position - right * (self.radius * 0.42)
        left_fin = self.position - direction * (self.radius * 0.75) + right * (self.radius * 0.62)
        right_fin = self.position - direction * (self.radius * 0.75) - right * (self.radius * 0.62)
        tail = self.position - direction * (self.radius * 1.45)
        hull = [nose, left_front, left_fin, tail, right_fin, right_front]

        flame_outer = [
            tail + right * (self.radius * 0.22),
            tail - direction * (self.radius * 0.9),
            tail - right * (self.radius * 0.22),
        ]
        flame_inner = [
            tail + right * (self.radius * 0.1),
            tail - direction * (self.radius * 0.55),
            tail - right * (self.radius * 0.1),
        ]

        _draw_glow_polygon(screen, self.color, hull, 16)
        _draw_glow_polygon(screen, ROCKET_TRAIL_COLOR, flame_outer, 18)
        pygame.draw.polygon(screen, ROCKET_TRAIL_COLOR, flame_outer, width=0)
        pygame.draw.polygon(screen, (255, 235, 190), flame_inner, width=0)
        pygame.draw.polygon(screen, self.color, hull, width=0)
        pygame.draw.polygon(screen, ROCKET_CORE_COLOR, [nose, left_front, self.position, right_front], width=0)
        pygame.draw.line(screen, (120, 20, 24), tail, nose, width=2)

    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        if self.lifetime <= 0 or self.is_offscreen():
            self.kill()
