import pygame
import math
import numpy as np


def rotate_point_around_axis(point, axis, angle_degree):
    angle = math.radians(angle_degree)
    if axis == "x":
        rotation_matrix = np.array(
            [
                1,
                0,
                0,
                0,
                math.cos(angle),
                -math.sin(angle),
                0,
                math.sin(angle),
                math.cos(angle),
            ]
        ).reshape(3, 3)
    elif axis == "y":
        rotation_matrix = np.array(
            [
                math.cos(angle),
                0,
                math.sin(angle),
                0,
                1,
                0,
                -math.sin(angle),
                0,
                math.cos(angle),
            ]
        ).reshape(3, 3)
    elif axis == "z":
        rotation_matrix = np.array(
            [
                math.cos(angle),
                -math.sin(angle),
                0,
                math.sin(angle),
                math.cos(angle),
                0,
                0,
                0,
                1,
            ]
        ).reshape(3, 3)
    else:
        raise ValueError("Axis must be 'x', 'y', or 'z'")

    return pygame.Vector3(*np.dot(rotation_matrix, point))


class Camera:
    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        z: float = 0,
        focal_length: float = 1.0,
        w: float = 1280,
        h: float = 720,
        pitch: float = 0.0,
    ):
        self.camera_position = pygame.Vector3(x, y, z)
        self.focal_length = focal_length
        self.screen_center = pygame.Vector2(w / 2, h / 2)
        self.w = w
        self.h = h
        self.pitch = pitch

    def project(self, point: pygame.Vector3) -> pygame.Vector2:
        relative_point = point - self.camera_position
        relative_point = rotate_point_around_axis(relative_point, "x", self.pitch)
        if relative_point.z <= 0:
            return None
        out = (
            self.focal_length
            * pygame.Vector2(
                relative_point.x / relative_point.z,
                -relative_point.y / relative_point.z,
            )
            + self.screen_center
        )
        return out

    def get_min_distance(self, point: pygame.Vector3) -> pygame.Vector2:
        relative_point = point - self.camera_position
        min_dist_x_clip = relative_point.x * self.focal_length / (self.w / 2)
        min_dist_y_clip = relative_point.y * self.focal_length / (self.h / 2)
        return abs(min_dist_x_clip), abs(min_dist_y_clip)
