import pygame
from quatro.control.properties import KEYBOARD, WEBCAM
from quatro.graphics.background import draw_background_from_asset
from quatro.sound.sound import (
    play_sound,
    toggle_audio,
    stop_all_sounds,
    pause_all_sounds,
)
from quatro.system.input_handler import KeyDebouncer

from quatro.graphics.animation.lion import Lion
from quatro.system.quit import handle_quit
from quatro.system.window import init_screen
from quatro.engine.planes import Floor, Wall, FacingWall
from quatro.engine.endless_track import MovingTrack, MovingElement
from quatro.engine.pinhole_camera import Camera
from typing import List
import random

MAX_SCORE_WIN = "max_score_win"
SCORE = "score"
WIN = "win"
DIFFICULTY = "difficulty"
EASY = 0
MEDIUM = 1
HARD = 2

DEFAULT_GAME_CONFIG = {MAX_SCORE_WIN: 10, DIFFICULTY: EASY}


class RainManager:
    def __init__(
        self,
        track_width: float = 10.0,
        track_depth: float = 100.0,
        camera: Camera = None,
    ):
        self.track_width = track_width
        self.track_depth = track_depth
        self.camera = camera
        self.raindrops: List[Raindrop] = []
        self.spawn_timer = 0
        self.spawn_interval = 0.05  # Time between raindrop spawns
        self.fall_speed = 10.0  # Speed at which raindrops fall
        self.rainfall_location = random.uniform(
            -self.track_width / 2, self.track_width / 2
        )

    def update(self, dt: float):
        # Update spawn timer
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_raindrop()

        # Update raindrop positions and remove ones that hit the ground
        for drop in self.raindrops[:]:
            drop.y -= self.fall_speed * dt
            if drop.y <= 0:  # Ground level
                self.raindrops.remove(drop)

    def spawn_raindrop(self):
        # Random position across track width

        x = self.rainfall_location + random.uniform(
            -self.track_width / 8, self.track_width / 8
        )
        # Start high above
        y = 60.0  # Height above ground
        # Random position along track depth
        # z = random.uniform(0, self.track_depth)
        # z = 0.2 * self.track_depth
        z = 50
        new_drop = Raindrop(
            x=x,
            y=y,
            z=z,
            xy_size=(0.5, 0.8),  # Size of raindrop
            color=[100, 100, 255],  # Blue color
            camera=self.camera,
        )
        self.raindrops.append(new_drop)

    def draw(self, screen: pygame.Surface):
        for drop in self.raindrops:
            drop.draw(screen)


def draw_text(screen: pygame.Surface, text: str):
    """Draw text on the screen."""
    font = pygame.font.SysFont(None, 72)
    txt = font.render(text, True, (255, 255, 255))
    text_rect = txt.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(txt, text_rect)


class Rock(FacingWall):
    def __init__(self, *args, score_multiplier=-1, **kwargs):
        super().__init__(*args, **kwargs)
        self.score_multiplier = score_multiplier

    def get_coordinates(self):
        pts_3d = super().get_coordinates()
        top = (pts_3d[0] + pts_3d[1]) / 2.0
        # br, bl = pts_3d[2], pts_3d[3]
        # pts_3d_triangle = pts_3d[:2] + [(br + bl) / 2.0]
        geometry = [
            {
                "type": "ellipse",
                "content": {
                    "color": self.color,  # gray color for the rock
                    "center": top,
                    "size_x": self.xy_size[0] * 0.7,
                    "size_y": self.xy_size[1] * 0.7,
                    "angle": 0,
                    "width": 0,
                },
            }
        ]
        return geometry

    def collide(self, player_bounding_box: pygame.Rect, screen: pygame.Surface = None):
        if self.bounding_box is None or player_bounding_box is None:
            return False

        # Offset the player bounding box to fit the feets
        offset_player_bounding_box = player_bounding_box.copy()
        offset_player_bounding_box.y += player_bounding_box.height * 0.5
        offset_player_bounding_box.height *= 0.3
        offset_player_bounding_box.x += player_bounding_box.width * 0.25
        offset_player_bounding_box.width *= 0.5
        if screen:
            if self.visible:
                pygame.draw.rect(screen, (255, 0, 0), self.bounding_box, 2)
            pygame.draw.rect(screen, (0, 255, 0), offset_player_bounding_box, 2)
        collision = self.bounding_box.colliderect(offset_player_bounding_box)
        if not self.visible:
            collision = False
        if collision:
            self.visible = False
        return collision


class Raindrop(FacingWall):
    def __init__(self, *args, score_multiplier=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.score_multiplier = score_multiplier
        if self.color is None:
            self.randomize_color()
        else:
            self.standardize_color()

    def randomize_color(self):
        # Create shades of blue for raindrops
        blue_base = random.randint(200, 255)
        self.color = [100, 100, blue_base]  # Blue tint with some white
        self.highlight_color = [220, 220, 255]  # Light reflection

    def standardize_color(self):
        self.color = [100, 100, 255]  # Standard blue for raindrops
        self.highlight_color = [220, 220, 255]  # Standard light reflection

    def get_coordinates(self):
        pts_3d = super().get_coordinates()
        top = (pts_3d[0] + pts_3d[1]) / 2.0
        bottom = (pts_3d[2] + pts_3d[3]) / 2.0
        center = (top + bottom) / 2.0

        # Create main teardrop shape
        drop_height = self.xy_size[1]
        drop_width = self.xy_size[0] * 0.6

        geometry = [
            {
                "type": "ellipse",
                "content": {
                    "color": self.color,
                    "center": center,
                    "size_x": drop_width,
                    "size_y": drop_height,
                    "angle": 0,
                    "width": 0,
                },
            },
            # Add highlight reflection (smaller ellipse in upper right)
            {
                "type": "ellipse",
                "content": {
                    "color": self.highlight_color,
                    "center": center
                    + pygame.Vector3(drop_width * 0.2, -drop_height * 0.2, 0),
                    "size_x": drop_width * 0.3,
                    "size_y": drop_height * 0.3,
                    "angle": -20,
                    "width": 0,
                },
            },
        ]
        return geometry

    def collide(self, player_bounding_box: pygame.Rect, screen: pygame.Surface = None):
        if self.bounding_box is None or player_bounding_box is None:
            return False

        # Offset the player bounding box to fit the feets
        offset_player_bounding_box = player_bounding_box.copy()
        offset_player_bounding_box.y += player_bounding_box.height * 0.5
        offset_player_bounding_box.height *= 0.3
        offset_player_bounding_box.x += player_bounding_box.width * 0.25
        offset_player_bounding_box.width *= 0.5
        if screen:
            if self.visible:
                pygame.draw.rect(screen, (255, 0, 0), self.bounding_box, 2)
            pygame.draw.rect(screen, (0, 255, 0), offset_player_bounding_box, 2)
        collision = self.bounding_box.colliderect(offset_player_bounding_box)
        if not self.visible:
            collision = False
        if collision:
            self.visible = False
        return collision


class Hole(Floor):
    def __init__(self, *args, score_multiplier=-1, **kwargs):
        super().__init__(*args, **kwargs)
        self.score_multiplier = score_multiplier

    def get_coordinates(self):
        pts_3d = super().get_coordinates()
        geometry = [
            {
                "type": "ellipse",
                "content": {
                    "color": (30, 30, 30),  # dark green color
                    "center": (pts_3d[0] + pts_3d[1] + pts_3d[2] + pts_3d[3]) / 4.0,
                    "size_x": self.xy_size[0],
                    "size_y": 0,
                    "size_z": self.xy_size[1],
                    "angle": 0.0,
                    "width": 0,
                },
            }
        ]
        return geometry

    def collide(self, player_bounding_box: pygame.Rect, screen: pygame.Surface = None):
        if player_bounding_box is None:
            return False
        # Offset the player bounding box to fit the feets
        offset_player_bounding_box = player_bounding_box.copy()
        offset_player_bounding_box.y += player_bounding_box.height * 1.0
        offset_player_bounding_box.height *= 0.1
        # Correct the hole bounding box to make it easier to collide
        corrected_bounding_box = self.bounding_box.copy()
        corrected_bounding_box.inflate_ip(
            -corrected_bounding_box.width * 0.5, -corrected_bounding_box.height * 0.5
        )
        if screen:
            if self.visible:
                pygame.draw.rect(
                    screen,
                    (255, 0, 0) if self.enabled else (0, 0, 255),
                    corrected_bounding_box,
                    2,
                )
            pygame.draw.rect(screen, (255, 255, 0), offset_player_bounding_box, 2)
        collision = corrected_bounding_box.colliderect(offset_player_bounding_box)
        if not self.enabled:
            collision = False
        if collision:
            self.enabled = False
        return collision


def draw_gauge(screen, score, max_score, position, size, draw_text=True):
    """Draw a gauge bar.

    Args:
        screen (pygame.Surface): The pygame surface to draw on
        score (int): Current score
        max_score (int): Maximum score
        position (tuple): (x, y) position of the gauge
        size (tuple): (width, height) of the gauge
    """
    x, y = position
    width, height = size
    gauge_color = (255, 255, 0)  # yellow color

    # Draw the filled part of the gauge
    filled_width = width * min((score / max_score), 1)
    pygame.draw.rect(screen, (255, 69, 0), (x, y, filled_width, height))
    # Draw the gauge body
    pygame.draw.rect(screen, gauge_color, (x, y, width, height), 1)
    # Draw the current score text
    if draw_text:
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"{score}", True, (255, 255, 255))
        screen.blit(score_text, (x + width // 2 - 10, y + 2))


def launch_thirsty_lion(
    resolution=None,
    debug: bool = False,
    audio: bool = True,
    game_config: dict = DEFAULT_GAME_CONFIG,
    controller: List[str] = [KEYBOARD],
) -> dict:
    max_score = game_config.get(MAX_SCORE_WIN, 10)
    context = {}
    context = {WIN: False, SCORE: 0}
    screen = init_screen(resolution)
    toggle_audio(audio)
    key_debouncer = KeyDebouncer(cooldown_ms=200)
    winning_animation = False
    w, h = screen.get_width(), screen.get_height()
    f_factor = 10.0
    camera = Camera(
        x=0.0,
        y=4.0 * f_factor,
        z=0.0,
        focal_length=100.0 * f_factor,
        w=w,
        h=h,
        pitch=-18.0,
        yaw=0.0,
    )
    clock = pygame.time.Clock()
    running = True
    pause = False
    dt = 0
    speed = 2.0 * f_factor
    track_speed = 0.0
    # speed = 0.
    TRACK_WIDTH = 2.6 * f_factor
    CROP_TOP = 2.0 * f_factor
    Z_SOURCE = 30.0 * f_factor
    # Initialize rain manager

    rain_manager = RainManager(
        track_width=TRACK_WIDTH, track_depth=Z_SOURCE, camera=camera
    )
    WHEAT_COLOR = (245, 222, 179)
    score = 0
    moving_elements = []
    moving_tracks = []
    # Track setting
    moving_tracks += [
        MovingTrack(
            speed=track_speed,
            num_elements=50,
            z_source=Z_SOURCE * 1.5,
            xy_size=TRACK_WIDTH * 2,
            element_type=Floor,
            camera=camera,
        )
    ]

    for sign in [-1, 1]:
        moving_tracks.append(
            MovingTrack(
                speed=track_speed,
                num_elements=70,
                z_source=Z_SOURCE,
                x_source=sign * TRACK_WIDTH,
                randomness_amplitude=0,
                element_type=Wall,
                angle=sign * 5.0,
                xy_size=CROP_TOP,
                color=WHEAT_COLOR,
                camera=camera,
            )
        )
    for sign in [-1, 1]:
        CROP_TOP_SIZE = 200.0
        moving_tracks.append(
            MovingTrack(
                speed=track_speed,
                num_elements=50,
                y=CROP_TOP,
                z_source=Z_SOURCE,
                x_source=sign * (TRACK_WIDTH + CROP_TOP_SIZE / 2),
                xy_size=CROP_TOP_SIZE,
                element_type=Floor,
                color=WHEAT_COLOR,
                camera=camera,
            )
        )

    # Moving elements
    ROCK_SIZE = 0.5
    moving_elements.append(
        MovingElement(
            speed=speed,
            num_elements=3,
            y=0.0 * CROP_TOP,
            z_source=Z_SOURCE,
            x_range=[-TRACK_WIDTH * 0.6, TRACK_WIDTH * 0.6],
            xy_size=[ROCK_SIZE * CROP_TOP, ROCK_SIZE * CROP_TOP],
            z_size=0.0,
            element_type=Rock,
            color=(100, 100, 100),  # gray color
            camera=camera,
        )
    )
    if game_config[DIFFICULTY] > EASY:
        moving_elements.append(
            MovingElement(
                speed=speed,
                num_elements=10,
                y=0.0 * CROP_TOP,
                z_source=Z_SOURCE,
                x_range=[-TRACK_WIDTH * 0.6, TRACK_WIDTH * 0.6],
                xy_size=[0.2 * TRACK_WIDTH, 0.2 * TRACK_WIDTH],
                z_size=0.0,
                element_type=Hole,
                color=(255, 165, 0),  # orange color
                camera=camera,
            )
        )
    RESTART_HEIGHT = 10.0
    player_pos = 0.0, RESTART_HEIGHT, 50.0
    player = Lion(*player_pos, size=3.0, camera=camera)
    # shadow = Shadow(
    #     player.x, player.body_bottom, player.z, shadow_size=5.0, camera=camera
    # )  # looks like  a shadow
    current_background = "night_wheat_field"
    play_sound("chill_music", loop=1000)
    if WEBCAM in controller:
        from quatro.control.webcam import Controller

        body_control = Controller(
            webcam_show=False, allow_hand_control=False, allow_body_control=True
        )
        context["body_control"] = body_control
    while running:
        if KEYBOARD in controller:
            keys = pygame.key.get_pressed()
            running = handle_quit(keys, context)
        else:
            running = handle_quit([], context)
        draw_background_from_asset(screen, current_background)
        for moving_track in moving_tracks + moving_elements:
            moving_track.move(dt=dt)
            moving_track.draw(screen)
        if player.enabled:
            for reward_elements in moving_elements:
                for reward_element in reward_elements.elements:
                    if reward_element.collide(
                        player.bounding_box, screen=screen if debug else None
                    ):
                        score += reward_element.score_multiplier * 1
                        if reward_element.score_multiplier < 0:
                            player.y = RESTART_HEIGHT
                            play_sound("booing")
                        if reward_element.score_multiplier > 0:
                            play_sound("beep")
                            for _reward_element in reward_elements.elements:
                                if score >= 3 and score % 2 == 1:
                                    _reward_element.randomize_color()
                                else:
                                    _reward_element.standardize_color()

        # Draw black holes
        # shadow.x = player.x
        # shadow.y = 0.0
        # shadow.z = player.z
        # shadow.draw(screen)
        player.draw(screen, dt=dt)
        if debug:
            pygame.draw.rect(screen, (255, 0, 0), player.bounding_box, 1)

        draw_gauge(screen, score, max_score, position=(10, 10), size=(200, 30))

        # Game control update logic
        # Gravity in action!
        ground_level_player = 2.0 * player.size
        side_limit = TRACK_WIDTH - 1.5 * player.size

        if WEBCAM in controller:
            body_control.process_webcam()
            if body_control.current_position is not None:
                player.x = (body_control.current_position - 0.5) * 1.3 * TRACK_WIDTH
        if player.x < -side_limit:
            player.x = -side_limit
        if player.x > side_limit:
            player.x = side_limit
        if player.y > ground_level_player:
            player.enabled = False
            player.global_intensity = 0.0
            player.y -= 50.0 * dt
            if player.y < ground_level_player:
                player.y = ground_level_player
                player.global_intensity = 1.0
                player.enabled = True
        MAX_YAW = 30
        # Keyboard control
        # ----------------
        if KEYBOARD in controller:
            if keys[pygame.K_LEFT]:
                player.x -= speed / f_factor * 5.0 * dt
            if keys[pygame.K_RIGHT]:
                player.x += speed / f_factor * 5.0 * dt
            if keys[pygame.K_KP8]:
                camera.camera_position.y += 1.0 * f_factor * dt
            if keys[pygame.K_KP2]:
                camera.camera_position.y -= 1.0 * f_factor * dt
            if keys[pygame.K_PAGEDOWN]:
                camera.pitch += 20.0 * dt
            if keys[pygame.K_PAGEUP]:
                camera.pitch -= 20.0 * dt
            if keys[pygame.K_KP4] and camera.yaw < MAX_YAW:
                camera.yaw += 20.0 * dt
            if keys[pygame.K_KP6] and camera.yaw > -MAX_YAW:
                camera.yaw -= 20.0 * dt
            if key_debouncer.is_key_pressed(pygame.K_p, keys=keys):
                trigger_pause = True
            else:
                trigger_pause = False
        # Pause logic
        # ----------------
        if trigger_pause:
            pause = not pause
            pause_all_sounds(pause)
            for element in moving_tracks + moving_elements:
                element.toggle_pause(pause)
            for element in moving_elements:
                element.toggle_visibility(not pause)

        if pause:
            draw_text(screen, "PAUSE")

        player.toggle_pause(pause)

        # Win event
        # ----------------
        if score >= max_score:
            winning_animation = True
            moving_elements = []
            for element in moving_tracks:
                element.speed = 0.0

            player.enabled = False
        if winning_animation and not pause:
            player.z += 20.0 * dt
            draw_text(screen, f"____ WIN ____ \n  SCORE = {score} ")
            if player.z > 100.0:
                running = False
                context = {WIN: True, SCORE: score}

        # Update and draw rain
        if not pause:
            rain_manager.update(dt)
        rain_manager.draw(screen)

        pygame.display.flip()
        dt = clock.tick(60) / 1000
    stop_all_sounds()
    if WEBCAM in controller:
        body_control.release_resources()
    del screen
    return context
