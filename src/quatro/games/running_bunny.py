import pygame
from quatro.graphics.background import draw_background_from_asset
from quatro.graphics.animation.bunny import Bunny
from quatro.system.quit import handle_quit
from quatro.system.window import init_screen
from quatro.engine.planes import Floor, Wall, FacingWall
from quatro.engine.endless_track import MovingTrack, MovingElement
from quatro.engine.pinhole_camera import Camera
from math import sin, radians


class Hole:
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.width = 80

    def draw(self, screen):
        pygame.draw.ellipse(
            screen, (0, 0, 0), (self.x - self.width / 2, self.y, self.width, 40)
        )


class Carrot(FacingWall):
    def get_coordinates(self):
        pts_3d = super().get_coordinates()
        top = (pts_3d[0] + pts_3d[1]) / 2.0
        br, bl = pts_3d[2], pts_3d[3]
        pts_3d_triangle = pts_3d[:2] + [(br + bl) / 2.0]
        geometry = [
            {
                "type": "poly",
                "content": pts_3d_triangle,
            }
        ]
        for angle in [-20, 20]:
            leaf_size = self.xy_size[1] * 0.7
            leaf = {
                "type": "ellipse",
                "content": {
                    "color": (0, 100, 0),  # dark green color
                    "center": top
                    + pygame.Vector3(
                        sin(radians(-angle)) * leaf_size / 2.0, leaf_size / 2.0, 0
                    ),
                    "size_x": leaf_size * 0.2,
                    "size_y": leaf_size,
                    "angle": angle,
                    "width": 0,
                },
            }
            geometry.append(leaf)
        return geometry

    def collide(self, player_bounding_box: pygame.Rect, screen: pygame.Surface = None):
        if screen:
            if self.visible:
                pygame.draw.rect(screen, (255, 0, 0), self.bounding_box, 2)
            pygame.draw.rect(screen, (0, 255, 0), player_bounding_box, 2)
        collision = self.bounding_box.colliderect(player_bounding_box)
        if not self.visible:
            collision = False
        if collision:
            self.visible = False
        return collision


def launch_running_bunny(resolution=None):
    screen = init_screen(resolution)
    w, h = screen.get_width(), screen.get_height()
    f_factor = 10.0
    camera = Camera(
        x=0.0,
        y=4.0 * f_factor,
        z=0.0,
        focal_length=100.0 * f_factor,
        w=w,
        h=h,
        pitch=-18.0,
    )
    clock = pygame.time.Clock()
    running = True
    dt = 0
    speed = 1.0 * f_factor
    TRACK_WIDTH = 3.0 * f_factor
    CROP_TOP = 2.0 * f_factor
    Z_SOURCE = 30.0 * f_factor
    WHEAT_COLOR = (245, 222, 179)
    score = 0
    moving_tracks = [
        MovingTrack(
            speed=speed,
            num_elements=50,
            z_source=Z_SOURCE * 1.5,
            xy_size=TRACK_WIDTH * 2,
            element_type=Floor,
            camera=camera,
        )
    ]
    moving_elements = []

    for sign in [-1, 1]:
        moving_tracks.append(
            MovingTrack(
                speed=speed,
                num_elements=70,
                z_source=Z_SOURCE,
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
                speed=speed,
                num_elements=50,
                y=CROP_TOP,
                z_source=Z_SOURCE,
                x_source=sign * (TRACK_WIDTH + CROP_TOP_SIZE / 2),
                xy_size=CROP_TOP_SIZE,
                element_type=Floor,
                color=WHEAT_COLOR,
                camera=camera,
            )
        )

    moving_elements.append(
        MovingElement(
            speed=speed,
            num_elements=10,
            y=0.0 * CROP_TOP,
            z_source=Z_SOURCE,
            x_range=[-TRACK_WIDTH * 0.6, TRACK_WIDTH * 0.6],
            xy_size=[0.1 * TRACK_WIDTH, 0.3 * CROP_TOP],
            z_size=0.0,
            element_type=Carrot,
            color=(255, 165, 0),  # orange color
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
        for moving_track in moving_tracks + moving_elements:
            moving_track.move(dt=dt)
            moving_track.draw(screen)
        for reward_elements in moving_elements:
            for reward_element in reward_elements.elements:
                if reward_element.collide(player.bounding_box, screen=None):
                    score += 1
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
            camera.camera_position.y += 1.0 * f_factor * dt
        if keys[pygame.K_DOWN]:
            camera.camera_position.y -= 1.0 * f_factor * dt
        if keys[pygame.K_PAGEDOWN]:
            camera.pitch += 20.0 * dt
        if keys[pygame.K_PAGEUP]:
            camera.pitch -= 20.0 * dt

        pygame.display.flip()

        dt = clock.tick(60) / 1000

    pygame.quit()
