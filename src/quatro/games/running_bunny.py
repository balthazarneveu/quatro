import pygame
from quatro.graphics.background import draw_background_from_asset
from quatro.graphics.animation.bunny import Bunny
from quatro.system.quit import handle_quit
from quatro.engine.maths import clip
from quatro.engine.pinhole_camera import Camera
import random
import math
from collections import deque


class Hole:
    def __init__(self, x, y, z=0):
        self.x = x
        self.y = y
        self.width = 80

    def draw(self, screen):
        pygame.draw.ellipse(
            screen, (0, 0, 0), (self.x - self.width / 2, self.y, self.width, 40)
        )


camera = None


class MovingTrack:
    def __init__(
        self,
        num_planks=10,
        x_source=0.0,
        z_source=10.0,
        randomness_amplitude=0.0,
        element_type=None,
        **kwargs,
    ):
        self.z_source = z_source
        self.x_source = x_source
        self.randomness_amplitude = randomness_amplitude
        self.planks = deque(
            [
                element_type(
                    z=z_source - (i / num_planks) * z_source,
                    intensity=0.5 + random.uniform(0.0, 0.5),
                    x=self.x_source,
                    z_size=z_source / num_planks,
                    **kwargs,
                )
                for i in range(num_planks)
            ]  # first element is the farthest from the screen (= the back)
        )

    def move_planks(self, dt: float = 0.1):
        global camera
        for plank in self.planks:
            plank.z -= dt
        if self.planks[-1].out_of_screen():
            current_plank = self.planks.pop()
            current_plank.z = self.planks[0].z + self.z_source / len(
                self.planks
            )  # Need an extra offset to put it behind the back plank
            current_plank.x = self.x_source
            self.planks.appendleft(current_plank)

    def draw(self, screen: pygame.Surface):
        for plank in self.planks:
            plank.draw(screen)


class WallElement:
    def __init__(
        self,
        x: float = 0,  # => in the middle horizontally
        y: float = 0,  # => on the floor
        z: float = 10.0,  # => 10 units away from the screen
        z_size: float = 5.0,  # Depth of the plank
        xy_size: float = 5.0,
        color=(139, 69, 19),
        intensity: float = 1.0,
        angle=0.0,
    ):
        self.x = x
        self.y = y
        self.z = z
        self.color = [_color * intensity for _color in color]
        self.z_size = z_size
        self.xy_size = xy_size
        self.back = self.z + self.z_size / 2
        self.front = self.z - self.z_size / 2
        self.angle = angle

    def out_of_screen(self):
        min_distance_z = self.get_min_distance()
        if self.back <= min_distance_z:
            return True

    def get_min_distance(self):
        min_distance_x, min_distance_y = camera.get_min_distance(
            pygame.Vector3(self.x, self.y, 0.0)
        )
        return min(min_distance_x, min_distance_y)

    def get_coordinates(self):
        raise NotImplementedError

    def draw(
        self,
        screen: pygame.Surface,
    ):
        global camera
        # 3D plank coordinates
        min_distance = self.get_min_distance()
        self.back = clip(self.z + self.z_size / 2, min_distance, None)
        self.front = clip(self.z - self.z_size / 2, min_distance, None)

        pts_3d = self.get_coordinates()

        # Visibility check
        if all([pt_3d.z >= 0 for pt_3d in pts_3d]):
            points = [camera.project(pt_3d) for pt_3d in pts_3d]
            if None in points:
                return
            pygame.draw.polygon(screen, self.color, points)


class Floor(WallElement):
    def get_coordinates(self):
        left = self.x - self.xy_size / 2
        right = self.x + self.xy_size / 2

        tl = pygame.Vector3(left, self.y, self.back)
        tr = pygame.Vector3(right, self.y, self.back)
        br = pygame.Vector3(right, self.y, self.front)
        bl = pygame.Vector3(left, self.y, self.front)
        pts_3d = [tl, tr, br, bl]
        return pts_3d


class Wall(WallElement):
    def get_coordinates(self):
        down = self.y
        up = self.y + math.cos(math.radians(self.angle)) * self.xy_size
        x_offset = math.sin(math.radians(self.angle)) * self.xy_size
        tl = pygame.Vector3(self.x, down, self.back)
        tr = pygame.Vector3(self.x + x_offset, up, self.back)
        br = pygame.Vector3(self.x + x_offset, up, self.front)
        bl = pygame.Vector3(self.x, down, self.front)
        pts_3d = [tl, tr, br, bl]
        return pts_3d


def launch_running_bunny(resolution=(1280, 720)):
    pygame.init()
    screen = pygame.display.set_mode(resolution)
    w, h = screen.get_width(), screen.get_height()
    global camera
    camera = Camera(x=0.0, y=2.0, z=0.0, focal_length=100.0, w=w, h=h)
    clock = pygame.time.Clock()
    running = True
    dt = 0
    TRACK_WIDTH = 5.0
    CROP_TOP = 2.0
    WHEAT_COLOR = (245, 222, 179)
    moving_tracks = [
        MovingTrack(
            num_planks=70, z_source=10.0, xy_size=TRACK_WIDTH * 2, element_type=Floor
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
