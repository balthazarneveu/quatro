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


camera = None


def clip(value, min_value, max_value):
    if min_value is None:
        return min(value, max_value)
    if max_value is None:
        return max(value, min_value)
    return min(max(value, min_value), max_value)


class SandTrack:
    def __init__(self, num_planks=10, z_source=10.0):
        self.z_source = z_source
        self.planks = [
            Plank(
                z=z_source - (i / num_planks) * z_source,
                intensity=0.5 + i / num_planks,
                x=random.uniform(-1, 1.0),
                plank_depth=1.0,
            )
            for i in range(num_planks)
        ]

    def move_planks(self, dt: float = 0.1):
        global camera
        for plank in self.planks:
            plank.z -= dt
            if plank.z <= 0.5:
                plank.z = self.z_source
                plank.x = random.uniform(-1, 1)

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
        plank_width: float = 3.0,
        color=(139, 69, 19),
        intensity=1.0,
    ):
        self.x = x
        self.y = y
        self.z = z
        self.color = [_color * intensity for _color in color]
        self.plank_depth = plank_depth
        self.plank_width = plank_width

    def draw(
        self,
        screen: pygame.Surface,
    ):
        global camera
        # 3D plank coordinates
        left = self.x - self.plank_width / 2
        right = self.x + self.plank_width / 2
        top = clip(self.z + self.plank_depth / 2, camera.min_distance, None)
        bottom = clip(self.z - self.plank_depth / 2, camera.min_distance, None)
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


def launch_running_bunny():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    w, h = screen.get_width(), screen.get_height()
    global camera
    camera = Camera(x=0, y=2.0, z=0, focal_length=100.0, w=w, h=h)
    clock = pygame.time.Clock()
    running = True
    dt = 0
    plank = Plank()
    sandtrack = SandTrack()

    player_pos = pygame.Vector2(w / 2, 3 * h / 4)
    player = Bunny(*player_pos, size=50, animation_speed=10)
    current_background = "night_wheat_field"
    while running:
        keys = pygame.key.get_pressed()
        running = handle_quit(keys)
        draw_background_from_asset(screen, current_background)

        sandtrack.move_planks(dt=dt)
        sandtrack.draw(screen)
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
