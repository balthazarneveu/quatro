import pygame
import math
from quatro.control.control import ControlledPlayer
from quatro.engine.pinhole_camera import Camera
from quatro.engine.primitives import draw_elements


class Bunny(ControlledPlayer):
    """A class representing a bunny

    Attributes:
        x (int): X-coordinate of the Bunny's position
        y (int): Y-coordinate of the Bunny's position
        z (float): Z-coordinate of the Bunny's position
        size (int): Size of the bunny in pixels
        time (float): Internal time counter for animation
    """

    def __init__(
        self,
        x: int,
        y: int,
        z: float = 0.0,
        velocity: float = 0,
        size: float = 1.0,
        animation_speed: float = 40.0,
        global_intensity: float = 0.8,
        camera: Camera = None,
    ) -> None:
        """Initialize a new Bunny instance.

        Args:
            x (int): X-coordinate of the Bunny's position
            y (int): Y-coordinate of the Bunny's position
            z (float): Z-coordinate of the Bunny's position
            size (int, optional): Size of the Bunny. Defaults to 20.
        """
        super().__init__(x, y, velocity=velocity, animation_speed=animation_speed)
        self.z = z
        self.size = size
        self.previous_time = pygame.time.get_ticks() / 1000
        self.previous_phase = 0
        self.global_intensity = global_intensity
        self.bounding_box = None
        self.elements = []
        self.camera = camera
        self.enabled = True
        self._prepare_draw_body()

    def animate(self, dt: float = 0) -> None:
        current_phase = self.previous_phase + dt * self.animation_speed
        self.previous_phase = current_phase

    def oscillate(self, min_val, max_val, speed=1) -> None:
        oscillation = (
            math.sin(self.previous_phase * speed) * 0.5
        )  # Oscillates between -0.5 and +0.5
        return min_val + (max_val - min_val) * (oscillation + 0.5)

    def draw(self, screen: pygame.Surface, dt: float = 0) -> None:
        """Draw the bunny on the given pygame surface.

        Args:
            screen (pygame.Surface): The pygame surface to draw on
            dt (float, optional): External current_time value (unused). Defaults to 0.
        """

        self.animate(dt)
        self.elements = []  # Reset elements list

        self._draw_head(y_offset=self.oscillate(-0.05, 0) * self.size)
        self._draw_ears(angle=10 + self.oscillate(0, 10))
        self._prepare_draw_body()
        self._draw_legs(
            intensity=self.oscillate(0.8, 1.0),
            leg_height_factor=self.oscillate(0.8, 1.0),
            angle=self.oscillate(0, 1),
        )
        self._draw_arm(intensity=0.8, angle_offset=self.oscillate(20, 30))
        self._draw_body(
            tail_offset=self.oscillate(-1, 1, speed=-1) * self.size * 0.02,
            intensity=0.95,
        )

        self.bounding_box = draw_elements(self.elements, screen, self.camera)

    def _draw_head(self, y_offset=0, intensity: float = 1.0) -> None:
        intensity *= self.global_intensity
        color = (intensity * 255, intensity * 255, intensity * 255)
        head_element = {
            "type": "ellipse",
            "content": {
                "center": pygame.Vector3(self.x, self.y - y_offset, self.z),
                "size_x": 3 * self.size / 4,
                "size_y": 3 * self.size / 4,
                "color": color,
            },
        }
        self.elements.append(head_element)

    def _draw_ears(self, angle: float = 10, intensity: float = 1.0) -> None:
        intensity *= self.global_intensity
        color = (intensity * 255, intensity * 255, intensity * 255)
        ear_width = self.size // 4
        ear_height = self.size

        ear_elements = [
            {
                "type": "ellipse",
                "content": {
                    "center": pygame.Vector3(
                        self.x + sign * 1.2 * ear_width,
                        self.y + ear_height * 0.75,
                        self.z,
                    ),
                    "size_x": ear_width,
                    "size_y": ear_height,
                    "color": color,
                    "angle": -sign * angle,
                },
            }
            for sign in [-1.0, 1.0]
        ]
        self.elements.extend(ear_elements)

    def _prepare_draw_body(
        self,
    ) -> None:
        body_height = self.size * 1.2
        self.body_y = self.y - self.size // 4
        self.body_bottom = self.body_y - body_height
        self.body_height = body_height

    def _draw_body(
        self, intensity: float = 1, angle=0, tail_offset=0, skip=False
    ) -> None:
        body_width = self.size * 3 // 4
        intensity *= self.global_intensity
        color = (intensity * 255, intensity * 255, intensity * 255)
        tail_color = (intensity * 230, intensity * 230, intensity * 230)

        elements = [
            {
                "type": "ellipse",
                "content": {
                    "center": pygame.Vector3(
                        self.x, self.body_y - self.body_height / 2, self.z
                    ),
                    "size_x": body_width,
                    "size_y": self.body_height,
                    "color": color,
                },
            },
            {
                "type": "ellipse",
                "content": {
                    "center": pygame.Vector3(
                        self.x,
                        self.body_y - (self.body_height * 0.8 + tail_offset),
                        self.z,
                    ),
                    "size_x": self.size * 0.78,
                    "size_y": self.size * 0.8,
                    "color": tail_color,
                    "angle": angle,
                },
            },
        ]
        self.elements.extend(elements)

    def _draw_legs(self, intensity=1, leg_height_factor=1.0, angle=0) -> None:
        intensity *= self.global_intensity
        leg_width = self.size // 4
        leg_height = self.size * 0.8 * leg_height_factor
        leg_y = self.body_bottom + self.body_height * 0.15
        leg_color = (intensity * 255, intensity * 255, intensity * 255)

        leg_elements = [
            {
                "type": "ellipse",
                "content": {
                    "center": pygame.Vector3(
                        self.x - sign * (leg_width + leg_width // 2),
                        leg_y - leg_height / 2,
                        self.z,
                    ),
                    "size_x": leg_width,
                    "size_y": leg_height,
                    "color": leg_color,
                    "angle": sign * angle,
                },
            }
            for sign in [-1, 1]
        ]
        self.elements.extend(leg_elements)

    def _draw_arm(self, intensity=1, angle_offset=0) -> None:
        intensity *= self.global_intensity
        arm_width = self.size // 4
        arm_height = self.size * 0.8
        arm_y = self.y - self.body_height * 0.3
        arm_color = (intensity * 255, intensity * 255, intensity * 255)

        arm_elements = [
            {
                "type": "ellipse",
                "content": {
                    "center": pygame.Vector3(
                        self.x + sign * (arm_width + arm_width // 2 + self.size * 0.12),
                        arm_y - arm_height / 2,
                        self.z,
                    ),
                    "size_x": arm_width,
                    "size_y": arm_height,
                    "color": arm_color,
                    "angle": sign * angle_offset,
                },
            }
            for sign in [-1, 1]
        ]
        self.elements.extend(arm_elements)


class Shadow:
    def __init__(self, x, y, z, shadow_size=1.0, camera: Camera = None, intensity=0.1):
        self.x = x
        self.y = y
        self.z = z  # z position won't affect rendering since shadow is at z=0
        self.width = shadow_size
        self.camera = camera  # Will be set when drawing
        self.intensity = intensity

    def draw(self, screen):
        shadow_element = {
            "type": "ellipse",
            "content": {
                "center": pygame.Vector3(self.x, self.y, self.z),
                "size_x": self.width,
                "size_y": self.width / 2.0,
                "color": (
                    self.intensity * 255,
                    self.intensity * 255,
                    self.intensity * 255,
                ),
            },
        }
        draw_elements([shadow_element], screen, self.camera)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()

    w, h = screen.get_width(), screen.get_height()
    f_factor = 10.0
    camera = Camera(
        x=0.0,
        y=0.0 * f_factor,
        z=0.0,
        focal_length=100.0 * f_factor,
        w=w,
        h=h,
        pitch=0.0,
        yaw=0.0,
    )
    bunny = Bunny(0.0, 0.0, z=5.0, size=10.0, camera=camera)
    dt = 0
    from quatro.system.quit import handle_quit

    while handle_quit(pygame.key.get_pressed()):
        screen.fill((0, 0, 0))
        bunny.x = 0.0
        bunny.y = 0.0
        bunny.z = 100.0
        bunny.draw(screen, dt=dt)
        pygame.display.flip()
        clock.tick(60)
        dt = clock.tick(60) / 1000
