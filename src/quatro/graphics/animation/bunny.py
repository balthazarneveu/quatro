import pygame
import math
from quatro.control.control import ControlledPlayer
from quatro.engine.ellipse import draw_ellipse_angle


class Bunny(ControlledPlayer):
    """A class representing a bunny

    Attributes:
        x (int): X-coordinate of the Bunny's position
        y (int): Y-coordinate of the Bunny's position
        size (int): Size of the bunny in pixels
        time (float): Internal time counter for animation
    """

    def __init__(
        self,
        x: int,
        y: int,
        velocity: float = 0,
        size: int = 20,
        animation_speed: float = 40.0,
        global_intensity: float = 0.8,
    ) -> None:
        """Initialize a new Bunny instance.

        Args:
            x (int): X-coordinate of the Bunny's position
            y (int): Y-coordinate of the Bunny's position
            size (int, optional): Size of the Bunny. Defaults to 20.
        """
        super().__init__(x, y, velocity=velocity)
        self.size = size
        self.previous_time = pygame.time.get_ticks() / 1000
        self.previous_phase = 0
        self.animation_speed = animation_speed
        self.global_intensity = global_intensity
        self.get_bounding_box()

    def get_bounding_box(self):
        extension = 1.2
        self.bounding_box = pygame.Rect(
            self.x - extension * self.size // 2,
            self.y - self.size,
            extension * self.size,
            self.size * 3,
        )

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
        self._draw_head(screen, y_offset=self.oscillate(-0.05, 0) * self.size)
        self._draw_ears(screen, angle=10 + self.oscillate(0, 10))
        self._draw_body(None)
        self._draw_legs(
            screen,
            intensity=self.oscillate(0.8, 1.0),
            leg_height_factor=self.oscillate(0.8, 1.0),
            angle=self.oscillate(0, 1),
        )
        self._draw_arm(screen, intensity=0.8, angle_offset=self.oscillate(20, 30))
        self._draw_body(
            screen,
            # angle=self.oscillate(-4, 4, speed=0.25),
            tail_offset=self.oscillate(-1, 1, speed=-1) * self.size * 0.02,
            intensity=0.95,
        )
        self.get_bounding_box()

    def _draw_head(
        self, screen: pygame.Surface, y_offset=0, intensity: float = 1.0
    ) -> None:
        intensity *= self.global_intensity
        color = (intensity * 255, intensity * 255, intensity * 255)
        pygame.draw.circle(
            screen, color, (self.x, self.y + y_offset), 3 * self.size // 8
        )

    def _draw_ears(
        self, screen: pygame.Surface, angle: float = 10, intensity: float = 1.0
    ) -> None:
        intensity *= self.global_intensity
        color = (intensity * 255, intensity * 255, intensity * 255)
        ear_width = self.size // 4
        ear_height = self.size
        left_ear_pos = (self.x - ear_width - ear_width // 2, self.y - ear_height)
        right_ear_pos = (self.x + ear_width // 2, self.y - ear_height)
        draw_ellipse_angle(
            screen,
            color,
            (left_ear_pos[0], left_ear_pos[1], ear_width, ear_height),
            angle,
        )
        draw_ellipse_angle(
            screen,
            color,
            (right_ear_pos[0], right_ear_pos[1], ear_width, ear_height),
            -angle,
        )

    def _draw_body(
        self, screen: pygame.Surface, intensity: float = 1, angle=0, tail_offset=0
    ) -> None:
        intensity *= self.global_intensity
        # Draw body as an elongated ellipse
        body_width = self.size * 3 // 4
        body_height = self.size * 1.2
        body_y = self.y + self.size // 4
        self.body_bottom = body_y + body_height
        self.body_height = body_height
        color = (intensity * 255, intensity * 255, intensity * 255)
        if screen is not None:
            pygame.draw.ellipse(
                screen,
                color,
                (self.x - body_width // 2, body_y, body_width, body_height),
            )
        # Draw a fluffy tail
        tail_x = self.x
        tail_y = body_y + body_height * 0.8 + tail_offset
        color = (intensity * 230, intensity * 230, intensity * 230)
        tail_width = self.size * 0.78
        tail_height = self.size * 0.8
        if screen is not None:
            draw_ellipse_angle(
                screen,
                color,
                (
                    tail_x - tail_width // 2,
                    tail_y - tail_height // 2,
                    tail_width,
                    tail_height,
                ),
                angle=angle,
            )

    def _draw_legs(
        self, screen: pygame.Surface, intensity=1, leg_height_factor=1.0, angle=0
    ) -> None:
        intensity *= self.global_intensity
        # Draw two legs as elongated ellipses
        leg_width = self.size // 4
        leg_height = self.size * 0.8 * leg_height_factor
        # Update leg positions based on body_bottom
        leg_y = self.body_bottom - self.body_height * 0.15
        left_leg_pos = (self.x - leg_width - leg_width // 2, leg_y)
        right_leg_pos = (self.x + leg_width // 2, leg_y)
        leg_color = (intensity * 255, intensity * 255, intensity * 255)
        draw_ellipse_angle(
            screen,
            leg_color,
            (left_leg_pos[0], left_leg_pos[1], leg_width, leg_height),
            angle,
        )
        draw_ellipse_angle(
            screen,
            leg_color,
            (right_leg_pos[0], right_leg_pos[1], leg_width, leg_height),
            -angle,
        )

    def _draw_arm(self, screen: pygame.Surface, intensity=1, angle_offset=0) -> None:
        intensity *= self.global_intensity
        # Draw two arms as elongated ellipses
        arm_width = self.size // 4
        arm_height = self.size * 0.8
        arm_y = self.y + self.body_height * 0.4
        left_arm_pos = (self.x - arm_width - arm_width // 2 - self.size * 0.12, arm_y)
        right_arm_pos = (self.x + arm_width // 2 + self.size * 0.12, arm_y)
        arm_color = (intensity * 255, intensity * 255, intensity * 255)

        draw_ellipse_angle(
            screen,
            arm_color,
            (left_arm_pos[0], left_arm_pos[1], arm_width, arm_height),
            -angle_offset,
        )
        draw_ellipse_angle(
            screen,
            arm_color,
            (right_arm_pos[0], right_arm_pos[1], arm_width, arm_height),
            angle_offset,
        )


1
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    clock = pygame.time.Clock()

    bunny = Bunny(200, 150, size=60)
    dt = 0
    from quatro.system.quit import handle_quit

    while handle_quit(pygame.key.get_pressed()):
        screen.fill((0, 0, 0))
        bunny.x = pygame.mouse.get_pos()[0] - 50
        bunny.y = pygame.mouse.get_pos()[1] - 20
        bunny.draw(screen, dt=dt)
        pygame.display.flip()
        clock.tick(60)
        dt = clock.tick(60) / 1000
