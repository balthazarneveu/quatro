import numpy as np


def draw_butterfly(
    out: np.ndarray,
    time: float,
    x: float,
    y: float,
    flapping_speed: float = 10.0,
    size: float = 1.0,
    body_size: int = 3,
    wing_size: int = 7,
    color: np.ndarray = np.array([1.0, 1.0, 1.0]),
) -> None:
    wing_size = int(wing_size * size)
    wing_angle = np.sin(time * flapping_speed) * 0.5  # Flapping effect
    shape = out.shape
    # Draw left wing
    for i in range(1, wing_size + 1):
        dx = int(i * np.cos(wing_angle))
        dy = int(i * np.sin(wing_angle))
        if (
            0 <= int((1 - y) * (shape[0] - 1)) + dy < shape[0]
            and 0 <= int(x * (shape[1] - 1)) - dx < shape[1]
        ):
            out[int((1 - y) * (shape[0] - 1)) + dy, int(x * (shape[1] - 1)) - dx, :] = (
                color
            )

    # Draw right wing
    for i in range(1, wing_size + 1):
        dx = int(i * np.cos(wing_angle))
        dy = int(i * np.sin(wing_angle))
        if (
            0 <= int((1 - y) * (shape[0] - 1)) + dy < shape[0]
            and 0 <= int(x * (shape[1] - 1)) + dx < shape[1]
        ):
            out[int((1 - y) * (shape[0] - 1)) + dy, int(x * (shape[1] - 1)) + dx, :] = (
                color
            )

    # Draw butterfly body
    body_size = int(2 * size)
    for i in range(-body_size, body_size + 1):
        for j in range(-body_size, body_size + 1):
            if i**2 + j**2 <= body_size**2:
                if (
                    0 <= int((1 - y) * (shape[0] - 1)) + i < shape[0]
                    and 0 <= int(x * (shape[1] - 1)) + j < shape[1]
                ):
                    out[
                        int((1 - y) * (shape[0] - 1)) + i,
                        int(x * (shape[1] - 1)) + j,
                        :,
                    ] = color
