import random
import pygame
from collections import deque

MOVING_TRACK_SPEED = 1.0


class MovingTrack:
    def __init__(
        self,
        num_elements=10,
        x_source=0.0,
        z_source=10.0,
        z_size=None,
        randomness_amplitude=0.0,
        element_type=None,
        speed=MOVING_TRACK_SPEED,
        **kwargs,
    ):
        self.z_source = z_source
        self.x_source = x_source
        self.randomness_amplitude = randomness_amplitude
        self.elements = deque(
            [
                element_type(
                    z=z_source - (i / num_elements) * z_source,
                    intensity=0.5 + random.uniform(0.0, 0.5),
                    x=self.x_source,
                    z_size=z_source / num_elements if z_size is None else z_size,
                    **kwargs,
                )
                for i in range(num_elements)
            ]  # first element is the farthest from the screen (= the back)
        )
        self.speed = speed

    def move(self, dt: float = 0.1):
        for element in self.elements:
            element.z -= self.speed * dt
        if self.elements[-1].out_of_screen():
            current_element = self.elements.pop()
            current_element.z = self.elements[0].z + self.z_source / len(
                self.elements
            )  # Need an extra offset to put it behind the back element
            current_element.x = self.x_source
            self.elements.appendleft(current_element)

    def draw(self, screen: pygame.Surface):
        for element in self.elements:
            element.draw(screen)


class MovingElement:
    def __init__(
        self,
        z_source=10.0,
        x_range=[-1, 1],
        num_elements=10,
        speed=MOVING_TRACK_SPEED,
        element_type=None,
        **kwargs,
    ):
        self.speed = speed
        self.z_source = z_source
        self.xrange = x_range
        self.elements = deque()
        for i in range(num_elements):
            z_value = z_source - (i / num_elements) * z_source
            x_value = random.uniform(x_range[0], x_range[1])
            self.elements.append(element_type(x=x_value, z=z_value, **kwargs))

    def move(self, dt: float = 0.1):
        for plank in self.elements:
            plank.z -= self.speed * dt
        if self.elements[-1].out_of_screen():
            current_element = self.elements.pop()
            current_element.z = self.elements[0].z + self.z_source / len(self.elements)
            current_element.x = random.uniform(self.xrange[0], self.xrange[1])
            current_element.visible = True
            current_element.enabled = True
            self.elements.appendleft(current_element)

    def draw(self, screen: pygame.Surface):
        for element in self.elements:
            element.draw(screen)
