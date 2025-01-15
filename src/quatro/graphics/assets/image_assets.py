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
    },
    "sunset_field_large": {
        PATH: BACKGROUND_ASSETS / "sunset_field_sideways.webp",
        DESCRIPTION: "DALL·E 2025-01-11 17.22.50 -A cartoon-style video game background designed for children"
        + " viewed from a sideways perspective. The scene features a picturesque wheat field with golden stalks"
        + "swaying gently under a vibrant sunset. On the side, a dense and vibrant forest with lush green trees"
        + "forms a natural border. The colorful gradient sky with orange, pink, and purple hues dominates the"
        + "background maintaining the serene and cheerful atmosphere. The perspective emphasizes depth, with"
        + "the wheat field and orest stretching into the horizon. The design is whimsical, vibrant, and playful, "
        + "with exaggerated and rounded features.",
        SIZE: (1792, 1024),
    },
    "night_wheat_field": {
        PATH: BACKGROUND_ASSETS / "night_field.webp",
        DESCRIPTION: "A mystical wheat field at night in an artistic style suitable for a video game. The scene features less saturated colors for a subdued and mysterious look. A wide pathway runs prominently through the middle of the field, inviting exploration. The golden wheat, now muted in tone, sways gently under the faint glow of the starry night sky, which is expansive and moonless. The atmosphere is darker and more mysterious, with distant silhouettes of trees and hills adding depth to the scene. The style remains immersive and detailed, ideal for a fantasy or exploration video game.",  # noqa
        SIZE: (1792, 1024),
    },
}

if __name__ == "__main__":
    assert all(
        [p[PATH].exists() for p in BACKGROUNDS.values()]
    ), "Background assets not found"
