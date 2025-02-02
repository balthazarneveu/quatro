import pygame
from quatro.sound.assets.sound_assets import SOUNDS, PATH

ALL_SOUNDS = list(SOUNDS.keys())


def play_sound(sound_name: str) -> None:
    """Play a sound from the sound assets

    Args:
        sound_name (str): Name of the sound to play
    """
    assert sound_name in ALL_SOUNDS, f"Sound not found: {sound_name}"
    sound_path = SOUNDS[sound_name][PATH]
    sound = pygame.mixer.Sound(sound_path)
    sound.play()
