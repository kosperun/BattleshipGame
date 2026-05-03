"""Module for drawing."""

import os
import sys

import pygame

from elements.constants import (
    BLACK,
    BLOCK_SIZE,
    FONT_SIZE,
    GAME_OVER_FONT_SIZE,
    LEFT_MARGIN,
    RED,
    SIZE,
    UPPER_MARGIN,
    WHITE,
)

# Resolve asset base dir: use PyInstaller's unpacked dir when frozen, else src/
_BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pygame.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("BattleShip")
try:
    icon = pygame.image.load(os.path.join(_BASE_DIR, "media", "BattleShip.png"))
    pygame.display.set_icon(icon)
except FileNotFoundError:
    print("Warning: media/BattleShip.png not found — window icon not set.")

font = pygame.font.SysFont("notosans", FONT_SIZE)
game_over_font = pygame.font.SysFont("notosans", GAME_OVER_FONT_SIZE)


def pixel_to_grid(px: int, py: int) -> tuple:
    return (px - LEFT_MARGIN) // BLOCK_SIZE + 1, (py - UPPER_MARGIN) // BLOCK_SIZE + 1


def grid_to_pixel(gx: int, gy: int) -> tuple:
    return BLOCK_SIZE * (gx - 1) + LEFT_MARGIN, BLOCK_SIZE * (gy - 1) + UPPER_MARGIN


def draw_ships(ships_coordinates_list: list, ships_color: tuple = BLACK) -> None:
    """
    Draws rectangles around the blocks that are occupied by a ship
    Args:
        ships_coordinates_list (list of tuples): a list of ships's coordinates
    """
    for elem in ships_coordinates_list:
        ship = sorted(elem)
        x_start = ship[0][0]
        y_start = ship[0][1]
        # Horizontal and 1block ships
        ship_width = BLOCK_SIZE * len(ship)
        ship_height = BLOCK_SIZE
        # Vertical ships
        if len(ship) > 1 and ship[0][0] == ship[1][0]:
            ship_width, ship_height = ship_height, ship_width
        x, y = grid_to_pixel(x_start, y_start)
        pygame.draw.rect(screen, ships_color, ((x, y), (ship_width, ship_height)), width=BLOCK_SIZE // 10)


def draw_from_dotted_set(dotted_set_to_draw_from: set, dots_color: tuple = BLACK) -> None:
    """
    Draws dots in the center of all blocks in the dotted_set
    """
    for elem in dotted_set_to_draw_from:
        pygame.draw.circle(
            screen,
            dots_color,
            (BLOCK_SIZE * (elem[0] - 0.5) + LEFT_MARGIN, BLOCK_SIZE * (elem[1] - 0.5) + UPPER_MARGIN),
            BLOCK_SIZE // 6,
        )


def draw_hit_blocks(hit_blocks_to_draw_from: set, hit_blocks_color: tuple = BLACK) -> None:
    """
    Draws 'X' in the blocks that were successfully hit either by computer or by human
    """
    for block in hit_blocks_to_draw_from:
        x1, y1 = grid_to_pixel(block[0], block[1])
        pygame.draw.line(screen, hit_blocks_color, (x1, y1), (x1 + BLOCK_SIZE, y1 + BLOCK_SIZE), BLOCK_SIZE // 6)
        pygame.draw.line(screen, hit_blocks_color, (x1, y1 + BLOCK_SIZE), (x1 + BLOCK_SIZE, y1), BLOCK_SIZE // 6)


def draw_computer_shot_with_highlight(fired_block: tuple, dotted_set: set, hit_blocks: set) -> None:
    """Draw only the latest computer shot in red, pause, then redraw it in black."""
    if fired_block in hit_blocks:
        draw_hit_blocks({fired_block}, RED)
    else:
        draw_from_dotted_set({fired_block}, RED)
    pygame.display.update()
    pygame.time.delay(600)
    if fired_block in hit_blocks:
        draw_hit_blocks({fired_block})
    else:
        draw_from_dotted_set({fired_block})


def show_message_at_rect_center(
    message: str,
    rect: tuple,
    font: pygame.font.Font = font,
    message_color: tuple = RED,
    background_color: tuple = WHITE,
) -> None:
    """
    Prints message to screen at a given rect's center.
    Args:
        message (str): Message to print
        rect (tuple): rectangle in (x_start, y_start, width, height) format
        font (pygame font object, optional): What font to use to print message. Defaults to font.
        message_color (tuple, optional): Color of the message. Defaults to RED.
    """
    message_width, message_height = font.size(message)
    message_rect = pygame.Rect(rect)
    x_start = message_rect.centerx - message_width / 2
    y_start = message_rect.centery - message_height / 2
    background_rect = pygame.Rect(x_start - BLOCK_SIZE / 2, y_start, message_width + BLOCK_SIZE, message_height)
    message_to_blit = font.render(message, True, message_color)
    screen.fill(background_color, background_rect)
    screen.blit(message_to_blit, (x_start, y_start))


def print_destroyed_ships_count(
    x_offset: int, y_offset: int, count_dict: dict, font: pygame.font.Font, color: tuple = RED
) -> None:
    """
    Prints numbers of destroyed ships at the grid's side.
    Args:
        font (pygame font object, optional): What font to use to print message.
        color (tuple, optional): Color of the message. Defaults to RED.
    """
    for ship, count in count_dict.items():
        title = font.render("Ships", True, color)
        text = font.render(f"{ship}: {count}", True, color)
        screen.blit(title, (x_offset, y_offset))
        num = ship if isinstance(ship, int) else 5
        screen.blit(text, (x_offset, y_offset + num * BLOCK_SIZE))
