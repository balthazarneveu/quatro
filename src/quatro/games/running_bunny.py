import pygame
from quatro.graphics.background import draw_background_from_asset
from quatro.graphics.animation.bunny import Bunny
from quatro.system.quit import handle_quit


def launch_running_bunny():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    dt = 0
    w, h = screen.get_width(), screen.get_height()
    player_pos = pygame.Vector2(w / 2, 3 * h / 4)
    player = Bunny(*player_pos, size=50, animation_speed=10)
    current_background = "night_wheat_field"
    while running:
        keys = pygame.key.get_pressed()
        running = handle_quit(keys)
        draw_background_from_asset(screen, current_background)
        player.draw(screen, dt=dt)
        # Game control update logic
        if keys[pygame.K_LEFT]:
            player.x -= 100 * dt
        if keys[pygame.K_RIGHT]:
            player.x += 100 * dt

        pygame.display.flip()

        dt = clock.tick(60) / 1000

    pygame.quit()
