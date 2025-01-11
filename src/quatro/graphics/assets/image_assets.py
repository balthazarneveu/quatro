from pathlib import Path

ASSET_FOLDER = Path(__file__).parent.parent.parent.parent.parent / "assets"
assert ASSET_FOLDER.exists(), f"Asset folder not found: {ASSET_FOLDER}"
PATH = "path"
DESCRIPTION = "description"
BACKGROUND_ASSETS = ASSET_FOLDER / "backgrounds"
SIZE = "size"
BACKGROUNDS = {
    "sunset_field": {
        PATH: BACKGROUND_ASSETS / "sunset_field.webp",
        DESCRIPTION: "DALL·E 2025-01-11 17.02.16 - A cartoon-style video game background designed for children"
        + ", featuring a picturesque wheat field with golden stalks swaying gently under a vibrant sun.webp",
        SIZE: (1792, 1024),
    }
}

if __name__ == "__main__":
    assert all(
        [p[PATH].exists() for p in BACKGROUNDS.values()]
    ), "Background assets not found"
