import pygame
import math
from typing import Tuple, Union
import time


class Butterfly:
    """A class representing a butterfly that can be drawn on a pygame screen with flapping wings.

    Attributes:
        x (int): X-coordinate of the butterfly's position
        y (int): Y-coordinate of the butterfly's position
        size (int): Size of the butterfly in pixels
        color (Tuple[int, int, int]): RGB color tuple for the butterfly
        flap_speed (float): Speed of wing flapping animation
        time (float): Internal time counter for animation
    """

    def __init__(self, x: int, y: int, size: int = 20,
                 color: Union[str, Tuple[int, int, int]] = (255, 255, 255),
                 flap_speed: float = 5) -> None:
        """Initialize a new Butterfly instance.

        Args:
            x (int): X-coordinate of the butterfly's position
            y (int): Y-coordinate of the butterfly's position
            size (int, optional): Size of the butterfly. Defaults to 20.
            color (Tuple[int, int, int], optional): RGB color tuple. Defaults to (255, 255, 255).
            flap_speed (float, optional): Speed of wing flapping. Defaults to 5.
        """
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.flap_speed = flap_speed
        self.start_time = pygame.time.get_ticks() / 1000

    def draw(self, screen: pygame.Surface, current_time: float = None) -> None:
        """Draw the butterfly on the given pygame surface.

        Args:
            screen (pygame.Surface): The pygame surface to draw on
            current_time (float, optional): External current_time value (unused). Defaults to 0.
        """
        if current_time is None:
            current_time = pygame.time.get_ticks() / 1000
        relative_time = current_time - self.start_time
        # Draw body (circle)
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size // 4)

        # Calculate wing angle
        wing_angle = math.sin(relative_time * self.flap_speed) * 0.5

        # Calculate wing endpoints
        left_wing_end = (
            self.x - int(self.size * math.cos(wing_angle)),
            self.y - int(self.size * math.sin(wing_angle))
        )
        right_wing_end = (
            self.x + int(self.size * math.cos(wing_angle)),
            self.y - int(self.size * math.sin(wing_angle))
        )

        # Draw wings (lines)
        pygame.draw.line(screen, self.color, (self.x, self.y), left_wing_end, 4)
        pygame.draw.line(screen, self.color, (self.x, self.y), right_wing_end, 4)

    def set_position(self, x: int, y: int) -> None:
        """Set the position of the butterfly.

        Args:
            x (int): X-coordinate of the butterfly's position
            y (int): Y-coordinate of the butterfly's position
        """
        self.x = x
        self.y = y


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    clock = pygame.time.Clock()

    butterfly = Butterfly(200, 150, size=30, color="red", flap_speed=10)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        butterfly.x = pygame.mouse.get_pos()[0]
        butterfly.y = pygame.mouse.get_pos()[1] - 10
        butterfly.draw(screen, current_time=time.time())
        pygame.display.flip()
        clock.tick(60)
