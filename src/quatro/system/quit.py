import pygame
QUIT = "quit"


def handle_quit(keys: dict, context: dict) -> bool:
    running = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if keys[pygame.K_ESCAPE] or keys[pygame.K_q]:
        running = False
    context[QUIT] = not running
    return running
