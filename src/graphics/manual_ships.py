"""Create ships manually."""

import pygame

from elements.constants import (
    BLOCK_SIZE,
    LEFT_MARGIN,
    RECT_FOR_MESSAGES_AND_BUTTONS,
    UPPER_MARGIN,
    WHITE,
)
from game_logic import is_ship_valid, update_used_blocks, validate_ships_numbers
from graphics.drawing import screen, show_message_at_rect_center

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
    start_block = ((x_start - LEFT_MARGIN) // BLOCK_SIZE + 1, (y_start - UPPER_MARGIN) // BLOCK_SIZE + 1)
    end_block = ((x_end - LEFT_MARGIN) // BLOCK_SIZE + 1, (y_end - UPPER_MARGIN) // BLOCK_SIZE + 1)
    if start_block > end_block:
        start_block, end_block = end_block, start_block
    temp_ship = []
    if 15 < start_block[0] < 26 and 0 < start_block[1] < 11 and 15 < end_block[0] < 26 and 0 < end_block[1] < 11:
        temp_ship = create_new_ship(start_block, end_block)
    else:
        show_message_at_rect_center("SHIP IS BEYOND YOUR GRID! Try again!", RECT_FOR_MESSAGES_AND_BUTTONS)
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
                f"There already are enough of {len(temp_ship)} ships!", RECT_FOR_MESSAGES_AND_BUTTONS
            )
    else:
        show_message_at_rect_center("SHIPS ARE TOUCHING! Try again", RECT_FOR_MESSAGES_AND_BUTTONS)


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
        show_message_at_rect_center("SHIP IS TOO LARGE! Try again!", RECT_FOR_MESSAGES_AND_BUTTONS)
    return temp_ship
