import pygame
import math
from quatro.engine.maths import clip
from quatro.engine.ellipse import draw_ellipse_angle


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
        if not self.visible:
            return
        elements_to_draw = self.get_coordinates()
        if isinstance(elements_to_draw, list) and not isinstance(
            elements_to_draw[0], dict
        ):
            elements_to_draw = [
                {"type": "poly", "content": elements_to_draw},
            ]

        # Visibility check
        all_bounding_boxes = []
        for element_to_draw in elements_to_draw:
            geometry_type = element_to_draw.get("type", "poly")
            pts_3d = element_to_draw.get("content", [])
            if geometry_type == "poly":
                if all([pt_3d.z >= 0 for pt_3d in pts_3d]):
                    points = [self.camera.project(pt_3d) for pt_3d in pts_3d]
                    if None in points:
                        continue
                    pygame.draw.polygon(screen, self.color, points)
                    all_bounding_boxes.append(
                        pygame.Rect(
                            min([pt.x for pt in points]),
                            min([pt.y for pt in points]),
                            max([pt.x for pt in points]) - min([pt.x for pt in points]),
                            max([pt.y for pt in points]) - min([pt.y for pt in points]),
                        )
                    )
            if geometry_type == "ellipse":
                content = element_to_draw["content"]
                center_3d = content["center"]
                center = self.camera.project(center_3d)
                offset_x = self.camera.project(
                    center_3d + pygame.Vector3(content["size_x"], 0.0, 0.0)
                )
                if offset_x is None:
                    continue
                width = abs((offset_x - center).x)
                offset_y = self.camera.project(
                    center_3d
                    + pygame.Vector3(0.0, content["size_y"], content.get("size_z", 0.0))
                )
                if offset_y is None:
                    continue
                height = abs((offset_y - center).y)
                offset = pygame.Vector2(width, height)
                bounding_box = pygame.Rect(
                    center[0] - offset[0] / 2.0,
                    center[1] - offset[1] / 2.0,
                    width,
                    height,
                )
                all_bounding_boxes.append(bounding_box)
                draw_ellipse_angle(
                    screen,
                    content.get("color", (0, 0, 0)),
                    bounding_box,
                    angle=content.get("angle", 0.0),
                    width=content.get("width", 0.0),
                )
        if len(all_bounding_boxes) > 0:
            self.bounding_box = all_bounding_boxes[0].unionall(all_bounding_boxes[1:])
        else:
            self.bounding_box = pygame.Rect(0, 0, 0, 0)


class Floor(WallElement):
    def get_coordinates(self):
        left = self.x - self.xy_size[0] / 2
        right = self.x + self.xy_size[0] / 2

        tl = pygame.Vector3(left, self.y, self.back)
        tr = pygame.Vector3(right, self.y, self.back)
        br = pygame.Vector3(right, self.y, self.front)
        bl = pygame.Vector3(left, self.y, self.front)
        pts_3d = [tl, tr, br, bl]
        return pts_3d


class Wall(WallElement):
    def get_coordinates(self):
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
