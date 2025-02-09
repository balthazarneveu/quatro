import pygame
from quatro.graphics.background import draw_background_from_asset
from quatro.sound.sound import play_sound, toggle_audio
from quatro.system.input_handler import KeyDebouncer

from quatro.graphics.animation.bunny import Bunny, Shadow
from quatro.system.quit import handle_quit
from quatro.system.window import init_screen
from quatro.engine.planes import Floor, Wall, FacingWall
from quatro.engine.endless_track import MovingTrack, MovingElement
from quatro.engine.pinhole_camera import Camera
from math import sin, radians


def draw_pause_text(screen):
    """Draw 'Pause' text on the screen."""
    font = pygame.font.SysFont(None, 72)
    pause_text = font.render("Pause", True, (255, 255, 255))
    text_rect = pause_text.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2)
    )
    screen.blit(pause_text, text_rect)


class Carrot(FacingWall):
    def __init__(self, *args, score_multiplier=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.score_multiplier = score_multiplier

    def get_coordinates(self):
        pts_3d = super().get_coordinates()
        top = (pts_3d[0] + pts_3d[1]) / 2.0
        br, bl = pts_3d[2], pts_3d[3]
        pts_3d_triangle = pts_3d[:2] + [(br + bl) / 2.0]
        geometry = [
            {
                "type": "poly",
                "content": {"points": pts_3d_triangle, "color": self.color},
            }
        ]
        for angle in [-20, 20]:
            leaf_size = self.xy_size[1] * 0.7
            leaf = {
                "type": "ellipse",
                "content": {
                    "color": (0, 100, 0),  # dark green color
                    "center": top
                    + pygame.Vector3(
                        sin(radians(-angle)) * leaf_size / 2.0, leaf_size / 2.0, 0
                    ),
                    "size_x": leaf_size * 0.2,
                    "size_y": leaf_size,
                    "angle": angle,
                    "width": 0,
                },
            }
            geometry.append(leaf)
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


def draw_carrot_gauge(screen, score, max_score, position, size, draw_text=True):
    """Draw a carrot-shaped gauge bar.

    Args:
        screen (pygame.Surface): The pygame surface to draw on
        score (int): Current score
        max_score (int): Maximum score
        position (tuple): (x, y) position of the gauge
        size (tuple): (width, height) of the gauge
    """
    x, y = position
    width, height = size
    carrot_color = (255, 165, 0)  # orange color with transparency

    # Draw the filled part of the gauge
    filled_width = width * min((score / max_score), 1)
    pygame.draw.rect(screen, (255, 69, 0), (x, y, filled_width, height))
    # Draw the carrot body
    pygame.draw.rect(screen, carrot_color, (x, y, width, height), 1)
    # Draw the current score text
    if draw_text:
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"{score}", True, (255, 255, 255))
        screen.blit(score_text, (x + width // 2 - 10, y + 2))


def launch_running_bunny(
    resolution=None, debug: bool = False, audio: bool = True
) -> dict:
    context = {}
    screen = init_screen(resolution)
    toggle_audio(audio)
    key_debouncer = KeyDebouncer(cooldown_ms=200)
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
    TRACK_WIDTH = 2.6 * f_factor
    CROP_TOP = 2.0 * f_factor
    Z_SOURCE = 30.0 * f_factor
    WHEAT_COLOR = (245, 222, 179)
    score = 0
    max_score = 10  # Set the maximum score for the gauge
    moving_elements = []
    moving_tracks = []
    moving_tracks += [
        MovingTrack(
            speed=speed,
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
                speed=speed,
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
                speed=speed,
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

    moving_elements.append(
        MovingElement(
            speed=speed,
            num_elements=10,
            y=0.0 * CROP_TOP,
            z_source=Z_SOURCE,
            x_range=[-TRACK_WIDTH * 0.6, TRACK_WIDTH * 0.6],
            xy_size=[0.1 * TRACK_WIDTH, 0.3 * CROP_TOP],
            z_size=0.0,
            element_type=Carrot,
            color=(255, 165, 0),  # orange color
            camera=camera,
        )
    )
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
    player = Bunny(*player_pos, size=5.0, animation_speed=10, camera=camera)
    shadow = Shadow(
        player.x, player.body_bottom, player.z, shadow_size=5.0, camera=camera
    )  # looks like  a shadow
    current_background = "night_wheat_field"
    play_sound("chill_music", loop=1000)
    while running:
        keys = pygame.key.get_pressed()
        running = handle_quit(keys, context)
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

        # Draw black holes
        shadow.x = player.x
        shadow.y = 0.0
        shadow.z = player.z
        shadow.draw(screen)
        player.draw(screen, dt=dt)
        if debug:
            pygame.draw.rect(screen, (255, 0, 0), player.bounding_box, 1)

        draw_carrot_gauge(screen, score, max_score, position=(10, 10), size=(200, 30))

        # Game control update logic
        # Gravity in action!
        ground_level_player = 2.0 * player.size
        side_limit = TRACK_WIDTH - 1.5 * player.size
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
        if keys[pygame.K_LEFT]:
            player.x -= speed / f_factor * 5.0 * dt

        if keys[pygame.K_RIGHT]:
            player.x += speed / f_factor * 5.0 * dt
        MAX_YAW = 30
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
            pause = not pause
            for element in moving_tracks + moving_elements:
                element.toggle_pause(pause)
            for element in moving_elements:
                element.toggle_visibility(not pause)

        if pause:
            draw_pause_text(screen)
        player.toggle_pause(pause)
        pygame.display.flip()

        dt = clock.tick(60) / 1000
    return context
