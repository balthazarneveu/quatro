import random
import pygame
from collections import deque

MOVING_TRACK_SPEED = 1.0


class MovingStuff:
    def __init__(self, speed: float = MOVING_TRACK_SPEED):
        self.standard_speed = speed
        self.speed = speed

    def pause(self) -> None:
        self.speed = 0.0

    def resume(self) -> None:
        self.speed = self.standard_speed

    def hide(self) -> None:
        for element in self.elements:
            element.visible = False
            element.enabled = False

    def show(self) -> None:
        for element in self.elements:
            element.visible = True
            element.enabled = True

    def toggle_pause(self, pause: bool = False) -> None:
        if pause:
            self.pause()
        else:
            self.resume()

    def toggle_visibility(self, visible: bool = False) -> None:
        if visible:
            self.show()
        else:
            self.hide()


class MovingTrack(MovingStuff):
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
        super().__init__(speed=speed)
        self.z_source = z_source
        self.x_source = x_source
        self.randomness_amplitude = randomness_amplitude
        self.element_size = z_source / num_elements if z_size is None else z_size
        # Add small overlap to prevent gaps
        self.element_size *= 1.005
        self.elements = deque(
            [
                element_type(
                    z=z_source - i * self.element_size,  # Use fixed element_size
                    intensity=0.5 + random.uniform(0.0, 0.5),
                    x=self.x_source,
                    z_size=self.element_size,
                    **kwargs,
                )
                for i in range(num_elements)
            ]  # first element is the farthest from the screen (= the back)
        )

    def move(self, dt: float = 0.1):
        for element in self.elements:
            element.z -= self.speed * dt
        if self.elements[-1].out_of_screen():
            current_element = self.elements.pop()
            # Use stored element_size for precise positioning
            current_element.z = self.elements[0].z + self.element_size
            current_element.x = self.x_source
            self.elements.appendleft(current_element)

    def draw(self, screen: pygame.Surface):
        for element in self.elements:
            element.draw(screen)


class MovingElement(MovingStuff):
    def __init__(
        self,
        z_source=10.0,
        x_range=[-1, 1],
        num_elements=10,
        speed=MOVING_TRACK_SPEED,
        element_type=None,
        **kwargs,
    ):
        super().__init__(speed=speed)
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
