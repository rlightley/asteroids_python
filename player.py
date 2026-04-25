from circleshape import CircleShape
from constants import PLAYER_RADIUS
from constants import PLAYER_TURN_SPEED
from constants import PLAYER_SPEED
from constants import PLAYER_SHOOT_SPEED
from constants import SHOT_RADIUS
from constants import PLAYER_SHOOT_COOLDOWN_SECONDS
from shot import Shot
from shot import RocketShot
import pygame

class Player(CircleShape):
    def __init__(self, x, y, cooldown, number_of_rockets):
        super().__init__(x, y, PLAYER_RADIUS)
        self.cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS 
        self.rotation = 0
        self.number_of_rockets = number_of_rockets

    def draw(self, screen):
        pygame.draw.polygon(screen, ("white"), self.triangle(), width=2)

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt
    
    def update(self, dt):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rotate(-dt)
        if keys[pygame.K_d]:
            self.rotate(dt)
        if keys[pygame.K_w]:
            self.move(dt)
        if keys[pygame.K_s]:
            self.move(-dt)
        if keys[pygame.K_SPACE]:
            self.shoot()
        if keys[pygame.K_n]:
            self.shoot_rocket()
        self.cooldown = self.cooldown - dt

    def move(self, dt):
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector


    def shoot_rocket(self):
        if self.cooldown > 0 or self.number_of_rockets <= 0:
            return None
        self.cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = RocketShot(0, 0, 15, "red")
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        shot_velocity = rotated_vector * PLAYER_SHOOT_SPEED
        shot.velocity = shot_velocity
        shot_position = self.position + rotated_vector * self.radius
        shot.position = shot_position
        self.number_of_rockets -= 1
        return shot

    def shoot(self):
        if self.cooldown > 0:
            return None
        self.cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = Shot(0, 0, SHOT_RADIUS, "green")
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        shot_velocity = rotated_vector * PLAYER_SHOOT_SPEED
        shot.velocity = shot_velocity
        shot_position = self.position + rotated_vector * self.radius
        shot.position = shot_position
        return shot
