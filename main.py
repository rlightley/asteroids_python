import pygame
import sys
from constants import SCREEN_WIDTH
from constants import SCREEN_HEIGHT
from logger import log_state
from logger import log_event
from player import Player
from asteroidfield import AsteroidField
from asteroid import Asteroid
from shot import Shot


def main():
    print("Starting Asteroids with pygame version: VERSION")
    print(f"Screen height: {SCREEN_HEIGHT}")
    print(f"Screen width: {SCREEN_WIDTH}")

    pygame.init()
    pygame.event.set_grab(True)
    clock = pygame.time.Clock()
    dt = 0
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)


    updatable = pygame.sprite.Group() 
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Player.containers = (drawable, updatable) 
    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, dt)

    Asteroid.containers = (drawable, updatable, asteroids)
    AsteroidField.containers = (updatable)
    asteroid_field = AsteroidField()

    Shot.containers = (drawable, updatable, shots)

    while True:
        log_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            

        screen.fill((0, 0, 0))
        for sprite in drawable:
            sprite.draw(screen)
        pygame.display.flip()
        clock.tick(60)
        dt = clock.get_time() / 1000.0

        updatable.update(dt)
        for asteroid in asteroids:
            if player.collides_with(asteroid):
                log_event("player_hit")
                print("Game Over!")
                sys.exit()
                return
        for shot in shots:
            for asteroid in asteroids:
                if shot.collides_with(asteroid):
                    log_event("asteroid_shot")
                    shot.kill()
                    asteroid.split()

if __name__ == "__main__":
    main()
