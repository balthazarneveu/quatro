from pathlib import Path

ASSET_FOLDER = Path(__file__).parent.parent.parent.parent.parent / "assets"
assert ASSET_FOLDER.exists(), f"Asset folder not found: {ASSET_FOLDER}"
PATH = "path"
DESCRIPTION = "description"
SOUNDS = {
    "booing": {
        PATH: ASSET_FOLDER / "sounds" / "booing.wav",
    },
    "shimmer_win": {
        PATH: ASSET_FOLDER / "sounds" / "shimmer_win.wav",
    },
    "beep": {
        PATH: ASSET_FOLDER / "sounds" / "beep.wav",
    },
    "win": {
        PATH: ASSET_FOLDER / "sounds" / "win.wav",
    },
    "bounce": {
        PATH: ASSET_FOLDER / "sounds" / "bounce.wav",
    },
    "chill_music": {
        PATH: ASSET_FOLDER / "sounds" / "chill_music.mp3",
    },
    "groovy_shake": {
        PATH: ASSET_FOLDER / "sounds" / "groovy_shake.mp3",
    },
    "rock_hits_lion": {
        PATH: ASSET_FOLDER / "sounds" / "rock_hits_lion.wav",
    },
    "rainfall": {
        PATH: ASSET_FOLDER / "sounds" / "rainfall.wav",
    },
    "roars": {
        PATH: ASSET_FOLDER / "sounds" / "lion_roars.wav",
    },
}

if __name__ == "__main__":
    assert all(
        [p[PATH].exists() for p in SOUNDS.values()]
    ), "Background assets not found"
