from circleshape import CircleShape
from constants import PLAYER_RADIUS
from constants import PLAYER_CANOPY_COLOR
from constants import PLAYER_COLOR
from constants import PLAYER_PANEL_COLOR
from constants import PLAYER_RESPAWN_INVULNERABILITY_SECONDS
from constants import PLAYER_STARTING_PULSES
from constants import PLAYER_STARTING_ROCKETS
from constants import PLAYER_THRUST_CORE_COLOR
from constants import PLAYER_THRUST_COLOR
from constants import PLAYER_TURN_SPEED
from constants import PLAYER_SPEED
from constants import PLAYER_SHOOT_SPEED
from constants import PLAYER_INVULNERABLE_COLOR
from constants import SHOT_RADIUS
from constants import SHOT_COLOR
from constants import PLAYER_SHOOT_COOLDOWN_SECONDS
from constants import ROCKET_COLOR
from pulse import PulseWave
from shot import Shot
from shot import RocketShot
import pygame


def _draw_glow_polygon(screen, color, points, padding):
    min_x = min(point.x for point in points) - padding
    max_x = max(point.x for point in points) + padding
    min_y = min(point.y for point in points) - padding
    max_y = max(point.y for point in points) + padding
    glow_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    glow_surface = pygame.Surface((max(1, int(glow_rect.width)), max(1, int(glow_rect.height))), pygame.SRCALPHA)
    translated_points = [pygame.Vector2(point.x - glow_rect.x, point.y - glow_rect.y) for point in points]
    pygame.draw.polygon(glow_surface, (*color, 40), translated_points, width=8)
    pygame.draw.polygon(glow_surface, (*color, 18), translated_points, width=14)
    screen.blit(glow_surface, glow_rect.topleft)

class Player(CircleShape):
    def __init__(self, x, y, cooldown, number_of_rockets):
        super().__init__(x, y, PLAYER_RADIUS)
        self.cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS 
        self.rotation = 0
        self.number_of_rockets = number_of_rockets
        self.number_of_pulses = PLAYER_STARTING_PULSES
        self.invulnerable_timer = PLAYER_RESPAWN_INVULNERABILITY_SECONDS

    def draw(self, screen):
        color = PLAYER_COLOR
        if self.invulnerable_timer > 0:
            color = PLAYER_INVULNERABLE_COLOR

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            flame_outer, flame_inner = self.thrust_flame()
            _draw_glow_polygon(screen, PLAYER_THRUST_COLOR, flame_outer, 18)
            pygame.draw.polygon(screen, PLAYER_THRUST_COLOR, flame_outer, width=0)
            pygame.draw.polygon(screen, PLAYER_THRUST_CORE_COLOR, flame_inner, width=0)

        hull = self.triangle()
        _draw_glow_polygon(screen, color, hull, 14)
        pygame.draw.polygon(screen, color, hull, width=3)
        pygame.draw.polygon(screen, PLAYER_PANEL_COLOR, self.inner_hull(), width=2)
        pygame.draw.polygon(screen, PLAYER_CANOPY_COLOR, self.canopy(), width=0)
        pygame.draw.line(screen, PLAYER_PANEL_COLOR, hull[1], hull[0], width=2)
        pygame.draw.line(screen, PLAYER_PANEL_COLOR, hull[2], hull[0], width=2)

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]

    def inner_hull(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90)
        nose = self.position + forward * (self.radius * 0.58)
        left = self.position - forward * (self.radius * 0.38) - right * (self.radius * 0.46)
        tail = self.position - forward * (self.radius * 0.72)
        rgt = self.position - forward * (self.radius * 0.38) + right * (self.radius * 0.46)
        return [nose, left, tail, rgt]

    def canopy(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90)
        nose = self.position + forward * (self.radius * 0.28)
        left = self.position - forward * (self.radius * 0.02) - right * (self.radius * 0.24)
        tail = self.position - forward * (self.radius * 0.26)
        rgt = self.position - forward * (self.radius * 0.02) + right * (self.radius * 0.24)
        return [nose, left, tail, rgt]

    def thrust_flame(self):
        backward = pygame.Vector2(0, -1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90)
        base = self.position + backward * (self.radius * 0.7)
        tip = self.position + backward * (self.radius * 1.9)
        left = base - right * (self.radius * 0.4)
        rgt = base + right * (self.radius * 0.4)
        inner_base = self.position + backward * (self.radius * 0.88)
        inner_tip = self.position + backward * (self.radius * 1.45)
        inner_left = inner_base - right * (self.radius * 0.18)
        inner_rgt = inner_base + right * (self.radius * 0.18)
        return [left, tip, rgt], [inner_left, inner_tip, inner_rgt]

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
        self.invulnerable_timer = max(0, self.invulnerable_timer - dt)
        self.wrap_position()

    def move(self, dt):
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
        self.position += rotated_with_speed_vector


    def shoot_rocket(self):
        if self.cooldown > 0 or self.number_of_rockets <= 0:
            return None
        self.cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
        shot = RocketShot(0, 0, 15, ROCKET_COLOR)
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
        shot = Shot(0, 0, SHOT_RADIUS, SHOT_COLOR)
        unit_vector = pygame.Vector2(0, 1)
        rotated_vector = unit_vector.rotate(self.rotation)
        shot_velocity = rotated_vector * PLAYER_SHOOT_SPEED
        shot.velocity = shot_velocity
        shot_position = self.position + rotated_vector * self.radius
        shot.position = shot_position
        return shot

    def fire_pulse(self):
        if self.number_of_pulses <= 0:
            return None
        pulse = PulseWave(self.position.x, self.position.y)
        self.number_of_pulses -= 1
        return pulse

    def reset(self, x, y):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0, 0)
        self.rotation = 0
        self.cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
        self.invulnerable_timer = PLAYER_RESPAWN_INVULNERABILITY_SECONDS

    def add_rockets(self, amount):
        self.number_of_rockets += amount

    def add_pulses(self, amount):
        self.number_of_pulses += amount

    def replenish_rockets(self):
        self.number_of_rockets = max(self.number_of_rockets, PLAYER_STARTING_ROCKETS)
