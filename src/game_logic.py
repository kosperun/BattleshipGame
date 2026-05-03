"""Module for the logic behind the game."""

from random import choice
from typing import Callable

from elements.autoships import AutoShips
from elements.constants import COMPUTER_X_MAX, COMPUTER_X_MIN, Y_MAX, Y_MIN


class GameState:
    """Holds all mutable game state that was previously in module-level globals."""

    def __init__(self) -> None:
        self.computer_available_to_fire_set: set = {
            (x, y) for x in range(COMPUTER_X_MIN, COMPUTER_X_MAX + 1) for y in range(Y_MIN, Y_MAX + 1)
        }
        self.around_last_computer_hit_set: set = set()
        self.dotted_set_for_computer_not_to_shoot: set = set()
        self.hit_blocks_for_computer_not_to_shoot: set = set()
        self.last_hits_list: list = []
        self.hit_blocks: set = set()
        self.dotted_set: set = set()
        self.destroyed_computer_ships: list = []
        self.human_destroyed_ships_count: dict = {4: 0, 3: 0, 2: 0, 1: 0, "#": 0}
        self.computer_destroyed_ships_count: dict = {4: 0, 3: 0, 2: 0, 1: 0, "#": 0}

    def reset(self) -> None:
        self.computer_available_to_fire_set = {
            (x, y) for x in range(COMPUTER_X_MIN, COMPUTER_X_MAX + 1) for y in range(Y_MIN, Y_MAX + 1)
        }
        self.around_last_computer_hit_set.clear()
        self.dotted_set_for_computer_not_to_shoot.clear()
        self.hit_blocks_for_computer_not_to_shoot.clear()
        self.last_hits_list.clear()
        self.hit_blocks.clear()
        self.dotted_set.clear()
        self.destroyed_computer_ships.clear()
        self.human_destroyed_ships_count = {4: 0, 3: 0, 2: 0, 1: 0, "#": 0}
        self.computer_destroyed_ships_count = {4: 0, 3: 0, 2: 0, 1: 0, "#": 0}


def computer_shoots(state: GameState) -> tuple:
    """Randomly chooses a block from available to shoot from set."""
    if not state.computer_available_to_fire_set:
        state.computer_available_to_fire_set = {
            (x, y) for x in range(COMPUTER_X_MIN, COMPUTER_X_MAX + 1) for y in range(Y_MIN, Y_MAX + 1)
        }

    set_to_shoot_from = state.computer_available_to_fire_set
    if state.around_last_computer_hit_set:
        set_to_shoot_from = state.around_last_computer_hit_set
    computer_fired_block = choice(tuple(set_to_shoot_from))
    state.computer_available_to_fire_set.discard(computer_fired_block)
    return computer_fired_block


def check_hit_or_miss(
    *,
    state: GameState,
    fired_block: tuple,
    opponents_ships_list: list[list],
    computer_turn: bool,
    opponents_ships_list_original_copy: list,
    opponents_ships_set: set,
    computer: AutoShips,
) -> bool:
    """
    Checks whether the block that was shot at either by computer or by human is a hit or a miss.
    Updates sets with dots (in missed blocks or in diagonal blocks around hit block) and 'X's
    (in hit blocks).
    Removes destroyed ships from the list of ships.
    """
    for ind, elem in enumerate(opponents_ships_list):
        diagonal_only = True
        if fired_block in elem:
            if len(elem) == 1:
                diagonal_only = False
            update_dotted_and_hit_sets(
                state=state,
                fired_block=fired_block,
                computer_turn=computer_turn,
                diagonal_only=diagonal_only,
            )
            elem.remove(fired_block)
            opponents_ships_set.discard(fired_block)
            if computer_turn:
                state.last_hits_list.append(fired_block)
                update_around_last_computer_hit(
                    state=state,
                    fired_block=fired_block,
                    computer_hits=True,
                )
            if not elem:
                update_destroyed_ships(
                    state=state,
                    ind=ind,
                    computer_turn=computer_turn,
                    opponents_ships_list_original_copy=opponents_ships_list_original_copy,
                )
                if computer_turn:
                    state.last_hits_list.clear()
                    state.around_last_computer_hit_set.clear()
                else:
                    # Computer ships are hidden until destroyed
                    state.destroyed_computer_ships.append(computer.ships[ind])
            return True
    add_missed_block_to_dotted_set(state=state, fired_block=fired_block)
    if computer_turn:
        update_around_last_computer_hit(
            state=state,
            fired_block=fired_block,
            computer_hits=False,
        )
    return False


def update_destroyed_ships(
    *,
    state: GameState,
    ind: int,
    computer_turn: bool,
    opponents_ships_list_original_copy: list,
) -> None:
    """
    Adds blocks before and after a ship to dotted_set to draw dots on them.
    Adds all blocks in a ship to hit_blocks set to draw 'X's within a destroyed ship.
    """
    ship = sorted(opponents_ships_list_original_copy[ind])
    for i in range(-1, 1):
        update_dotted_and_hit_sets(
            state=state,
            fired_block=ship[i],
            computer_turn=computer_turn,
            diagonal_only=False,
        )
    if computer_turn:
        state.human_destroyed_ships_count[len(ship)] += 1
        state.human_destroyed_ships_count["#"] += 1
    else:
        state.computer_destroyed_ships_count[len(ship)] += 1
        state.computer_destroyed_ships_count["#"] += 1


def update_around_last_computer_hit(
    *,
    state: GameState,
    fired_block: tuple,
    computer_hits: bool,
) -> None:
    """
    Updates around_last_computer_hit_set if computer hit but didn't destroy a ship.
    Makes computer choose the right blocks to quickly finish off a partially-hit ship.
    """
    if computer_hits and fired_block in state.around_last_computer_hit_set:
        state.around_last_computer_hit_set = computer_hits_twice(state)
    elif computer_hits and fired_block not in state.around_last_computer_hit_set:
        computer_first_hit(state=state, fired_block=fired_block)
    elif not computer_hits:
        state.around_last_computer_hit_set.discard(fired_block)

    state.around_last_computer_hit_set -= state.dotted_set_for_computer_not_to_shoot
    state.around_last_computer_hit_set -= state.hit_blocks_for_computer_not_to_shoot
    state.computer_available_to_fire_set -= state.around_last_computer_hit_set
    state.computer_available_to_fire_set -= state.dotted_set_for_computer_not_to_shoot


def computer_first_hit(*, state: GameState, fired_block: tuple) -> None:
    """
    Adds blocks above, below, to the right and to the left from the block hit
    by computer to a temporary set for computer to choose its next shot from.
    """
    x_hit, y_hit = fired_block
    if x_hit > COMPUTER_X_MIN:
        state.around_last_computer_hit_set.add((x_hit - 1, y_hit))
    if x_hit < COMPUTER_X_MAX:
        state.around_last_computer_hit_set.add((x_hit + 1, y_hit))
    if y_hit > Y_MIN:
        state.around_last_computer_hit_set.add((x_hit, y_hit - 1))
    if y_hit < Y_MAX:
        state.around_last_computer_hit_set.add((x_hit, y_hit + 1))


def computer_hits_twice(state: GameState) -> set:
    """
    Adds blocks before and after two or more consecutive hit blocks so the computer
    can finish the ship faster.
    """
    state.last_hits_list.sort()
    new_around_last_hit_set = set()
    for i in range(len(state.last_hits_list) - 1):
        x1 = state.last_hits_list[i][0]
        x2 = state.last_hits_list[i + 1][0]
        y1 = state.last_hits_list[i][1]
        y2 = state.last_hits_list[i + 1][1]
        if x1 == x2:
            if y1 > Y_MIN:
                new_around_last_hit_set.add((x1, y1 - 1))
            if y2 < Y_MAX:
                new_around_last_hit_set.add((x1, y2 + 1))
        elif y1 == y2:
            if x1 > COMPUTER_X_MIN:
                new_around_last_hit_set.add((x1 - 1, y1))
            if x2 < COMPUTER_X_MAX:
                new_around_last_hit_set.add((x2 + 1, y1))
    return new_around_last_hit_set


def update_dotted_and_hit_sets(
    *,
    state: GameState,
    fired_block: tuple,
    computer_turn: bool,
    diagonal_only: bool = True,
) -> None:
    """
    Puts dots in center of diagonal or all around a block that was hit (either by human or
    by computer). Adds all diagonal blocks or all-around chosen block to a separate set.
    """
    x, y = fired_block
    x_min = 15 * computer_turn
    x_max = 11 + 15 * computer_turn
    state.hit_blocks_for_computer_not_to_shoot.add(fired_block)
    state.hit_blocks.add(fired_block)
    for i in range(-1, 2):
        for j in range(-1, 2):
            if (not diagonal_only or (i != 0 and j != 0)) and x_min < x + i < x_max and Y_MIN - 1 < y + j < Y_MAX + 1:
                add_missed_block_to_dotted_set(state=state, fired_block=(x + i, y + j))
    state.dotted_set -= state.hit_blocks


def add_missed_block_to_dotted_set(*, state: GameState, fired_block: tuple) -> None:
    """
    Adds fired_block to the dotted sets (missed shots / computer exclusion).
    """
    state.dotted_set.add(fired_block)
    state.dotted_set_for_computer_not_to_shoot.add(fired_block)


def is_ship_valid(*, ship_set: set, blocks_for_manual_drawing: set) -> bool:
    """
    Checks if ship is not touching other ships.
    """
    return ship_set.isdisjoint(blocks_for_manual_drawing)


def validate_ships_numbers(*, ship: list, num_ships_list: list) -> bool:
    """
    Checks if a ship of particular length (1-4) does not exceed necessary quantity (4-1).
    """
    return (5 - len(ship)) > num_ships_list[len(ship) - 1]


def update_used_blocks(*, ship: list, method: Callable) -> None:
    """
    Adds ship's blocks and all surrounding blocks to the used-blocks set.
    """
    for block in ship:
        for i in range(-1, 2):
            for j in range(-1, 2):
                method((block[0] + i, block[1] + j))
