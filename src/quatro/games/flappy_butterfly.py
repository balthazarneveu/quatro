import pygame
# from quatro.graphics.assets.image_assets import BACKGROUNDS, PATH
from quatro.graphics.background import draw_background_from_asset


def launch_flappy_butterfly():
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True
    dt = 0

    player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
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
        pygame.draw.circle(screen, "red", player_pos, 40)

        # Game control update logic
        if keys[pygame.K_UP]:
            player_pos.y -= 300 * dt
        if keys[pygame.K_DOWN]:
            player_pos.y += 300 * dt
        if keys[pygame.K_LEFT]:
            player_pos.x -= 300 * dt
        if keys[pygame.K_RIGHT]:
            player_pos.x += 300 * dt

        if player_pos.y < 0:
            player_pos.y = screen.get_height() - 30
            current_background = "sunset_field_large"
        if player_pos.y > screen.get_height():
            player_pos.y = 30
            current_background = "sunset_field"

        # flip() the display to put your work on screen
        pygame.display.flip()

        # limits FPS to 60
        # dt is delta time in seconds since last frame, used for framerate-
        # independent physics.
        dt = clock.tick(60) / 1000

    pygame.quit()
