class ControlledPlayer:
    def __init__(
        self, x: int, y: int, velocity: float = 0, animation_speed: float = 1.0
    ) -> None:
        self.set_position(x, y)
        self.velocity = velocity
        self.animation_speed = animation_speed
        self.animation_speed_default = animation_speed
        self.prev_position = None

    def set_position(self, x: int, y: int) -> None:
        """Set the position of the butterfly.

        Args:
            x (int): X-coordinate of the butterfly's position
            y (int): Y-coordinate of the butterfly's position
        """
        self.x = x
        self.y = y

    def __str__(self):
        return f"Player at ({self.x}, {self.y})"

    def pause(self) -> None:
        self.animation_speed = 0
        if self.prev_position is None:
            self.prev_position = (self.x, self.y)
        self.x = self.prev_position[0]
        self.y = self.prev_position[1]

    def resume(self) -> None:
        self.animation_speed = self.animation_speed_default
        self.prev_position = None

    def toggle_pause(self, pause: bool = False) -> None:
        if pause:
            self.pause()
        else:
            self.resume()
