import pygame
import math
from quatro.control.properties import KEYBOARD, WEBCAM
from quatro.graphics.background import draw_background_from_asset
from quatro.graphics.assets.image_assets import SPRITES, PATH
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
from quatro.system.performance_tracker import PerformanceTracker
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
        moving_elements: List[MovingElement] = None,
        score_multiplier: float = 0.01,
    ):
        self.track_width = track_width
        self.rainfall_width = self.track_width / 8.0 * 2.0
        self.track_depth = track_depth
        self.camera = camera
        self.moving_elements = moving_elements
        self.raindrops: List[Raindrop] = []
        self.delay = 4.0
        self.spawn_timer = 0
        self.spawn_interval = 0.05  # Time between raindrop spawns
        self.fall_speed = 12.0  # Speed at which raindrops fall
        self.sample_rainfall_location()
        self.score_multiplier = score_multiplier
        self.enabled = True

    def sample_rainfall_location(self):
        self.rainfall_location = random.uniform(
            -self.track_width / 2, self.track_width / 2
        )

    def update(self, dt: float):
        self.spawn_timer += dt
        if self.delay is not None:
            if self.spawn_timer >= self.delay:
                self.reset()
                self.delay = None
            return
        if self.total_drops_spawned > 50:  # Limit the number of active raindrops
            self.disable()

        if (
            not self.enabled and len(self.raindrops) < 40
        ):  # All raindrops have fallen -> reset
            self.sample_rainfall_location()
            self.reset()

        # Update spawn timer

        if self.enabled and self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_raindrop()

        # Update raindrop positions and remove ones that hit the ground
        for drop in self.raindrops[:]:
            drop.y -= self.fall_speed * dt
            if drop.y <= 0:  # Ground level
                self.raindrops.remove(drop)

    def disable(self):
        self.enabled = False

    def reset(self):
        play_sound("rainfall")
        self.total_drops_spawned = 0
        self.enabled = True

    def spawn_raindrop(self):
        # Random position across track width
        self.total_drops_spawned += 1
        x = self.rainfall_location + random.uniform(
            -self.rainfall_width, self.rainfall_width
        )
        # Start high above
        y = 50.0  # Height above ground
        # Random position along track depth
        # z = random.uniform(0, self.track_depth)
        # z = 0.2 * self.track_depth
        z = 50 + random.uniform(-15, 0)
        new_drop = Raindrop(
            x=x,
            y=y,
            z=z,
            xy_size=(0.5, 0.8),  # Size of raindrop
            color=[100, 100, 255],  # Blue color
            camera=self.camera,
            score_multiplier=self.score_multiplier,
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

        # Create oscillations based on z position
        import math

        phase = self.z * 0.2 * 4.0
        # Detail dot oscillation
        detail_oscillation = math.sin(phase) * self.xy_size[1] * 0.5 * 0.95

        # Create bumpy road effect with multiple frequencies and phases
        # Main bumps
        bump_y = (
            math.sin(self.z * 0.3) * self.xy_size[1] * 0.15  # Medium frequency
            + math.sin(self.z * 1.2 + 0.5) * self.xy_size[1] * 0.08  # High frequency
            + math.sin(self.z * 0.1 - 0.3) * self.xy_size[1] * 0.1  # Low frequency
        ) * 0.1

        bump_x = (
            math.cos(self.z * 0.4) * self.xy_size[0] * 0.08  # Medium frequency
            + math.cos(self.z * 0.9 + 0.7) * self.xy_size[0] * 0.05  # Higher frequency
            + math.sin(self.z * 0.15 + 1.1) * self.xy_size[0] * 0.04  # Low frequency
        ) * 0.1

        # Add some extra jitter based on position
        jitter_x = math.sin(self.z * 2.5) * self.xy_size[0] * 0.02
        jitter_y = math.cos(self.z * 2.8) * self.xy_size[1] * 0.02

        # Apply the bumpy movement to the rock position
        bumpy_pos = pygame.Vector3(
            top.x + bump_x + jitter_x, top.y + bump_y + jitter_y, top.z
        )

        geometry = [
            {
                "type": "ellipse",
                "content": {
                    "color": self.color,  # gray color for the rock
                    "center": bumpy_pos,
                    "size_x": self.xy_size[0],
                    "size_y": self.xy_size[1],
                    "angle": 0,
                    "width": 0,
                },
            }
        ]

        # Only add the detail when it's "visible" (in front of the rock)
        if math.cos(phase) > 0:
            # Apply the same bumpy movement to the detail
            detail_pos = pygame.Vector3(
                bumpy_pos.x, bumpy_pos.y + detail_oscillation, bumpy_pos.z
            )
            geometry.append(
                {
                    "type": "ellipse",
                    "content": {
                        "color": [
                            max(c - 30, 0) for c in self.color
                        ],  # darker shade for detail
                        "center": detail_pos,
                        "size_x": self.xy_size[0] * 0.1,
                        "size_y": self.xy_size[1] * 0.1,
                        "angle": 0,
                        "width": 0,
                    },
                }
            )
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
    def __init__(self, *args, score_multiplier=0.01, **kwargs):
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


class SmashEffect:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.active = False
        self.zoom_duration = 0.15  # Duration of initial zoom
        self.stick_duration = 1.0  # Duration to stay in place
        self.slide_duration = 1.5  # Duration of sliding down
        self.total_duration = (
            self.zoom_duration + self.stick_duration + self.slide_duration
        )
        self.timer = 0
        self.sprite_path = SPRITES["lion_smash"][PATH]
        self.original_sprite = pygame.image.load(str(self.sprite_path))

        # Calculate target size
        scale_factor = 0.8
        self.target_width = int(screen_width * scale_factor)
        self.target_height = int(screen_height * scale_factor)
        orig_width, orig_height = self.original_sprite.get_size()
        self.aspect_ratio = orig_width / orig_height
        if self.target_width / self.target_height > self.aspect_ratio:
            self.target_width = int(self.target_height * self.aspect_ratio)
        else:
            self.target_height = int(self.target_width / self.aspect_ratio)

        # Setup decorative stars
        self.num_stars = 6
        self.stars = []
        self.star_radius = (
            min(self.target_width, self.target_height) * 0.15
        )  # Orbit radius
        self.star_size = min(self.target_width, self.target_height) * 0.05  # Star size
        self.star_spin_speed = 0.8  # Rotations per second (slowed down)
        for i in range(self.num_stars):
            angle = (i / self.num_stars) * 2 * math.pi
            star_points = []
            for j in range(10):
                point_angle = (j * 2 * math.pi / 10) + math.pi / 2  # Start from top
                radius = self.star_size if j % 2 == 0 else self.star_size * 0.4
                x = math.cos(point_angle) * radius
                y = math.sin(point_angle) * radius
                star_points.append((x, y))
            self.stars.append({"base_angle": angle, "points": star_points})

        # Create target sized sprite
        self.sprite = pygame.transform.scale(
            self.original_sprite, (self.target_width, self.target_height)
        )

        # Center position
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2
        self.initial_y = (screen_height - self.target_height) // 2

    def _generate_star_points(self, size):
        points = []
        for i in range(10):
            angle = (i * 2 * math.pi / 10) + math.pi / 2  # Start from top
            radius = size if i % 2 == 0 else size * 0.4
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            points.append((x, y))
        return points

    def _draw_stars(self, screen, center_x, center_y, scale=1.0):
        # Draw spinning stars in an elliptical orbit above the sprite
        sprite_top = center_y - (
            self.target_height * scale * 0.4
        )  # Position above the sprite

        for i in range(6):  # Draw 6 stars
            # Calculate star position on elliptical orbit
            base_angle = (i / 6) * 2 * math.pi
            angle = base_angle + self.timer * 0.8 * 2 * math.pi  # Slower rotation

            # Elliptical orbit (wider than it is tall)
            horizontal_radius = (
                min(self.target_width, self.target_height) * 0.25 * scale
            )
            vertical_radius = horizontal_radius * 0.4  # Flattened for perspective

            # Calculate position on ellipse
            star_x = center_x + math.cos(angle) * horizontal_radius
            star_y = sprite_top + math.sin(angle) * vertical_radius

            # Adjust star size based on position (smaller in back, larger in front)
            base_size = min(self.target_width, self.target_height) * 0.05 * scale
            size_scale = 0.7 + (
                math.sin(angle) * 0.3
            )  # Stars are smaller when "behind"
            star_size = base_size * size_scale

            # Generate and draw star
            star_points = []
            for j in range(10):
                point_angle = (j * 2 * math.pi / 10) + math.pi / 2
                radius = star_size if j % 2 == 0 else star_size * 0.4
                x = star_x + math.cos(point_angle) * radius
                y = star_y + math.sin(point_angle) * radius
                star_points.append((x, y))

            if len(star_points) >= 3:
                # Adjust star brightness based on position (dimmer in back)
                brightness = int(200 + (55 * math.sin(angle)))  # Range from 200-255
                star_color = (
                    brightness,
                    brightness,
                    0,
                )  # Yellow with varying brightness
                pygame.draw.polygon(screen, star_color, star_points)

    def start(self):
        self.active = True
        self.timer = 0
        self.y = self.initial_y

    def is_finished(self):
        return not self.active or self.timer >= self.total_duration

    def get_current_scale(self):
        if self.timer <= self.zoom_duration:
            # Start from 10% size and zoom to full size
            progress = self.timer / self.zoom_duration
            # Use ease-out quad for smooth deceleration
            progress = -(progress * (progress - 2))
            return 0.1 + (1.0 - 0.1) * progress
        return 1.0

    def update(self, dt):
        if not self.active:
            return

        self.timer += dt

        # First phase: zoom and stick
        if self.timer <= self.stick_duration + self.zoom_duration:
            return

        # Second phase: slide down
        slide_time = self.timer - (self.stick_duration + self.zoom_duration)
        if slide_time < self.slide_duration:
            # Accelerating slide using quadratic easing
            progress = slide_time / self.slide_duration
            slide_factor = progress * progress  # Quadratic easing
            total_slide = self.screen_height - self.initial_y
            self.y = self.initial_y + (total_slide * slide_factor)
        else:
            self.active = False

    def _init_stars(self):
        if not hasattr(self, "stars"):
            # Setup decorative stars
            self.num_stars = 6
            self.stars = []
            self.star_radius = (
                min(self.target_width, self.target_height) * 0.15
            )  # Orbit radius
            self.star_size = (
                min(self.target_width, self.target_height) * 0.05
            )  # Star size
            self.star_spin_speed = 2.0  # Rotations per second
            for i in range(self.num_stars):
                angle = (i / self.num_stars) * 2 * math.pi
                self.stars.append(
                    {
                        "base_angle": angle,
                        "points": self._generate_star_points(self.star_size),
                    }
                )

    def draw(self, screen):
        if not self.active:
            return

        # Get current scale for zoom effect
        scale = self.get_current_scale()
        current_width = int(self.target_width * scale)
        current_height = int(self.target_height * scale)

        # Scale sprite to current size
        if scale != 1.0:
            current_sprite = pygame.transform.scale(
                self.sprite, (current_width, current_height)
            )
        else:
            current_sprite = self.sprite

        # Calculate position to center the sprite
        x = self.center_x - current_width // 2
        y = self.center_y - current_height // 2

        if self.timer > self.zoom_duration:
            y = self.y  # Use sliding y position after zoom

        # Calculate opacity
        if self.timer <= self.stick_duration + self.zoom_duration:
            # Full opacity during zoom and stick phase
            alpha = 255
            # Draw stars during stick phase (but not during initial zoom)
            if self.timer >= self.zoom_duration:
                self._draw_stars(screen, self.center_x, y + current_height // 2, scale)
        else:
            # Fade out during slide phase
            slide_progress = (
                self.timer - (self.stick_duration + self.zoom_duration)
            ) / self.slide_duration
            alpha = int(
                255 * (1 - slide_progress * 0.7)
            )  # Keep some visibility while sliding

        current_sprite.set_alpha(alpha)
        screen.blit(current_sprite, (int(x), int(y)))

        # Draw stars throughout the effect until fading starts
        if (
            self.timer >= self.zoom_duration
            and self.timer <= self.stick_duration + self.zoom_duration
        ):
            self._draw_stars(screen, self.center_x, y + current_height // 2, scale)


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


def draw_gauge(screen, score, max_score, position, size, draw_text=False):
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
    pygame.draw.rect(
        screen, (30, 144, 255), (x, y, filled_width, height)
    )  # Dodger Blue
    # Draw the gauge body
    pygame.draw.rect(screen, gauge_color, (x, y, width, height), 1)
    # Draw the current score text
    if draw_text:
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"{score:.1f}", True, (255, 255, 255))
        screen.blit(score_text, (x + width // 2 - 10, y + 2))


def launch_thirsty_lion(
    resolution=None,
    debug: bool = False,
    audio: bool = True,
    game_config: dict = DEFAULT_GAME_CONFIG,
    controller: List[str] = [KEYBOARD],
    log_performance: bool = False,
) -> dict:
    if log_performance:
        performance_tracker = PerformanceTracker()
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

    TRACK_WIDTH = 2.6 * f_factor * 0.5
    CROP_TOP = 2.0 * f_factor
    Z_SOURCE = 30.0 * f_factor * 0.25
    # Initialize managers and effects
    score = 0
    moving_elements = []
    moving_tracks = []
    smash_effect = SmashEffect(w, h)

    rain_manager = RainManager(
        track_width=TRACK_WIDTH,
        track_depth=Z_SOURCE,
        camera=camera,
        moving_elements=moving_elements,
        score_multiplier=0.1,
    )
    if False:
        track_speed = 0.0
        speed = 0.0
        WHEAT_COLOR = (245, 222, 179)
        CROP_TOP_SIZE = 200.0
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
    ROCK_SIZE = 0.5 * 0.7
    moving_elements.append(
        MovingElement(
            speed=speed,
            num_elements=3,
            y=0.0 * CROP_TOP,
            z_source=Z_SOURCE,
            z_far_away=Z_SOURCE,
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
    RESTART_HEIGHT = 40.0
    player_pos = 0.0, RESTART_HEIGHT, 50.0
    player = Lion(*player_pos, size=3.0, camera=camera)
    player.hit_timer = 0  # Timer for hit state
    player.is_hit = False  # Whether the lion is in hit state
    player.hit_stick_duration = 0.2  # How long to stick in place after hit
    player.hit_fall_speed = 20.0  # Base fall speed after being hit
    # shadow = Shadow(
    #     player.x, player.body_bottom, player.z, shadow_size=5.0, camera=camera
    # )  # looks like  a shadow
    current_background = "jungle_volcano"
    play_sound("groovy_shake", loop=1000)
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
        # player.set_action("idle")
        if hasattr(player, "can_collide") and player.can_collide:
            for rain_drop in rain_manager.raindrops:
                if rain_drop.collide(
                    player.bounding_box, screen=screen if debug else None
                ):
                    # player.set_action("drinking")
                    score += rain_drop.score_multiplier * 1
            for reward_elements in moving_elements:
                for reward_element in reward_elements.elements:
                    if reward_element.collide(
                        player.bounding_box, screen=screen if debug else None
                    ):
                        score += reward_element.score_multiplier * 1
                        if reward_element.score_multiplier < 0:
                            player.y = RESTART_HEIGHT
                            play_sound("rock_hits_lion")
                            player.set_action("dizzy")
                            smash_effect.start()  # Start the smash effect animation
                            player.is_hit = True  # Enter hit state
                            player.hit_timer = 0  # Reset hit timer
                            player.enabled = False  # Hide the lion
                        if reward_element.score_multiplier > 0:
                            play_sound("rainfall")
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
        if score < 0:
            score = 0
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
            player.can_collide = (
                False  # Use this for gameplay mechanics instead of enabled
            )

            if player.is_hit:
                # Only start falling after smash effect is done
                if smash_effect.is_finished():
                    # Make the lion visible again
                    player.enabled = True
                    # Start falling with increasing speed after smash effect
                    player.hit_timer += dt
                    falling_speed = player.hit_fall_speed * (
                        1 + player.hit_timer * 2
                    )  # Accelerate the fall
                    player.y -= falling_speed * dt
            else:
                # Normal landing behavior
                landing_speed = max(
                    10.0, 80.0 * (player.y - ground_level_player) / RESTART_HEIGHT
                )
                player.y -= landing_speed * dt

            if player.y < ground_level_player:
                player.y = ground_level_player
                player.enabled = True  # Make sure lion is visible
                player.can_collide = True
                player.is_hit = False  # Reset hit state
                player.set_action("idle")
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
            play_sound("roars")
            winning_animation = True
            moving_elements = []
            for element in moving_tracks:
                element.speed = 0.0
                element.disable()

            player.can_collide = False  # Disable collisions but keep visible
        if winning_animation and not pause:
            player.z += 10.0 * dt
            draw_text(screen, f"____ WIN ____ \n  SCORE = {score:.1f} ")
            if player.z > 100.0:
                running = False
                context = {WIN: True, SCORE: score}

        # Update and draw rain and effects
        if not pause:
            rain_manager.update(dt)
            smash_effect.update(dt)
        rain_manager.draw(screen)
        smash_effect.draw(screen)

        # Track FPS
        if log_performance:
            performance_tracker.track_performance()

        pygame.display.flip()
        dt = clock.tick(60) / 1000
    stop_all_sounds()
    if WEBCAM in controller:
        body_control.release_resources()
    del screen
    return context
