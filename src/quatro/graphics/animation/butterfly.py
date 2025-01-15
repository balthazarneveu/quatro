import pygame
import math
from typing import Tuple, Union
from quatro.control.control import ControlledPlayer


class Butterfly(ControlledPlayer):
    """A class representing a butterfly that can be drawn on a pygame screen with flapping wings.

    Attributes:
        x (int): X-coordinate of the butterfly's position
        y (int): Y-coordinate of the butterfly's position
        size (int): Size of the butterfly in pixels
        color (Tuple[int, int, int]): RGB color tuple for the butterfly
        flap_speed (float): Speed of wing flapping animation
        time (float): Internal time counter for animation
    """

    def __init__(
        self,
        x: int,
        y: int,
        velocity: float = 0,
        size: int = 20,
        color: Union[str, Tuple[int, int, int]] = (255, 255, 255),
        flap_speed: float = 5,
    ) -> None:
        """Initialize a new Butterfly instance.

        Args:
            x (int): X-coordinate of the butterfly's position
            y (int): Y-coordinate of the butterfly's position
            size (int, optional): Size of the butterfly. Defaults to 20.
            color (Tuple[int, int, int], optional): RGB color tuple. Defaults to (255, 255, 255).
            flap_speed (float, optional): Speed of wing flapping. Defaults to 5.
        """
        super().__init__(x, y, velocity=velocity)
        self.size = size
        self.color = color
        self.flap_speed = flap_speed
        self.previous_time = pygame.time.get_ticks() / 1000
        self.previous_phase = 0

    def draw(self, screen: pygame.Surface, dt: float = 0) -> None:
        """Draw the butterfly on the given pygame surface.

        Args:
            screen (pygame.Surface): The pygame surface to draw on
            dt (float, optional): External current_time value (unused). Defaults to 0.
        """
        # Draw body (circle)
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size // 4)

        # Calculate wing angle
        current_phase = self.previous_phase + dt * self.flap_speed
        self.previous_phase = current_phase
        wing_angle = math.sin(current_phase) * 0.5

        # Calculate wing endpoints
        left_wing_end = (
            self.x - int(self.size * math.cos(wing_angle)),
            self.y - int(self.size * math.sin(wing_angle)),
        )
        right_wing_end = (
            self.x + int(self.size * math.cos(wing_angle)),
            self.y - int(self.size * math.sin(wing_angle)),
        )

        # Draw wings (lines)
        pygame.draw.line(screen, self.color, (self.x, self.y), left_wing_end, 4)
        pygame.draw.line(screen, self.color, (self.x, self.y), right_wing_end, 4)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    clock = pygame.time.Clock()

    butterfly = Butterfly(200, 150, size=30, color="red", flap_speed=10)

    running = True
    dt = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        butterfly.x = pygame.mouse.get_pos()[0]
        butterfly.y = pygame.mouse.get_pos()[1] - 10
        butterfly.draw(screen, dt=dt)
        pygame.display.flip()
        clock.tick(60)
        dt = clock.tick(60) / 1000
