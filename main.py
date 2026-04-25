import pygame
import random
from constants import BACKGROUND_BOTTOM
from constants import BACKGROUND_TOP
from constants import FPS
from constants import HUD_ACCENT
from constants import HUD_PANEL
from constants import NEBULA_COLOR_A
from constants import NEBULA_COLOR_B
from constants import PLANET_GLOW_COLOR
from constants import PLAYER_STARTING_LIVES
from constants import PLAYER_STARTING_PULSES
from constants import PLAYER_STARTING_ROCKETS
from constants import PULSE_PICKUP_AMOUNT
from constants import PULSE_PICKUP_CHANCE
from constants import ROCKET_PICKUP_AMOUNT
from constants import ROCKET_PICKUP_CHANCE
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from constants import STAR_COUNT
from constants import STAR_TWINKLE_SPEED_MAX
from constants import STAR_TWINKLE_SPEED_MIN
from constants import TEXT_PRIMARY
from constants import TEXT_SECONDARY
from constants import WAVE_CLEAR_DELAY_SECONDS
from logger import log_state
from logger import log_event
from player import Player
from pulse import PulseWave
from asteroidfield import AsteroidField
from asteroid import Asteroid
from pickup import PulsePickup
from pickup import RocketPickup
from shot import Shot
from shot import RocketShot


def create_starfield(width, height):
    stars = []
    for _ in range(STAR_COUNT):
        stars.append(
            {
                "position": pygame.Vector2(random.uniform(0, width), random.uniform(0, height)),
                "radius": random.choice((1, 1, 2)),
                "speed": random.uniform(8, 28),
                "alpha": random.randint(120, 255),
                "twinkle": random.uniform(STAR_TWINKLE_SPEED_MIN, STAR_TWINKLE_SPEED_MAX),
                "phase": random.uniform(0, 6.28),
            }
        )
    return stars


def update_starfield(stars, dt, width, height):
    for star in stars:
        star["position"].y += star["speed"] * dt
        star["phase"] += dt * star["twinkle"]
        if star["position"].y > height:
            star["position"].y = 0
            star["position"].x = random.uniform(0, width)


def draw_background(screen, stars):
    width, height = screen.get_size()
    for y in range(height):
        blend = y / max(1, height - 1)
        color = (
            int(BACKGROUND_TOP[0] + (BACKGROUND_BOTTOM[0] - BACKGROUND_TOP[0]) * blend),
            int(BACKGROUND_TOP[1] + (BACKGROUND_BOTTOM[1] - BACKGROUND_TOP[1]) * blend),
            int(BACKGROUND_TOP[2] + (BACKGROUND_BOTTOM[2] - BACKGROUND_TOP[2]) * blend),
        )
        pygame.draw.line(screen, color, (0, y), (width, y))

    nebula_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.circle(nebula_surface, (*NEBULA_COLOR_A, 36), (int(width * 0.2), int(height * 0.22)), int(min(width, height) * 0.24))
    pygame.draw.circle(nebula_surface, (*NEBULA_COLOR_B, 28), (int(width * 0.76), int(height * 0.28)), int(min(width, height) * 0.2))
    pygame.draw.circle(nebula_surface, (*PLANET_GLOW_COLOR, 55), (int(width * 0.84), int(height * 0.16)), int(min(width, height) * 0.09))
    pygame.draw.circle(nebula_surface, (18, 34, 58, 220), (int(width * 0.84), int(height * 0.16)), int(min(width, height) * 0.055))
    screen.blit(nebula_surface, (0, 0))

    for star in stars:
        brightness = int(star["alpha"] * (0.72 + 0.28 * (1 + pygame.math.Vector2(1, 0).rotate_rad(star["phase"]).x) / 2))
        pygame.draw.circle(screen, (brightness, brightness, brightness), star["position"], star["radius"])


def draw_hud(screen, font, small_font, score, lives, wave, rockets, pulses, paused):
    status_text = f"Score {score}    Lives {lives}    Wave {wave}    Rockets {rockets}    Pulse {pulses}"
    controls_text = "WASD move   Space fire   N rocket   B pulse   P pause"
    pause_label = "PAUSED" if paused else "P PAUSE"

    status_surface = font.render(status_text, True, TEXT_PRIMARY)
    controls_surface = small_font.render(controls_text, True, TEXT_SECONDARY)
    pause_surface = small_font.render(pause_label, True, TEXT_PRIMARY)

    content_width = max(status_surface.get_width(), controls_surface.get_width()) + 32
    pause_width = pause_surface.get_width() + 28
    panel_width = min(screen.get_width() - 32, max(560, content_width + pause_width + 12))
    panel_rect = pygame.Rect(16, 16, panel_width, 96)
    shadow_rect = panel_rect.move(0, 6)
    shadow_surface = pygame.Surface(shadow_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 85), shadow_surface.get_rect(), border_radius=18)
    screen.blit(shadow_surface, shadow_rect.topleft)

    panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, (*HUD_PANEL, 228), panel_surface.get_rect(), border_radius=18)
    pygame.draw.rect(panel_surface, (*HUD_ACCENT, 90), panel_surface.get_rect(), width=2, border_radius=18)
    screen.blit(panel_surface, panel_rect.topleft)

    title_surface = small_font.render("MISSION STATUS", True, TEXT_SECONDARY)
    screen.blit(title_surface, (panel_rect.x + 16, panel_rect.y + 10))

    screen.blit(status_surface, (panel_rect.x + 16, panel_rect.y + 34))

    screen.blit(controls_surface, (panel_rect.x + 16, panel_rect.bottom - 24))

    pause_color = (255, 220, 120) if paused else HUD_ACCENT
    pause_box = pygame.Rect(panel_rect.right - pause_surface.get_width() - 24, panel_rect.y + 10, pause_surface.get_width() + 12, 24)
    pygame.draw.rect(screen, (14, 22, 36), pause_box, border_radius=10)
    pygame.draw.rect(screen, pause_color, pause_box, width=2, border_radius=10)
    screen.blit(pause_surface, (pause_box.x + 6, pause_box.y + 4))

    if paused:
        paused_surface = pygame.Surface((290, 44), pygame.SRCALPHA)
        pygame.draw.rect(paused_surface, (28, 22, 10, 220), paused_surface.get_rect(), border_radius=14)
        pygame.draw.rect(paused_surface, (255, 220, 120, 180), paused_surface.get_rect(), width=2, border_radius=14)
        paused_text = small_font.render("Paused  |  Press P to resume", True, (255, 234, 178))
        paused_surface.blit(paused_text, (18, 12))
        paused_rect = paused_surface.get_rect(center=(screen.get_width() / 2, 42))
        screen.blit(paused_surface, paused_rect)


def draw_center_message(screen, font, title, subtitle):
    title_surface = font.render(title, True, TEXT_PRIMARY)
    subtitle_surface = font.render(subtitle, True, TEXT_SECONDARY)
    title_rect = title_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 - 20))
    subtitle_rect = subtitle_surface.get_rect(center=(screen.get_width() / 2, screen.get_height() / 2 + 20))
    screen.blit(title_surface, title_rect)
    screen.blit(subtitle_surface, subtitle_rect)


def reset_round(player, asteroids, shots, rockets, pulses, pickups, asteroid_field, wave):
    for group in (asteroids, shots, rockets, pulses, pickups):
        for sprite in tuple(group):
            sprite.kill()

    player.reset(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    asteroid_field.spawn_timer = 0
    asteroid_field.set_level(wave)
    asteroid_field.spawn_wave(wave)

def main():
    pygame.init()
    pygame.font.init()

    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    print(f"Screen width: {SCREEN_WIDTH}")

    pygame.event.set_grab(True)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Asteroids+")

    dt = 0
    score = 0
    lives = PLAYER_STARTING_LIVES
    wave = 1
    paused = False
    game_over = False
    wave_clear_timer = 0.0
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    number_of_rockets = PLAYER_STARTING_ROCKETS
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    rockets = pygame.sprite.Group()
    pulses = pygame.sprite.Group()
    pickups = pygame.sprite.Group()
    stars = create_starfield(SCREEN_WIDTH, SCREEN_HEIGHT)
    Player.containers = (drawable, updatable)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, dt, number_of_rockets)

    Asteroid.containers = (drawable, updatable, asteroids)
    AsteroidField.containers = (updatable,)
    asteroid_field = AsteroidField()
    asteroid_field.set_level(wave)

    Shot.containers = (drawable, updatable, shots)
    RocketShot.containers = (drawable, updatable, rockets)
    PulseWave.containers = (drawable, updatable, pulses)
    RocketPickup.containers = (drawable, updatable, pickups)
    PulsePickup.containers = (drawable, updatable, pickups)
    asteroid_field.spawn_wave(wave)
    
    while True:
        dt = clock.tick(FPS) / 1000.0

        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p and not game_over:
                paused = not paused
            if event.type == pygame.KEYDOWN and event.key == pygame.K_b and not paused and not game_over:
                pulse = player.fire_pulse()
                if pulse is not None:
                    log_event("pulse_fired", wave=wave, score=score)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r and game_over:
                score = 0
                lives = PLAYER_STARTING_LIVES
                wave = 1
                paused = False
                game_over = False
                player.number_of_rockets = PLAYER_STARTING_ROCKETS
                player.number_of_pulses = PLAYER_STARTING_PULSES
                reset_round(player, asteroids, shots, rockets, pulses, pickups, asteroid_field, wave)

        if not paused and not game_over:
            update_starfield(stars, dt, screen.get_width(), screen.get_height())
            updatable.update(dt)

            for asteroid in tuple(asteroids):
                if player.invulnerable_timer <= 0 and player.collides_with(asteroid):
                    lives -= 1
                    log_event("player_hit", lives=lives, wave=wave, score=score)
                    if lives <= 0:
                        game_over = True
                        print(f"Game Over! Score: {score}")
                        break

                    reset_round(player, asteroids, shots, rockets, pulses, pickups, asteroid_field, wave)
                    break

                for shot in tuple(shots):
                    if shot.collides_with(asteroid):
                        log_event("asteroid_shot", wave=wave, score=score)
                        shot.kill()
                        if asteroid.radius > 20 and random.random() < ROCKET_PICKUP_CHANCE:
                            RocketPickup(asteroid.position.x, asteroid.position.y, ROCKET_PICKUP_AMOUNT)
                        elif asteroid.radius > 20 and random.random() < PULSE_PICKUP_CHANCE:
                            PulsePickup(asteroid.position.x, asteroid.position.y, PULSE_PICKUP_AMOUNT)
                        asteroid.split()
                        score += 2
                        break

                if not asteroid.alive():
                    continue
            
                for rocket in tuple(rockets):
                    if rocket.collides_with(asteroid):
                        log_event("asteroid_rocket", wave=wave, score=score)
                        rocket.kill()
                        if asteroid.radius > 20 and random.random() < ROCKET_PICKUP_CHANCE:
                            RocketPickup(asteroid.position.x, asteroid.position.y, ROCKET_PICKUP_AMOUNT)
                        elif asteroid.radius > 20 and random.random() < PULSE_PICKUP_CHANCE:
                            PulsePickup(asteroid.position.x, asteroid.position.y, PULSE_PICKUP_AMOUNT)
                        asteroid.kill()
                        score += 1
                        break

                if not asteroid.alive():
                    continue

                for pulse in tuple(pulses):
                    if pulse.collides_with(asteroid):
                        log_event("asteroid_pulsed", wave=wave, score=score)
                        asteroid.kill()
                        score += 3
                        break

            for pickup in tuple(pickups):
                if player.collides_with(pickup):
                    if isinstance(pickup, PulsePickup):
                        player.add_pulses(pickup.amount)
                        log_event("pulse_pickup", amount=pickup.amount, wave=wave, pulses=player.number_of_pulses)
                    else:
                        player.add_rockets(pickup.amount)
                        log_event("rocket_pickup", amount=pickup.amount, wave=wave, rockets=player.number_of_rockets)
                    pickup.kill()

            if len(asteroids) == 0:
                wave_clear_timer += dt
                if wave_clear_timer >= WAVE_CLEAR_DELAY_SECONDS:
                    wave += 1
                    player.add_rockets(1)
                    player.replenish_rockets()
                    asteroid_field.set_level(wave)
                    asteroid_field.spawn_wave(wave)
                    log_event("wave_started", wave=wave)
                    wave_clear_timer = 0.0
            else:
                wave_clear_timer = 0.0

        draw_background(screen, stars)

        for sprite in drawable:
            sprite.draw(screen)

        draw_hud(screen, font, small_font, score, lives, wave, player.number_of_rockets, player.number_of_pulses, paused)
        if game_over:
            draw_center_message(screen, font, "Game Over", "Press R to restart")

        pygame.display.flip()


if __name__ == "__main__":
    main()
