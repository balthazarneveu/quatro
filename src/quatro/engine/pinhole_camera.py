import pygame
from quatro.engine.maths import clip


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
