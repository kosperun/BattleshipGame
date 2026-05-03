"""Create ships manually."""

import pygame

from elements.constants import (
    COMPUTER_X_MAX,
    COMPUTER_X_MIN,
    RECT_FOR_MESSAGES_AND_BUTTONS,
    WHITE,
    Y_MAX,
    Y_MIN,
)
from game_logic import is_ship_valid, update_used_blocks, validate_ships_numbers
from graphics.drawing import pixel_to_grid, screen, show_message_at_rect_center

def manually_create_new_ship(
    *,
    human_ships_to_draw,
    human_ships_set,
    used_blocks_for_manual_drawing,
    num_ships_list,
    x_start,
    y_start,
    x_end,
    y_end,
) -> None:
    """
    Validate each manually created ship and add it to the list of ships.
    """
    start_block = pixel_to_grid(x_start, y_start)
    end_block = pixel_to_grid(x_end, y_end)
    if start_block > end_block:
        start_block, end_block = end_block, start_block
    temp_ship = []
    if (COMPUTER_X_MIN <= start_block[0] <= COMPUTER_X_MAX and Y_MIN <= start_block[1] <= Y_MAX
            and COMPUTER_X_MIN <= end_block[0] <= COMPUTER_X_MAX and Y_MIN <= end_block[1] <= Y_MAX):
        temp_ship = create_new_ship(start_block, end_block)
    else:
        show_message_at_rect_center("Ship is outside your grid! Try again.", RECT_FOR_MESSAGES_AND_BUTTONS)
    if temp_ship:
        validate_and_save_new_ship(
            human_ships_to_draw, human_ships_set, used_blocks_for_manual_drawing, num_ships_list, temp_ship
        )


def validate_and_save_new_ship(
    human_ships_to_draw, human_ships_set, used_blocks_for_manual_drawing, num_ships_list, temp_ship
):
    temp_ship_set = set(temp_ship)
    if is_ship_valid(ship_set=temp_ship_set, blocks_for_manual_drawing=used_blocks_for_manual_drawing):
        if validate_ships_numbers(ship=temp_ship, num_ships_list=num_ships_list):
            num_ships_list[len(temp_ship) - 1] += 1
            human_ships_to_draw.append(temp_ship)
            human_ships_set |= temp_ship_set
            update_used_blocks(ship=temp_ship, method=used_blocks_for_manual_drawing.add)
        else:
            show_message_at_rect_center(
                f"You already have enough {len(temp_ship)}-block ships!", RECT_FOR_MESSAGES_AND_BUTTONS
            )
    else:
        show_message_at_rect_center("Ships are touching! Try again.", RECT_FOR_MESSAGES_AND_BUTTONS)


def create_new_ship(start_block, end_block):
    screen.fill(WHITE, RECT_FOR_MESSAGES_AND_BUTTONS)
    temp_ship = []
    if start_block[0] == end_block[0] and (end_block[1] - start_block[1]) < 4:
        for block in range(start_block[1], end_block[1] + 1):
            temp_ship.append((start_block[0], block))
    elif start_block[1] == end_block[1] and (end_block[0] - start_block[0]) < 4:
        for block in range(start_block[0], end_block[0] + 1):
            temp_ship.append((block, start_block[1]))
    else:
        show_message_at_rect_center("Ship is too large! Try again.", RECT_FOR_MESSAGES_AND_BUTTONS)
    return temp_ship
