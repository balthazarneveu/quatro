import pygame
from quatro.graphics.background import draw_background_from_asset
from quatro.graphics.animation.bunny import Bunny
from quatro.system.quit import handle_quit
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


class Camera:
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        focal_length: float = 1.0,
        w: float = 1280,
        h: float = 720,
        min_distance=0.2,
    ):
        self.camera_position = pygame.Vector3(x, y, z)
        self.focal_length = focal_length
        self.screen_center = pygame.Vector2(w / 2, h / 2)
        self.w = w
        self.h = h
        self.min_distance = min_distance

    def project(self, point: pygame.Vector3) -> pygame.Vector2:
        relative_point = point - self.camera_position
        out = (
            self.focal_length
            * pygame.Vector2(
                relative_point.x / relative_point.z,
                -relative_point.y / relative_point.z,
            )
            + self.screen_center
        )
        out.x = clip(out.x, 0, self.w)
        out.y = clip(out.y, 0, self.h)
        return out

    def get_min_distance(self, point: pygame.Vector3) -> pygame.Vector2:
        relative_point = point - self.camera_position
        min_dist_x_clip = relative_point.x * self.focal_length / (self.w / 2)
        min_dist_y_clip = relative_point.y * self.focal_length / (self.h / 2)
        return abs(min_dist_x_clip), abs(min_dist_y_clip)


camera = None


def clip(value, min_value, max_value):
    if min_value is None:
        return min(value, max_value)
    if max_value is None:
        return max(value, min_value)
    return min(max(value, min_value), max_value)


class SandTrack:
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
                # intensity=0.5 + i / num_planks,
                intensity=0.5 + random.uniform(0.0, 0.5),
                x=self.x_source
                + random.uniform(-self.randomness_amplitude, self.randomness_amplitude),
                plank_depth=z_source / num_planks,
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


class Plank:
    def __init__(
        self,
        x: float = 0,  # => in the middle horizontally
        y: float = 0,  # => on the floor
        z: float = 10.0,  # => 10 units away from the screen
        plank_depth: float = 5.0,
        plank_width: float = 5.0,
        color=(139, 69, 19),
        intensity: float = 1.0,
    ):
        self.x = x
        self.y = y
        self.z = z
        self.color = [_color * intensity for _color in color]
        self.plank_depth = plank_depth
        self.plank_width = plank_width
        self.top = self.z + self.plank_depth / 2

    def out_of_screen(self):
        _, min_distance = camera.get_min_distance(pygame.Vector3(0.0, self.y, 0.0))
        if self.top <= min_distance:
            return True

    def draw(
        self,
        screen: pygame.Surface,
    ):
        global camera
        # 3D plank coordinates
        left = self.x - self.plank_width / 2
        right = self.x + self.plank_width / 2
        _, min_distance = camera.get_min_distance(pygame.Vector3(0.0, self.y, 0.0))
        self.top = self.z + self.plank_depth / 2
        top = clip(self.top, min_distance, None)
        bottom = clip(self.z - self.plank_depth / 2, min_distance, None)
        tl = pygame.Vector3(left, self.y, top)
        tr = pygame.Vector3(right, self.y, top)
        br = pygame.Vector3(right, self.y, bottom)
        bl = pygame.Vector3(left, self.y, bottom)
        # 2D screen coordinates
        pts_3d = [tl, tr, br, bl]
        # Visibility check
        if all([pt_3d.z >= 0 for pt_3d in pts_3d]):
            points = [camera.project(pt_3d) for pt_3d in pts_3d]
            pygame.draw.polygon(screen, self.color, points)
        pass


class Wall(Plank):
    def draw(
        self,
        screen: pygame.Surface,
    ):
        global camera
        self.top = self.z + self.plank_depth / 2
        _, min_distance = camera.get_min_distance(pygame.Vector3(0.0, self.y, 0.0))
        top = clip(self.top, min_distance, None)
        bottom = clip(self.z - self.plank_depth / 2, min_distance, None)

        down = self.y
        up = self.y + self.plank_width
        tl = pygame.Vector3(self.x, down, top)
        tr = pygame.Vector3(self.x, up, top)
        br = pygame.Vector3(self.x, up, bottom)
        bl = pygame.Vector3(self.x, down, bottom)
        pts_3d = [tl, tr, br, bl]
        if all([pt_3d.z >= 0 for pt_3d in pts_3d]):
            points = [camera.project(pt_3d) for pt_3d in pts_3d]
            pygame.draw.polygon(screen, self.color, points)
        pass


def launch_running_bunny():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    w, h = screen.get_width(), screen.get_height()
    global camera
    camera = Camera(x=0, y=2.0, z=0, focal_length=100.0, w=w, h=h)
    clock = pygame.time.Clock()
    running = True
    dt = 0
    sandtrack = SandTrack(num_planks=70, z_source=10.0, element_type=Plank)
    sidewalls_left = SandTrack(
        num_planks=100,
        z_source=10.0,
        x_source=-3.5,
        randomness_amplitude=0,
        element_type=Wall,
    )
    sidewalls_right = SandTrack(
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
