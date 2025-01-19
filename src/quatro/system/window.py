import pygame
from typing import Tuple, Optional


def init_screen(resolution: Optional[Tuple[int, int]] = None) -> pygame.Surface:
    pygame.init()
    if resolution is None:
        resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
    screen = pygame.display.set_mode(resolution, pygame.NOFRAME)
    return screen
