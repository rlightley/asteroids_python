import pygame

from constants import SCREEN_HEIGHT
from constants import SCREEN_WIDTH

# Base class for game objects
class CircleShape(pygame.sprite.Sprite):
    def __init__(self, x, y, radius):
        # we will be using this later
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.radius = radius

    def draw(self, screen):
        # must override
        pass

    def update(self, dt):
        # must override
        pass

    def collides_with(self, other):
        distance = self.position.distance_to(other.position)
        return distance < self.radius + other.radius

    def wrap_position(self):
        surface = pygame.display.get_surface()
        if surface is None:
            width = SCREEN_WIDTH
            height = SCREEN_HEIGHT
        else:
            width, height = surface.get_size()

        padding = self.radius
        if self.position.x < -padding:
            self.position.x = width + padding
        elif self.position.x > width + padding:
            self.position.x = -padding

        if self.position.y < -padding:
            self.position.y = height + padding
        elif self.position.y > height + padding:
            self.position.y = -padding
