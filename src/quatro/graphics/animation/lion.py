import pygame
from quatro.control.control import ControlledPlayer
from quatro.engine.pinhole_camera import Camera


class Lion(ControlledPlayer):
    """A class representing a Lion using sprite animations"""

    def __init__(
        self,
        x: int,
        y: int,
        z: float = 0.0,
        velocity: float = 0,
        size: float = 1.0,
        camera: Camera = None,
    ) -> None:
        super().__init__(x, y, velocity=velocity)
        self.z = z
        self.size = size
        self.camera = camera
        self.enabled = True
        self.bounding_box = None

        # Load the sprite sheet
        self.sprite_sheet = pygame.image.load("assets/sprites/lion.png").convert_alpha()

        # Each sprite in your generated PNG is in a 2x2 grid → 4 sprites total
        sheet_w, sheet_h = self.sprite_sheet.get_size()
        frame_w = sheet_w // 2
        frame_h = sheet_h // 2

        self.size = size / frame_h  # scale based on height

        # Cut out the 4 frames
        self.frames = []
        for row in range(2):
            for col in range(2):
                rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
                frame = self.sprite_sheet.subsurface(rect)
                # scale to desired size
                frame = pygame.transform.scale(
                    frame, (int(frame_w * size), int(frame_h * size))
                )
                self.frames.append(frame)

        # Map actions to frames
        self.actions = {
            "idle": self.frames[0],
            "drinking": self.frames[1],
            "dizzy": self.frames[2],
            "happy": self.frames[3],
        }

        self.current_action = "idle"
        self.facing_right = False

    def set_action(self, action: str) -> None:
        """Set the current action (idle, drinking, dizzy, happy)."""
        if action in self.actions:
            self.current_action = action

    def determine_direction(self) -> None:
        if not hasattr(self, "_last_x"):
            self._last_x = self.x

        dx = self.x - self._last_x
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
        self._last_x = self.x

    def draw(self, screen: pygame.Surface, dt: float = 0) -> None:
        """Draw the lion on screen and update bounding box"""
        if not self.camera or not self.enabled:
            return

        # Determine facing direction based on x position delta
        self.determine_direction()

        # Get the current frame
        frame = self.actions[self.current_action]

        # Flip if facing left
        if self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        # Project the center position using the camera
        center_3d = pygame.Vector3(self.x, self.y, self.z)
        center_2d = self.camera.project(center_3d)
        if center_2d is None:
            return

        # Calculate projected size based on a reference point offset in z
        ref_point = self.camera.project(center_3d + pygame.Vector3(1, 0, 0))
        if ref_point is None:
            return

        # Scale factor based on z-distance (perspective)
        scale_factor = abs((center_2d - ref_point).length()) * self.size

        # Scale the frame
        frame_w, frame_h = frame.get_size()
        scaled_size = (int(frame_w * scale_factor), int(frame_h * scale_factor))
        scaled_frame = pygame.transform.scale(frame, scaled_size)

        # Position the sprite
        rect = scaled_frame.get_rect(center=center_2d)
        screen.blit(scaled_frame, rect)

        # Update bounding box (used for collision detection)
        # Rescale the bounding box so the width is half the size
        bbox = rect.copy()
        bbox.width = rect.width // 2
        bbox.left += (rect.width - bbox.width) // 2  # center the bbox horizontally
        self.bounding_box = bbox

        # DEBUG: Draw the bounding box (optional)
        # pygame.draw.rect(screen, (255, 0, 0), self.bounding_box, 2)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 800))
    clock = pygame.time.Clock()

    lion = Lion(0.0, 0.0, z=5.0, size=0.4)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Example: change action with keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    lion.set_action("idle")
                elif event.key == pygame.K_2:
                    lion.set_action("drinking")
                elif event.key == pygame.K_3:
                    lion.set_action("dizzy")
                elif event.key == pygame.K_4:
                    lion.set_action("happy")

        # lion.update_movement(keys, dt=dt)
        if keys[pygame.K_LEFT]:
            lion.x -= 200 * dt
        if keys[pygame.K_RIGHT]:
            lion.x += 200 * dt

        screen.fill((180, 220, 255))  # sky color
        lion.draw(screen, dt)
        pygame.display.flip()

    pygame.quit()
