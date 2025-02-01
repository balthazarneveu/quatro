import pygame
from quatro.engine.ellipse import draw_ellipse_angle
from quatro.engine.pinhole_camera import Camera


def draw_elements(
    elements_to_draw: list[dict] | list[pygame.Vector3] | dict,
    screen: pygame.Surface,
    camera: Camera,
    color: tuple[int, int, int] = None,
) -> pygame.Rect:
    """
    Draw the given 3D elements (polygons or ellipses) onto the screen.

    :param screen: The pygame Surface to draw on.
    :param camera: The camera used for projecting 3D points to 2D.
    :param color: The color (R, G, B) to draw polygons by default.
    :param elements_to_draw: A geometry definition list or dict (e.g. poly, ellipse).
    :return: A pygame.Rect bounding box that encloses all drawn shapes.
    """
    all_bounding_boxes = []
    if isinstance(elements_to_draw, list) and not isinstance(elements_to_draw[0], dict):
        elements_to_draw = [
            {"type": "poly", "content": {"points": elements_to_draw, "color": color}}
        ]
    for element_to_draw in elements_to_draw:
        geometry_type = element_to_draw.get("type", "poly")
        content = element_to_draw["content"]
        if geometry_type == "poly":
            pts_3d = content.get("points", [])
            color = content.get("color", color)
            if all([pt_3d.z >= 0 for pt_3d in pts_3d]):
                points = [camera.project(pt_3d) for pt_3d in pts_3d]
                if None in points:
                    continue
                pygame.draw.polygon(screen, color, points)
                all_bounding_boxes.append(
                    pygame.Rect(
                        min([pt.x for pt in points]),
                        min([pt.y for pt in points]),
                        max([pt.x for pt in points]) - min([pt.x for pt in points]),
                        max([pt.y for pt in points]) - min([pt.y for pt in points]),
                    )
                )
        if geometry_type == "ellipse":
            center_3d = content["center"]
            center = camera.project(center_3d)
            offset_x = camera.project(
                center_3d + pygame.Vector3(content["size_x"], 0.0, 0.0)
            )
            if offset_x is None:
                continue
            width = abs((offset_x - center).x)
            offset_y = camera.project(
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
                content.get("color", color),
                bounding_box,
                angle=content.get("angle", 0.0),
                width=content.get("width", 0.0),
            )
    if len(all_bounding_boxes) > 0:
        return all_bounding_boxes[0].unionall(all_bounding_boxes[1:])
    return pygame.Rect(0, 0, 0, 0)
