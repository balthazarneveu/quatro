from interactive_pipe import (
    interactive_pipeline,
    interactive,
    TimeControl,
    KeyboardControl,
)
from quatro.graphics.animation.butterfly_numpy import draw_butterfly
import numpy as np
from PIL import Image
from quatro.graphics.assets.image_assets import BACKGROUNDS, PATH, SIZE
from quatro.system.quit import QUIT
import logging


def get_background(background_name="sunset_field"):
    """Add a background color to the image"""
    background = BACKGROUNDS[background_name]
    logging.warning(f"load background {background_name}")
    background_pth = background[PATH]
    if background_pth.exists():
        img = Image.open(background_pth)
        size = background[SIZE]
        img = img.resize((size[0] // 2, size[1] // 2))
        return np.array(img) / 255.0
    else:
        return np.ones((256, 256, 3)) * 0.1


def physics_model(jump=False, state={}):
    time = state["time"]
    state["y"] = state.get("y", 0.5)
    x = 0.5
    prev_time = state.get("prev_time", 0)
    time_diff = time - prev_time
    state["prev_time"] = time
    previous_jump = state.get("jump", False)
    if jump != previous_jump:
        trigger_jump = True
        state["jump"] = jump
    else:
        trigger_jump = False
    if trigger_jump:
        state["velocity"] = state.get("velocity", 0) + 0.01 * 30 * 3
    if state["y"] > 0:
        state["velocity"] = state.get("velocity", 0) - 0.01 / 10.0 * 2
    state["velocity"] = np.clip(state["velocity"], None, 0.2)  # keep within bounds
    state["y"] += state["velocity"] * time_diff
    state["y"] = np.clip(state["y"], 0.0, 1.0)  # keep within bounds
    if state["y"] <= 0 or state["y"] >= 1:
        state["velocity"] = 0
    state["x"] = x


def place_butteffly(img, flapping_speed=10.0, state={}):
    """Place a butterfly at position x, y"""
    out = img.copy()
    x = state.get("x", 0.5)
    y = state.get("y", 0.5)
    time = state["time"]
    draw_butterfly(
        out, time, x, y, flapping_speed=flapping_speed, size=5.0, color=[0.5, 0.0, 0.1]
    )
    return out


def get_time(time: float = 0, state={}):
    state["time"] = time


def draw_pipes(bg, pipe_speed=0.8, state={}):
    time = state["time"]
    out = bg.copy()
    pipe_width = 20
    pipe_height = 100
    pipe_gap = 50
    pipe_x = (1 - (time * pipe_speed) % 1) * (bg.shape[1] + pipe_width) - pipe_width
    pipe_y = (bg.shape[0] - pipe_height) // 2
    # Draw top pipe
    out[0 : pipe_y + pipe_height, int(pipe_x) : int(pipe_x + pipe_width), :] = [0, 1, 0]

    # Draw bottom pipe
    out[
        pipe_y + pipe_height + pipe_gap : -1, int(pipe_x) : int(pipe_x + pipe_width), :
    ] = [0, 1, 0]

    return out


def flappy_pipe():
    bg = get_background()
    get_time()
    bg_mv = draw_pipes(bg)
    physics_model()
    out = place_butteffly(bg_mv)
    return out


def launch_flappy_pipe(
    resolution=(1280, 720), debug: bool = False, audio: bool = True
) -> dict:
    from interactive_pipe.helper import _private

    _private.registered_controls_names = (
        []
    )  # this is for notebooks where you re-execute cells everytime.

    interactive(background_name=("sunset_field", list(BACKGROUNDS.keys())))(
        get_background
    )
    interactive(flapping_speed=(10, [0.0, 20.0]))(place_butteffly)
    interactive(jump=KeyboardControl(False, name="jump", keydown=" "))(physics_model)
    interactive(time=TimeControl(update_interval_ms=10, pause_resume_key="p"))(get_time)
    interactive(pipe_speed=(0.1, [0.0, 1.0]))(draw_pipes)
    interactive_pipeline(gui="qt", cache=True, size=resolution)(flappy_pipe)()
    return {QUIT: True}


if __name__ == "__main__":
    launch_flappy_pipe()
