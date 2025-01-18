import pygame
from quatro.graphics.background import draw_background_from_asset
from quatro.graphics.animation.bunny import Bunny
from quatro.system.quit import handle_quit
from quatro.engine.maths import clip
from quatro.engine.pinhole_camera import Camera
import random


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
        randomness_amplitude=0.1,
        element_type=None,
    ):
        self.z_source = z_source
        self.x_source = x_source
        self.randomness_amplitude = randomness_amplitude
        self.planks = [
            element_type(
                z=z_source - (i / num_planks) * z_source,
                intensity=0.5 + random.uniform(0.0, 0.5),
                x=self.x_source
                + random.uniform(-self.randomness_amplitude, self.randomness_amplitude),
                z_size=z_source / num_planks,
            )
            for i in range(num_planks)
        ]

    def move_planks(self, dt: float = 0.1):
        global camera
        for plank in self.planks:
            plank.z -= dt
            if plank.out_of_screen():
                plank.z = self.z_source
                plank.x = self.x_source + random.uniform(
                    -self.randomness_amplitude, self.randomness_amplitude
                )
                self.intensity = 0.5 + random.uniform(0.0, 0.5)

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
    ):
        self.x = x
        self.y = y
        self.z = z
        self.color = [_color * intensity for _color in color]
        self.z_size = z_size
        self.xy_size = xy_size
        self.back = self.z + self.z_size / 2
        self.front = self.z - self.z_size / 2

    def out_of_screen(self):
        _, min_distance = camera.get_min_distance(pygame.Vector3(0.0, self.y, 0.0))
        if self.back <= min_distance:
            return True

    def get_coordinates(self):
        raise NotImplementedError

    def draw(
        self,
        screen: pygame.Surface,
    ):
        global camera
        # 3D plank coordinates
        _, min_distance = camera.get_min_distance(pygame.Vector3(0.0, self.y, 0.0))
        self.back = clip(self.z + self.z_size / 2, min_distance, None)
        self.front = clip(self.z - self.z_size / 2, min_distance, None)

        pts_3d = self.get_coordinates()

        # Visibility check
        if all([pt_3d.z >= 0 for pt_3d in pts_3d]):
            points = [camera.project(pt_3d) for pt_3d in pts_3d]
            pygame.draw.polygon(screen, self.color, points)


class Floor(WallElement):
    def get_coordinates(self):
        left = self.x - self.xy_size / 2
        right = self.x + self.xy_size / 2

        tl = pygame.Vector3(left, self.y, self.back)
        tr = pygame.Vector3(right, self.y, self.back)
        br = pygame.Vector3(right, self.y, self.front)
        bl = pygame.Vector3(left, self.y, self.front)
        # 2D screen coordinates
        pts_3d = [tl, tr, br, bl]
        return pts_3d


class Wall(WallElement):
    def get_coordinates(self):
        down = self.y
        up = self.y + self.xy_size
        tl = pygame.Vector3(self.x, down, self.back)
        tr = pygame.Vector3(self.x, up, self.back)
        br = pygame.Vector3(self.x, up, self.front)
        bl = pygame.Vector3(self.x, down, self.front)
        pts_3d = [tl, tr, br, bl]
        return pts_3d


def launch_running_bunny():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    w, h = screen.get_width(), screen.get_height()
    global camera
    camera = Camera(x=0, y=2.0, z=0, focal_length=100.0, w=w, h=h)
    clock = pygame.time.Clock()
    running = True
    dt = 0
    sandtrack = MovingTrack(num_planks=70, z_source=10.0, element_type=Floor)
    sidewalls_left = MovingTrack(
        num_planks=100,
        z_source=10.0,
        x_source=-3.5,
        randomness_amplitude=0,
        element_type=Wall,
    )
    sidewalls_right = MovingTrack(
        num_planks=100,
        z_source=10.0,
        x_source=3.5,
        randomness_amplitude=0,
        element_type=Wall,
    )
    moving_tracks = [sandtrack, sidewalls_left, sidewalls_right]
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
        player.draw(screen, dt=dt)

        # Draw black holes
        hole = Hole(600, 650)  # looks like  a shadow
        hole.x = player.x
        hole.draw(screen)
        # Game control update logic
        if keys[pygame.K_LEFT]:
            player.x -= 100 * dt

        if keys[pygame.K_RIGHT]:
            player.x += 100 * dt
        pygame.display.flip()

        dt = clock.tick(60) / 1000

    pygame.quit()
