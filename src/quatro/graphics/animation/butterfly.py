import numpy as np


def draw_butterfly(
    out: np.ndarray, time: float, x: float, y: float, flapping_speed=10.0
) -> None:
    wing_angle = np.sin(time * flapping_speed) * 0.5  # Flapping effect
    wing_size = 7
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
                1.0
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
                1.0
            )

    # Draw butterfly body
    body_size = 3
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
                    ] = 1.0
