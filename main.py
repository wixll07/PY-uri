"""PYuri - an endless 2D platform game built with Pygame."""

from __future__ import annotations

import random
import re
from pathlib import Path

import pygame
from pygame.locals import (
    K_DOWN,
    K_ESCAPE,
    K_r,
    K_s,
    K_UP,
    K_z,
    KEYDOWN,
    QUIT,
    RESIZABLE,
)


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
AUDIO_DIR = ASSETS_DIR / "audio"

PLAYER_ANIMATIONS_DIR = IMAGES_DIR / "animations" / "player"
SNAIL_ANIMATIONS_DIR = IMAGES_DIR / "animations" / "enemies" / "snail"
COINS_DIR = IMAGES_DIR / "animations" / "items" / "coins"


def natural_sort_key(path: Path) -> list[object]:
    """Sort filenames containing numbers in human order: 1, 2, 10."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def load_images(folder: Path) -> list[pygame.Surface]:
    """Load every supported image from a folder in natural filename order."""
    supported_extensions = {".png", ".jpg", ".jpeg"}
    image_paths = sorted(
        (path for path in folder.iterdir() if path.suffix.lower() in supported_extensions),
        key=natural_sort_key,
    )

    if not image_paths:
        raise FileNotFoundError(f"No images found in: {folder}")

    return [pygame.image.load(path).convert_alpha() for path in image_paths]


# ---------------------------------------------------------------------------
# Pygame setup
# ---------------------------------------------------------------------------
pygame.init()
pygame.mixer.init()

WINDOW_SIZE = (696, 400)
WORLD_SIZE = (1920, 688)
FLOOR_HEIGHTS = [580, 460, 340]
FPS = 60

window = pygame.display.set_mode(WINDOW_SIZE, RESIZABLE)
pygame.display.set_caption("PYuri")
clock = pygame.time.Clock()
world = pygame.Surface(WORLD_SIZE)
font = pygame.font.SysFont(None, 36)

world_width, world_height = WORLD_SIZE


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------
background = pygame.image.load(IMAGES_DIR / "backgrounds" / "map.png").convert()
background = pygame.transform.scale(background, WORLD_SIZE)
background_width = background.get_width()

stand_images = load_images(PLAYER_ANIMATIONS_DIR / "stand")
run_images = load_images(PLAYER_ANIMATIONS_DIR / "run")
jump_images = load_images(PLAYER_ANIMATIONS_DIR / "jump")
crouch_images = load_images(PLAYER_ANIMATIONS_DIR / "crouch")
kick_images = load_images(PLAYER_ANIMATIONS_DIR / "kick")
dead_images = load_images(PLAYER_ANIMATIONS_DIR / "dead")
coin_images = load_images(COINS_DIR)
snail_images = load_images(SNAIL_ANIMATIONS_DIR / "walk")
snail_death_images = load_images(SNAIL_ANIMATIONS_DIR / "death")
coin_counter_image = pygame.image.load(IMAGES_DIR / "ui" / "coin_counter.png").convert_alpha()

pygame.mixer.music.load(AUDIO_DIR / "music" / "background_music.mp3")
pygame.mixer.music.set_volume(0.0)
pygame.mixer.music.play(-1)

start_sound = pygame.mixer.Sound(AUDIO_DIR / "sfx" / "start.mp3")
jump_sound = pygame.mixer.Sound(AUDIO_DIR / "sfx" / "jump.mp3")
crouch_sound = pygame.mixer.Sound(AUDIO_DIR / "sfx" / "crouch.mp3")
death_sound = pygame.mixer.Sound(AUDIO_DIR / "sfx" / "death.mp3")
coin_sound = pygame.mixer.Sound(AUDIO_DIR / "sfx" / "coin.mp3")
run_sound = pygame.mixer.Sound(AUDIO_DIR / "sfx" / "run.mp3")
crouch_sound.set_volume(1.0)


# ---------------------------------------------------------------------------
# World generation
# ---------------------------------------------------------------------------
def generate_platform(start_x: int, previous_floor: int) -> tuple[pygame.Rect, int]:
    width = random.randint(200, 600)
    horizontal_gap = random.randint(150, 400)
    previous_index = FLOOR_HEIGHTS.index(previous_floor)

    candidates = [previous_floor]
    if previous_index > 0:
        candidates.append(FLOOR_HEIGHTS[previous_index - 1])
    if previous_index < len(FLOOR_HEIGHTS) - 1:
        candidates.append(FLOOR_HEIGHTS[previous_index + 1])

    floor_y = random.choice(candidates)
    return pygame.Rect(start_x + horizontal_gap, floor_y, width, 20), floor_y


def create_initial_platforms() -> list[pygame.Rect]:
    platforms: list[pygame.Rect] = []
    generated_x = 0
    floor_y = FLOOR_HEIGHTS[0]

    for index in range(8):
        if index == 0:
            platform = pygame.Rect(generated_x, floor_y, 1000, 20)
        else:
            platform, floor_y = generate_platform(generated_x, floor_y)

        platforms.append(platform)
        generated_x = platform.right

    return platforms


def generate_coins_and_enemies(
    platforms: list[pygame.Rect],
) -> tuple[list[pygame.Rect], list[pygame.Rect]]:
    coins: list[pygame.Rect] = []
    enemies: list[pygame.Rect] = []

    for platform in platforms:
        if random.random() < 0.4:
            coins.append(pygame.Rect(platform.centerx, platform.top - 30, 30, 30))
        if random.random() < 0.3:
            enemies.append(pygame.Rect(platform.right - 40, platform.top - 40, 40, 40))

    return coins, enemies


def play_start_sound() -> None:
    if not start_sound.get_num_channels():
        start_sound.play()


def show_game_over() -> None:
    overlay = pygame.Surface(window.get_size())
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)
    window.blit(overlay, (0, 0))

    text = font.render("GAME OVER", True, (255, 0, 0))
    window.blit(text, (window.get_width() // 2 - text.get_width() // 2, 100))

    for image in dead_images:
        window.blit(image, image.get_rect(center=window.get_rect().center))
        pygame.display.flip()
        pygame.time.wait(150)

    pygame.time.wait(1000)


best_record = 0


def play_game() -> bool:
    """Run one game session. Return True to restart, False to quit."""
    global best_record

    platforms = create_initial_platforms()
    coins, enemies = generate_coins_and_enemies(platforms)

    player_image = stand_images[0]
    player_rect = player_image.get_rect(x=100, y=0)

    vertical_speed = 0
    gravity = 1
    remaining_jumps = 2
    image_index = 0
    frame_timer = 0
    animation_speed = 6
    crouching = False

    snail_index = 0
    snail_timer = 0
    snail_speed = 8

    coin_index = 0
    coin_timer = 0
    coin_speed = 8

    scroll_x = 0.0
    scroll_speed = 5.0
    distance = 0.0
    coin_score = 0
    paused = False

    play_start_sound()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    paused = not paused
                elif not paused and event.key in (K_UP, K_z) and remaining_jumps > 0:
                    vertical_speed = -20
                    remaining_jumps -= 1
                    image_index = 0
                    frame_timer = 0
                    jump_sound.play()
                elif not paused and event.key in (K_DOWN, K_s):
                    crouching = True
                    image_index = 0
                    frame_timer = 0
                    crouch_sound.play()
                elif event.key == K_r:
                    return True

        if paused:
            overlay = pygame.Surface(window.get_size())
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            window.blit(overlay, (0, 0))

            pause_title = font.render("PAUSE", True, (255, 255, 255))
            resume_text = font.render("Press ESC to resume", True, (200, 200, 200))
            window.blit(pause_title, pause_title.get_rect(center=(window.get_width() // 2, 110)))
            window.blit(resume_text, resume_text.get_rect(center=(window.get_width() // 2, 165)))
            pygame.display.flip()
            clock.tick(FPS)
            continue

        vertical_speed += gravity
        player_rect.y += vertical_speed

        standing_on_platform = False
        for platform in platforms:
            visible_platform = platform.move(-scroll_x, 0)
            if player_rect.colliderect(visible_platform) and vertical_speed >= 0:
                player_rect.bottom = visible_platform.top
                vertical_speed = 0
                remaining_jumps = 2
                standing_on_platform = True
                break

        for enemy in enemies[:]:
            visible_enemy = enemy.move(-scroll_x, 0)
            if player_rect.colliderect(visible_enemy):
                if crouching:
                    enemies.remove(enemy)
                else:
                    death_sound.play()
                    show_game_over()
                    return True

        for coin in coins[:]:
            visible_coin = coin.move(-scroll_x, 0)
            if player_rect.colliderect(visible_coin):
                coins.remove(coin)
                coin_score += 1
                coin_sound.play()

        if not standing_on_platform and player_rect.y > world_height:
            death_sound.play()
            show_game_over()
            return True

        scroll_speed += 0.001
        scroll_x += scroll_speed
        distance += scroll_speed / 50
        best_record = max(best_record, int(distance))

        if platforms[-1].right - scroll_x < 1000:
            new_platform, _ = generate_platform(platforms[-1].right, platforms[-1].y)
            platforms.append(new_platform)
            new_coins, new_enemies = generate_coins_and_enemies([new_platform])
            coins.extend(new_coins)
            enemies.extend(new_enemies)

        platforms = [p for p in platforms if p.right > scroll_x - 800]
        coins = [coin for coin in coins if coin.right > scroll_x - 800]
        enemies = [enemy for enemy in enemies if enemy.right > scroll_x - 800]

        world.fill((0, 0, 0))
        for index in range(-1, 3):
            x = index * background_width - (scroll_x % background_width)
            world.blit(background, (x, 0))

        for platform in platforms:
            pygame.draw.rect(world, (0, 0, 0), platform.move(-scroll_x, 0))

        coin_timer += 1
        if coin_timer >= coin_speed:
            coin_timer = 0
            coin_index = (coin_index + 1) % len(coin_images)
        for coin in coins:
            world.blit(coin_images[coin_index], coin.move(-scroll_x, 0))

        snail_timer += 1
        if snail_timer >= snail_speed:
            snail_timer = 0
            snail_index = (snail_index + 1) % len(snail_images)
        for enemy in enemies:
            world.blit(snail_images[snail_index], enemy.move(-scroll_x, 0))

        frame_timer += 1
        if frame_timer >= animation_speed:
            frame_timer = 0
            if not standing_on_platform:
                player_image = jump_images[image_index % len(jump_images)]
            elif crouching:
                if image_index < len(crouch_images):
                    player_image = crouch_images[image_index]
                else:
                    crouching = False
                    image_index = 0
                    player_image = run_images[0]
            else:
                player_image = run_images[image_index % len(run_images)]
            image_index += 1

        world.blit(player_image, player_rect)

        camera_y = player_rect.centery - window.get_height() // 2
        camera_y = max(0, min(camera_y, world_height - window.get_height()))
        window.blit(world, (0, 0), area=pygame.Rect(0, camera_y, *window.get_size()))

        distance_text = font.render(f"Distance: {int(distance)} m", True, (255, 255, 255))
        record_text = font.render(f"Record: {best_record} m", True, (255, 215, 0))
        score_text = font.render(str(coin_score), True, (255, 215, 0))

        window.blit(distance_text, (20, 20))
        window.blit(record_text, (500, 20))
        window.blit(coin_counter_image, (500, 39))
        window.blit(score_text, (500 + coin_counter_image.get_width() + 5, 50))

        pygame.display.flip()
        clock.tick(FPS)


def show_main_menu() -> bool:
    """Display the main menu. Return True to start or False to quit."""
    stand_index = 0
    stand_timer = 0
    menu_animation_speed = 6
    menu_scroll = 0.0

    while True:
        menu_scroll = (menu_scroll + 0.3) % background_width

        for index in range(-1, 2):
            x = index * background_width - menu_scroll
            window.blit(background, (x, -150))

        overlay = pygame.Surface(window.get_size())
        overlay.set_alpha(100)
        overlay.fill((0, 0, 0))
        window.blit(overlay, (0, 0))

        title = font.render("PYuri", True, (255, 255, 255))
        start_text = font.render("Press any key to start", True, (200, 200, 200))
        window.blit(title, title.get_rect(center=(window.get_width() // 2, 110)))
        window.blit(start_text, start_text.get_rect(center=(window.get_width() // 2, 160)))

        stand_timer += 1
        if stand_timer >= menu_animation_speed:
            stand_timer = 0
            stand_index = (stand_index + 1) % len(run_images)

        menu_player = run_images[stand_index]
        menu_player_rect = menu_player.get_rect(
            midbottom=(window.get_width() // 2, window.get_height() - 50)
        )
        window.blit(menu_player, menu_player_rect)

        floor = pygame.Rect(0, window.get_height() - 50, window.get_width(), 20)
        pygame.draw.rect(window, (0, 0, 0), floor)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == KEYDOWN:
                return True

        clock.tick(FPS)


def main() -> None:
    if show_main_menu():
        restart = True
        while restart:
            restart = play_game()

    pygame.quit()


if __name__ == "__main__":
    main()
