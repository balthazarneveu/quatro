import pygame
import math
import random
from typing import Tuple


class Wheat:
    def __init__(
        self,
        x: int,
        y: int,
        height: int = 40,
        color: Tuple[int, int, int] = (245, 222, 179),
        sway_speed: float = 1.0,
    ):
        self.x = x
        self.y = y
        self.height = height * random.uniform(0.8, 3 * 1.2)  # Random height variation
        self.color = color
        self.sway_speed = sway_speed
        self.segments = random.randint(3, 5)  # Random number of segments
        self.variation = random.uniform(0.8, 1.2)
        # Store random variations
        self.stalk_width = random.randint(1, 3)
        self.head_size = random.randint(6, 10)
        self.head_count = random.randint(3, 5)
        self.head_angle_start = random.uniform(math.pi / 8, math.pi / 4)
        self.head_angle_spread = random.uniform(math.pi / 8, math.pi / 4)
        self.phase = self.variation

    def draw(self, screen: pygame.Surface, dt: float) -> None:
        # Draw main stalk segments
        prev_x, prev_y = self.x, self.y
        for i in range(self.segments):
            segment_ratio = (i + 1) / self.segments
            self.phase += dt * self.sway_speed
            sway = math.sin(self.phase) * 5 * segment_ratio

            next_x = self.x + sway
            next_y = self.y - (self.height * segment_ratio)

            pygame.draw.line(
                screen, self.color, (prev_x, prev_y), (next_x, next_y), self.stalk_width
            )
            prev_x, prev_y = next_x, next_y

        # Draw wheat head with variations
        for i in range(self.head_count):
            angle = self.head_angle_start + (i * self.head_angle_spread)
            head_x = prev_x + math.cos(angle) * self.head_size
            head_y = prev_y + math.sin(angle) * self.head_size
            pygame.draw.ellipse(screen, self.color, (head_x - 2, head_y - 2, 4, 4))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    wheat_stalks = [
        Wheat(400 + random.randint(-200, 200), 500 + random.randint(-50, 50))
        for _ in range(200)
    ]

    running = True
    dt = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((135, 206, 235))  # Sky blue background
        pygame.draw.rect(screen, (139, 69, 19), (0, 450, 800, 150))  # Brown ground
        for wheat in wheat_stalks:
            wheat.draw(screen, dt)

        pygame.display.flip()
        dt = clock.tick(60) / 1000

    pygame.quit()
