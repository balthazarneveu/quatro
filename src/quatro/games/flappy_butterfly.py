import pygame
from quatro.graphics.background import draw_background_from_asset
from quatro.graphics.animation.butterfly import Butterfly
from quatro.control.control import ControlledPlayer
import numpy as np


def update_physics_model(player: ControlledPlayer, trigger_jump=False, dt=0):
    if trigger_jump:
        player.velocity = player.velocity - 0.01 * 30 * 3 * 1000
    if player.y > 0:
        player.velocity = player.velocity + 0.01 / 10.0 * 2 * 1000
    player.velocity = np.clip(player.velocity, -0.2*1000, None)  # keep within bounds
    player.y += player.velocity * dt


def launch_flappy_butterfly():
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    dt = 0
    player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    player = Butterfly(*player_pos, size=30, color="red", flap_speed=10)
    current_background = "sunset_field"
    while running:
        # check for events and key presses to stop the application
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
            running = False

        # fill the screen with an image

        draw_background_from_asset(screen, current_background)

        # draw a circle on the screen
        player.draw(screen, dt=dt)

        # Game control update logic
        if keys[pygame.K_LEFT]:
            player.x -= 100 * dt
        if keys[pygame.K_RIGHT]:
            player.x += 100 * dt

        update_physics_model(player, keys[pygame.K_SPACE], dt=dt)
        player.flap_speed = abs(max(-5, -player.velocity / 10))
        if player.y < 0:
            player.y = screen.get_height() - 30
            current_background = "sunset_field_large"
        if player.y > screen.get_height():
            player.y = 30
            current_background = "sunset_field"

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000

    pygame.quit()
