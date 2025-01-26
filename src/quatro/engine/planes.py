import pygame
import math
from quatro.engine.maths import clip


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
        camera=None,
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
        self.camera = camera

    def out_of_screen(self):
        min_distance_z = self.get_min_distance()
        if self.back <= min_distance_z:
            return True

    def get_min_distance(self):
        min_distance_x, min_distance_y = self.camera.get_min_distance(
            pygame.Vector3(self.x, self.y, 0.0)
        )
        return min(min_distance_x, min_distance_y)

    def get_coordinates(self):
        raise NotImplementedError

    def draw(
        self,
        screen: pygame.Surface,
    ):
        # 3D plank coordinates
        min_distance = self.get_min_distance()
        self.back = clip(self.z + self.z_size / 2, min_distance, None)
        self.front = clip(self.z - self.z_size / 2, min_distance, None)

        pts_3d = self.get_coordinates()

        # Visibility check
        if all([pt_3d.z >= 0 for pt_3d in pts_3d]):
            points = [self.camera.project(pt_3d) for pt_3d in pts_3d]
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


class FacingWall(WallElement):
    def get_coordinates(self):
        assert len(self.xy_size) == 2
        left = self.x - self.xy_size[0] / 2
        right = self.x + self.xy_size[0] / 2
        down = self.y
        up = self.y + self.xy_size[1]
        tl = pygame.Vector3(left, up, self.back)
        tr = pygame.Vector3(right, up, self.back)
        br = pygame.Vector3(right, down, self.back)
        bl = pygame.Vector3(left, down, self.back)
        pts_3d = [tl, tr, br, bl]
        return pts_3d
