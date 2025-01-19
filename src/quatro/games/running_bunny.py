import pygame
from quatro.graphics.background import draw_background_from_asset
from quatro.graphics.animation.bunny import Bunny
from quatro.system.quit import handle_quit
from quatro.engine.planes import Floor, Wall
from quatro.engine.endless_track import MovingTrack
from quatro.engine.pinhole_camera import Camera


class Hole:
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.width = 80

    def draw(self, screen):
        pygame.draw.ellipse(
            screen, (0, 0, 0), (self.x - self.width / 2, self.y, self.width, 40)
        )


def launch_running_bunny(resolution=(1280, 720)):
    pygame.init()
    screen = pygame.display.set_mode(resolution)
    w, h = screen.get_width(), screen.get_height()
    camera = Camera(x=0.0, y=2.0, z=0.0, focal_length=100.0, w=w, h=h)
    clock = pygame.time.Clock()
    running = True
    dt = 0
    TRACK_WIDTH = 5.0
    CROP_TOP = 2.0
    WHEAT_COLOR = (245, 222, 179)
    moving_tracks = [
        MovingTrack(
            num_planks=70,
            z_source=10.0,
            xy_size=TRACK_WIDTH * 2,
            element_type=Floor,
            camera=camera,
        )
    ]

    for sign in [-1, 1]:
        moving_tracks.append(
            MovingTrack(
                num_planks=70,
                z_source=10.0,
                x_source=sign * TRACK_WIDTH,
                randomness_amplitude=0,
                element_type=Wall,
                angle=sign * 5.0,
                xy_size=CROP_TOP,
                color=WHEAT_COLOR,
                camera=camera,
            )
        )
    for sign in [-1, 1]:
        CROP_TOP_SIZE = 200.0
        moving_tracks.append(
            MovingTrack(
                num_planks=50,
                y=CROP_TOP,
                z_source=10.0,
                x_source=sign * (TRACK_WIDTH + CROP_TOP_SIZE / 2),
                xy_size=CROP_TOP_SIZE,
                element_type=Floor,
                color=WHEAT_COLOR,
                camera=camera,
            )
        )
    player_pos = pygame.Vector2(w / 2, 3 * h / 4)
    player = Bunny(*player_pos, size=50, animation_speed=10)
    current_background = "night_wheat_field"
    while running:
        keys = pygame.key.get_pressed()
        running = handle_quit(keys)
        draw_background_from_asset(screen, current_background)
        for moving_track in moving_tracks:
            moving_track.move_planks(dt=dt)
            moving_track.draw(screen)

        # Draw black holes
        hole = Hole(player.x, player.y + player.size * 1.8)  # looks like  a shadow
        hole.x = player.x
        hole.draw(screen)
        player.draw(screen, dt=dt)

        # Game control update logic
        if keys[pygame.K_LEFT]:
            player.x -= 100 * dt

        if keys[pygame.K_RIGHT]:
            player.x += 100 * dt

        if keys[pygame.K_UP]:
            camera.camera_position.y += 1.0 * dt
        if keys[pygame.K_DOWN]:
            camera.camera_position.y -= 1.0 * dt

        pygame.display.flip()

        dt = clock.tick(60) / 1000

    pygame.quit()
