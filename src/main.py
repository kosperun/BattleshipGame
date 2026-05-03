import copy
import sys

import pygame

from elements.autoships import AutoShips
from elements.constants import (
    AUTO_BUTTON_PLACE,
    BLACK,
    BLOCK_SIZE,
    HOW_TO_CREATE_SHIPS_MESSAGE,
    LEFT_MARGIN,
    LETTERS,
    LIGHT_GRAY,
    MANUAL_BUTTON_PLACE,
    MESSAGE_RECT_COMPUTER,
    MESSAGE_RECT_HUMAN,
    PLAY_AGAIN_BUTTON_PLACE,
    PLAY_AGAIN_MESSAGE,
    RECT_FOR_COMPUTER_SHIPS_COUNT,
    RECT_FOR_GRIDS,
    RECT_FOR_HUMAN_SHIPS_COUNT,
    RECT_FOR_MESSAGES_AND_BUTTONS,
    SIZE,
    UNDO_BUTTON_PLACE,
    UPPER_MARGIN,
    WHITE,
    X_OFFSET_FOR_COMPUTER_SHIPS_COUNT,
    X_OFFSET_FOR_HUMAN_SHIPS_COUNT,
    Y_OFFSET_FOR_SHIPS_COUNT,
)
from game_logic import (
    around_last_computer_hit_set,
    check_hit_or_miss,
    computer_destroyed_ships_count,
    computer_shoots,
    destroyed_computer_ships,
    dotted_set,
    dotted_set_for_computer_not_to_shoot,
    hit_blocks,
    hit_blocks_for_computer_not_to_shoot,
    human_destroyed_ships_count,
    last_hits_list,
    update_used_blocks,
)
from graphics import Grid
from graphics.button import Button
from graphics.drawing import (
    draw_from_dotted_set,
    draw_hit_blocks,
    draw_ships,
    font,
    game_over_font,
    pixel_to_grid,
    print_destroyed_ships_count,
    screen,
    show_message_at_rect_center,
)
from graphics.manual_ships import manually_create_new_ship


def main():
    """
    The main function of the game where the following things happen:
    - decision how to create human ships (auto or manual)
    - optional manual creation of human ships
    - game loop
    - exit from the game
    """
    ships_creation_not_decided = True
    ships_not_created = True
    drawing = False
    game_over = False
    computer_turn = False
    start = (0, 0)
    ship_size = (0, 0)
    x_start, y_start = 0, 0

    human_ships_to_draw = []
    human_ships_set = set()
    used_blocks_for_manual_drawing = set()
    num_ships_list = [0, 0, 0, 0]

    # Create AUTO and MANUAL buttons and explanatory message for them
    auto_button = Button(AUTO_BUTTON_PLACE, "AUTO", HOW_TO_CREATE_SHIPS_MESSAGE, font)
    manual_button = Button(MANUAL_BUTTON_PLACE, "MANUAL", HOW_TO_CREATE_SHIPS_MESSAGE, font)

    # Create UNDO message and button
    undo_button = Button(UNDO_BUTTON_PLACE, "UNDO LAST SHIP", "", font)

    # Create PLAY AGAIN and QUIT buttons and message for them
    play_again_button = Button(PLAY_AGAIN_BUTTON_PLACE, "PLAY AGAIN", PLAY_AGAIN_MESSAGE, font)
    quit_game_button = Button(MANUAL_BUTTON_PLACE, "QUIT", PLAY_AGAIN_MESSAGE, font)

    screen.fill(WHITE)
    Grid(title="COMPUTER", offset=0, font=font, letters=LETTERS, line_color=BLACK, text_color=BLACK)  # type: ignore
    Grid(title="HUMAN", offset=15, font=font, letters=LETTERS, line_color=BLACK, text_color=BLACK)  # type: ignore
    # Create computer ships
    computer = AutoShips(0)
    computer_ships_working = copy.deepcopy(computer.ships)

    while ships_creation_not_decided:
        auto_button.draw()
        manual_button.draw()
        auto_button.change_color_on_hover()
        manual_button.change_color_on_hover()
        auto_button.print_message()

        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # If AUTO button is pressed - create human ships automatically
            elif event.type == pygame.MOUSEBUTTONDOWN and auto_button.rect.collidepoint(mouse):
                human = AutoShips(15)
                human_ships_to_draw = human.ships
                human_ships_working = copy.deepcopy(human.ships)
                human_ships_set = human.ships_set
                ships_creation_not_decided = False
                ships_not_created = False
            elif event.type == pygame.MOUSEBUTTONDOWN and manual_button.rect.collidepoint(mouse):
                ships_creation_not_decided = False

        pygame.display.update()
        screen.fill(WHITE, RECT_FOR_MESSAGES_AND_BUTTONS)

    while ships_not_created:
        screen.fill(WHITE, RECT_FOR_GRIDS)
        Grid(title="COMPUTER", offset=0, font=font, letters=LETTERS, line_color=BLACK, text_color=BLACK)  # type: ignore
        Grid(title="HUMAN", offset=15, font=font, letters=LETTERS, line_color=BLACK, text_color=BLACK)
        undo_button.draw()
        undo_button.print_message()
        undo_button.change_color_on_hover()
        mouse = pygame.mouse.get_pos()
        if not human_ships_to_draw:
            undo_button.draw(LIGHT_GRAY)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif undo_button.rect.collidepoint(mouse) and event.type == pygame.MOUSEBUTTONDOWN:
                if human_ships_to_draw:
                    screen.fill(WHITE, RECT_FOR_MESSAGES_AND_BUTTONS)
                    deleted_ship = human_ships_to_draw.pop()
                    num_ships_list[len(deleted_ship) - 1] -= 1
                    update_used_blocks(ship=deleted_ship, method=used_blocks_for_manual_drawing.discard)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                x_start, y_start = event.pos
                start = x_start, y_start
                ship_size = (0, 0)
            elif drawing and event.type == pygame.MOUSEMOTION:
                x_end, y_end = event.pos
                ship_size = x_end - x_start, y_end - y_start
            elif drawing and event.type == pygame.MOUSEBUTTONUP:
                x_end, y_end = event.pos
                drawing = False
                ship_size = (0, 0)
                manually_create_new_ship(
                    human_ships_to_draw=human_ships_to_draw,
                    human_ships_set=human_ships_set,
                    used_blocks_for_manual_drawing=used_blocks_for_manual_drawing,
                    num_ships_list=num_ships_list,
                    x_start=x_start,
                    y_start=y_start,
                    x_end=x_end,
                    y_end=y_end,
                )
            if len(human_ships_to_draw) == 10:
                ships_not_created = False
                human_ships_working = copy.deepcopy(human_ships_to_draw)
                screen.fill(WHITE, RECT_FOR_MESSAGES_AND_BUTTONS)
        pygame.draw.rect(screen, BLACK, (start, ship_size), 3)
        draw_ships(human_ships_to_draw)
        pygame.display.update()

    while not game_over:
        screen.fill(WHITE, RECT_FOR_HUMAN_SHIPS_COUNT)
        screen.fill(WHITE, RECT_FOR_COMPUTER_SHIPS_COUNT)
        if not dotted_set | hit_blocks:
            show_message_at_rect_center("GAME STARTED! YOUR MOVE!", MESSAGE_RECT_COMPUTER)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif not computer_turn and event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (LEFT_MARGIN < x < LEFT_MARGIN + 10 * BLOCK_SIZE) and (
                    UPPER_MARGIN < y < UPPER_MARGIN + 10 * BLOCK_SIZE
                ):
                    fired_block = pixel_to_grid(x, y)
                    computer_turn = not check_hit_or_miss(
                        fired_block=fired_block,
                        opponents_ships_list=computer_ships_working,
                        computer_turn=False,
                        opponents_ships_list_original_copy=computer.ships,
                        opponents_ships_set=computer.ships_set,
                        computer=computer,
                    )

                    draw_from_dotted_set(dotted_set)
                    draw_hit_blocks(hit_blocks)
                    screen.fill(WHITE, MESSAGE_RECT_COMPUTER)
                    show_message_at_rect_center(
                        f"Your last shot: {LETTERS[fired_block[0]-1] + str(fired_block[1])}",
                        MESSAGE_RECT_COMPUTER,
                    )
                else:
                    show_message_at_rect_center("Your shot is outside of grid! Try again", MESSAGE_RECT_COMPUTER)
        if computer_turn:
            fired_block = computer_shoots()
            computer_turn = check_hit_or_miss(
                fired_block=fired_block,
                opponents_ships_list=human_ships_working,
                computer_turn=True,
                opponents_ships_list_original_copy=human_ships_to_draw,
                opponents_ships_set=human_ships_set,
                computer=computer,
            )

            draw_from_dotted_set(dotted_set)
            draw_hit_blocks(hit_blocks)
            screen.fill(WHITE, MESSAGE_RECT_HUMAN)
            show_message_at_rect_center(
                f"Computer's last shot: {LETTERS[fired_block[0] - 16] + str(fired_block[1])}",
                MESSAGE_RECT_HUMAN,
            )
        draw_ships(destroyed_computer_ships)
        draw_ships(human_ships_to_draw)

        if not computer.ships_set:
            show_message_at_rect_center("YOU WIN!", (0, 0, SIZE[0], SIZE[1]), game_over_font)
            game_over = True
        if not human_ships_set:
            show_message_at_rect_center("YOU LOSE!", (0, 0, SIZE[0], SIZE[1]), game_over_font)
            game_over = True

        print_destroyed_ships_count(
            X_OFFSET_FOR_HUMAN_SHIPS_COUNT, Y_OFFSET_FOR_SHIPS_COUNT, human_destroyed_ships_count, font
        )
        print_destroyed_ships_count(
            X_OFFSET_FOR_COMPUTER_SHIPS_COUNT, Y_OFFSET_FOR_SHIPS_COUNT, computer_destroyed_ships_count, font
        )
        pygame.display.update()

    while game_over:
        screen.fill(WHITE, RECT_FOR_MESSAGES_AND_BUTTONS)
        play_again_button.draw()
        play_again_button.print_message()
        play_again_button.change_color_on_hover()
        quit_game_button.draw()
        quit_game_button.change_color_on_hover()

        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and play_again_button.rect.collidepoint(mouse):
                around_last_computer_hit_set.clear()
                dotted_set_for_computer_not_to_shoot.clear()
                hit_blocks_for_computer_not_to_shoot.clear()
                last_hits_list.clear()
                hit_blocks.clear()
                dotted_set.clear()
                destroyed_computer_ships.clear()
                main()
            elif event.type == pygame.MOUSEBUTTONDOWN and quit_game_button.rect.collidepoint(mouse):
                pygame.quit()
                sys.exit()
        pygame.display.update()


if __name__ == "__main__":
    main()
