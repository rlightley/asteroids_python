from circleshape import CircleShape
import pygame


class Shot(CircleShape):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius)
        self.color = color
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius)

    def update(self, dt):
        self.position += self.velocity * dt

class RocketShot(Shot):
    def __init__(self, x, y, radius, color):
        super().__init__(x, y, radius, color)
        self.color = color

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.position, self.radius)
    def update(self, dt):
        self.position += self.velocity * dt
