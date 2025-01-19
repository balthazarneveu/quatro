import random
import pygame
from collections import deque


class MovingTrack:
    def __init__(
        self,
        num_planks=10,
        x_source=0.0,
        z_source=10.0,
        randomness_amplitude=0.0,
        element_type=None,
        speed=1.0,
        **kwargs,
    ):
        self.z_source = z_source
        self.x_source = x_source
        self.randomness_amplitude = randomness_amplitude
        self.planks = deque(
            [
                element_type(
                    z=z_source - (i / num_planks) * z_source,
                    intensity=0.5 + random.uniform(0.0, 0.5),
                    x=self.x_source,
                    z_size=z_source / num_planks,
                    **kwargs,
                )
                for i in range(num_planks)
            ]  # first element is the farthest from the screen (= the back)
        )
        self.speed = speed

    def move_planks(self, dt: float = 0.1):
        global camera
        for plank in self.planks:
            plank.z -= self.speed * dt
        if self.planks[-1].out_of_screen():
            current_plank = self.planks.pop()
            current_plank.z = self.planks[0].z + self.z_source / len(
                self.planks
            )  # Need an extra offset to put it behind the back plank
            current_plank.x = self.x_source
            self.planks.appendleft(current_plank)

    def draw(self, screen: pygame.Surface):
        for plank in self.planks:
            plank.draw(screen)
