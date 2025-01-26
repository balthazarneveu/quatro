import pygame
from typing import Tuple


def draw_ellipse_angle(
    surface: pygame.Surface,
    color: Tuple[int, int, int],
    rect: pygame.Rect,
    angle: float,
    width: float = 0,
):
    """Draw an ellipse on a pygame surface with a specified rotation angle.

    Args:
        surface (pygame.Surface): The surface to draw on
        color (tuple): RGB or RGBA color tuple
        rect (tuple): Rectangle tuple (x, y, width, height) defining the ellipse bounds
        angle (float): Rotation angle in degrees
        width (int, optional): Width of ellipse outline. If 0, ellipse is filled. Defaults to 0.

    Returns:
        None

    Note:
        This function creates a temporary surface to draw the ellipse, rotates it,
        then blits it onto the target surface. This allows for smooth rotation of ellipses
        while preserving transparency.
    """
    target_rect = pygame.Rect(rect)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(shape_surf, color, (0, 0, *target_rect.size), width)
    rotated_surf = pygame.transform.rotate(shape_surf, angle)
    surface.blit(rotated_surf, rotated_surf.get_rect(center=target_rect.center))
