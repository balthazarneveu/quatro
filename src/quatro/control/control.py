class ControlledPlayer:
    def __init__(self, x: int, y: int, velocity: float = 0) -> None:
        self.set_position(x, y)
        self.velocity = velocity

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
