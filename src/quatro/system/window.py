import pygame
from typing import Tuple, Optional


def init_screen(resolution: Optional[Tuple[int, int]] = None) -> pygame.Surface:
    pygame.init()
    flags = pygame.NOFRAME
    if resolution is None:
        resolution = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        flags |= pygame.FULLSCREEN
    screen = pygame.display.set_mode(resolution, flags)
    return screen
