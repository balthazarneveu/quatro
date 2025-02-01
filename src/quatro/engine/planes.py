import pygame
import math
from quatro.engine.maths import clip
from quatro.engine.pinhole_camera import Camera

from quatro.engine.primitives import draw_elements


class WallElement:
    """
    Base class representing a 3D wall or floor element for drawing in a 2D surface.
    """

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 10.0,
        z_size: float = 5.0,
        xy_size: float = 5.0,
        color=(139, 69, 19),
        intensity: float = 1.0,
        angle=0.0,
        camera: Camera = None,
    ) -> None:
        """
        :param x: The x position of the element on the ground.
        :param y: The y position of the element on the ground.
        :param z: Distance along the Z-axis from the camera/screen.
        :param z_size: Thickness of the element along the Z-axis.
        :param xy_size: Size of the element in the X and Y directions.
        :param color: The R, G, B color values for the element.
        :param intensity: A multiplier that affects the base color.
        :param angle: Rotation angle of the element in degrees.
        :param camera: The camera used for 3D to 2D projection.
        """
        self.x = x
        self.y = y
        self.z = z
        self.color = [_color * intensity for _color in color]
        self.z_size = z_size
        self.xy_size = (
            xy_size if isinstance(xy_size, (list, tuple)) else [xy_size, xy_size]
        )
        self.back = self.z + self.z_size / 2
        self.front = self.z - self.z_size / 2
        self.angle = angle
        self.camera = camera
        self.visible = True
        self.enabled = True

    def out_of_screen(self):
        min_distance_z = self.get_min_distance()
        if self.back <= min_distance_z:
            return True

    def get_min_distance(self):
        min_distance_x, min_distance_y = self.camera.get_min_distance(
            pygame.Vector3(self.x, self.y, 0.0)
        )
        return min(min_distance_x, min_distance_y)

    def get_coordinates(self) -> list[pygame.Vector3]:
        """
        Compute and return the 3D corner or shape points for this element.
        """
        raise NotImplementedError

    def draw(self, screen: pygame.Surface) -> None:
        """
        Perform final checks, then project and draw element into the given screen.
        """
        min_distance = self.get_min_distance()
        self.back = clip(self.z + self.z_size / 2, min_distance, None)
        self.front = clip(self.z - self.z_size / 2, min_distance, None)
        if not self.visible:
            return
        self.bounding_box = draw_elements(
            self.get_coordinates(),
            screen,
            self.camera,
            color=self.color,
        )


class Floor(WallElement):
    def get_coordinates(self) -> list[pygame.Vector3]:
        left = self.x - self.xy_size[0] / 2
        right = self.x + self.xy_size[0] / 2

        tl = pygame.Vector3(left, self.y, self.back)
        tr = pygame.Vector3(right, self.y, self.back)
        br = pygame.Vector3(right, self.y, self.front)
        bl = pygame.Vector3(left, self.y, self.front)
        pts_3d = [tl, tr, br, bl]
        return pts_3d


class Wall(WallElement):
    def get_coordinates(self) -> list[pygame.Vector3]:
        down = self.y
        up = self.y + math.cos(math.radians(self.angle)) * self.xy_size[1]
        x_offset = math.sin(math.radians(self.angle)) * self.xy_size[0]
        tl = pygame.Vector3(self.x, down, self.back)
        tr = pygame.Vector3(self.x + x_offset, up, self.back)
        br = pygame.Vector3(self.x + x_offset, up, self.front)
        bl = pygame.Vector3(self.x, down, self.front)
        pts_3d = [tl, tr, br, bl]
        return pts_3d


class FacingWall(WallElement):
    def get_coordinates(self) -> list[pygame.Vector3]:
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
