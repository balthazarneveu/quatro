import pygame
from pathlib import Path
from quatro.graphics.assets.image_assets import BACKGROUNDS, PATH
import logging


CACHED_IMAGES = {}


def clear_cache():
    """Clear the cache of images"""
    global CACHED_IMAGES
    CACHED_IMAGES = {}


def draw_background(screen: pygame.display, background_image_path: Path) -> None:
    """Load background image and draw it on the screen

    Args:
        screen (pygame.display): Display object from pygame
        background_image_path (Path): Path to the background image.
        Blit the image onto the screen to wipe out the previous
    """
    global CACHED_IMAGES
    width, heigth = screen.get_width(), screen.get_height()
    key = (background_image_path, (width, heigth))
    background_image = CACHED_IMAGES.get(key, None)
    if background_image is None:
        logging.info(f"load background {background_image}")
        background_image = pygame.image.load(background_image_path)
        image_width, image_height = background_image.get_size()
        target_aspect = width / heigth
        image_aspect = image_width / image_height

        if image_aspect > target_aspect:
            # Image is wider than target aspect ratio, crop the sides
            new_width = int(image_height * target_aspect)
            offset = (image_width - new_width) // 2
            background_image = background_image.subsurface(
                (offset, 0, new_width, image_height)
            )
        elif image_aspect < target_aspect:
            # Image is taller than target aspect ratio, crop the top and bottom
            new_height = int(image_width / target_aspect)
            offset = (image_height - new_height) // 2
            background_image = background_image.subsurface(
                (0, offset, image_width, new_height)
            )
        background_image = pygame.transform.scale(
            background_image, (width, heigth)
        ).convert()
        CACHED_IMAGES[key] = background_image
    screen.blit(background_image, (0, 0))


def draw_background_from_asset(screen: pygame.display, background_name: str) -> None:
    """Load background image and draw it on the screen directly from an assert name

    Args:
        screen (pygame.display): Display object from pygame
        background_name (str): Name of the background image, see `src/quatro/graphics/assets/image_assets.py`
    """
    assert background_name in BACKGROUNDS, f"Background {background_name} not found"
    background_image_path = BACKGROUNDS[background_name][PATH]
    draw_background(screen, background_image_path)
