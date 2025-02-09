import pygame
from quatro.sound.assets.sound_assets import SOUNDS, PATH
from typing import Dict

mute = False
ALL_SOUNDS = list(SOUNDS.keys())
active_sounds: Dict[pygame.mixer.Sound, float] = {}


def toggle_audio(audio: bool = True) -> None:
    """Mute/Enable all sounds"""
    global mute
    mute = not audio


def play_sound(sound_name: str, loop: int = 0) -> None:
    """Play a sound from the sound assets

    Args:
        sound_name (str): Name of the sound to play
        loop (int): Number of times to loop the sound (-1 for infinite)
    """
    global mute, active_sounds
    if mute:
        return
    assert sound_name in ALL_SOUNDS, f"Sound not found: {sound_name}"
    sound_path = SOUNDS[sound_name][PATH]
    sound = pygame.mixer.Sound(sound_path)
    sound.play(loops=loop)
    active_sounds[sound_name] = sound


def pause_all_sounds(pause: bool = True) -> None:
    """Pause or unpause all currently playing sounds"""
    if pause:
        pygame.mixer.pause()
    else:
        pygame.mixer.unpause()


def resume_all_sounds() -> None:
    """Resume all paused sounds"""
    pygame.mixer.unpause()


def stop_all_sounds() -> None:
    """Stop all currently playing sounds"""
    pygame.mixer.stop()
