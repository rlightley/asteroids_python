import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from logger import log_state
from logger import log_event
from player import Player
from asteroidfield import AsteroidField
from asteroid import Asteroid
from shot import Shot
from shot import RocketShot

def main():
    pygame.init()
    pygame.font.init()

    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    print(f"Screen width: {SCREEN_WIDTH}")

    pygame.event.set_grab(True)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)

    dt = 0
    score = 0
    font = pygame.font.SysFont(None, 36)
    number_of_rockets = 50
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    rockets = pygame.sprite.Group()
    Player.containers = (drawable, updatable)
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, dt, number_of_rockets)

    Asteroid.containers = (drawable, updatable, asteroids)
    AsteroidField.containers = (updatable,)
    asteroid_field = AsteroidField()

    Shot.containers = (drawable, updatable, shots)
    RocketShot.containers = (drawable, updatable, rockets)
    
    while True:
        dt = clock.tick(60) / 1000.0

        log_state()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        updatable.update(dt)

        for asteroid in asteroids:
            if player.collides_with(asteroid):
                log_event("player_hit")
                print(f"Game Over! Score: {score}")
                return

            for shot in shots:
                if shot.collides_with(asteroid):
                    log_event("asteroid_shot")
                    shot.kill()
                    asteroid.split()
                    score += 2
                    break
            
            for rocket in rockets:
                if rocket.collides_with(asteroid):
                    log_event("asteroid_rocket")
                    rocket.kill()
                    asteroid.kill()
                    score += 1
                    break

        screen.fill((0, 0, 0))

        for sprite in drawable:
            sprite.draw(screen)

        score_surface = font.render(f"Score: {score} Rockets: {player.number_of_rockets}", True, (255, 255, 255))
        screen.blit(score_surface, (20, 20))

        pygame.display.flip()


if __name__ == "__main__":
    main()
