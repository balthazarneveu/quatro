import pygame
from quatro.graphics.background import draw_background_from_asset
from quatro.graphics.animation.butterfly import Butterfly
from quatro.control.control import ControlledPlayer
from quatro.graphics.animation.wheat import Wheat
from quatro.system.quit import handle_quit
from quatro.system.window import init_screen
import random
import numpy as np


def update_physics_model(player: ControlledPlayer, trigger_jump=False, dt=0):
    if trigger_jump:
        player.velocity = player.velocity - 0.01 * 30 * 3 * 1000
    if player.y > 0:
        player.velocity = player.velocity + 0.01 / 10.0 * 2 * 1000
    player.velocity = np.clip(player.velocity, -0.2 * 1000, None)  # keep within bounds
    player.y += player.velocity * dt


def launch_flappy_butterfly(
    resolution=(1280, 720), debug: bool = False, audio: bool = True
) -> dict:
    context = {}
    # pygame setup
    screen = init_screen(resolution)
    clock = pygame.time.Clock()
    running = True
    pause = False
    dt = 0
    w, h = screen.get_width(), screen.get_height()
    player_pos = pygame.Vector2(w / 2, h / 2)
    player = Butterfly(*player_pos, size=80, color="orange", flap_speed=10)
    current_background = "sunset_field"
    wheat_stalks = [
        Wheat(
            w // 2
            + (random.randint(0, 1) - 0.5) * 2 * (w // 8 + random.randint(0, w // 2)),
            h + random.randint(-50, 50),
            height=h / 10,
            color=(
                245 + random.randint(-20, 10),
                222 + random.randint(-5, 5),
                179 + random.randint(-5, 5),
            ),
        )
        for _ in range(500)
    ]

    while running:
        keys = pygame.key.get_pressed()
        running = handle_quit(keys, context)
        # fill the screen with an image

        draw_background_from_asset(screen, current_background)

        # draw a circle on the screen
        for wheat in wheat_stalks:
            wheat.x = (wheat.x - w // 2) * 1.005 + w // 2
            if wheat.x < 0 or wheat.x > w:
                wheat.x = (
                    w // 2
                    + (random.randint(0, 1) - 0.5) * 2 * w // 8
                    + random.randint(-w // 16, w // 16)
                )
                wheat.height = 2 * h / 3

            # wheat.height += 0.1
            WHEAT_MID_HEIGHT = h * 0.40
            wheat.height = WHEAT_MID_HEIGHT + abs(wheat.x - w // 2) / (w / 2) * (
                WHEAT_MID_HEIGHT - 1
            )
            wheat.draw(screen, dt)
        player.draw(screen, dt=dt)

        # Game control update logic
        if keys[pygame.K_LEFT]:
            player.x -= 100 * dt
        if keys[pygame.K_RIGHT]:
            player.x += 100 * dt
        if keys[pygame.K_p]:
            pause = not pause
        player.toggle_pause(pause)
        if not pause:
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
    return context
