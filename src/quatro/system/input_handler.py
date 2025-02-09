import pygame


class KeyDebouncer:
    def __init__(self, cooldown_ms: int = 200):
        self.cooldown_ms = cooldown_ms
        self.last_press_times = {}

    def is_key_pressed(self, key: pygame.key, keys: dict = None) -> bool:
        """Check if a key is pressed with debounce protection."""
        if keys is None:
            keys = pygame.key.get_pressed()
        if not keys[key]:
            return False

        current_time = pygame.time.get_ticks()
        last_time = self.last_press_times.get(key, 0)

        if current_time - last_time > self.cooldown_ms:
            self.last_press_times[key] = current_time
            return True
        return False
