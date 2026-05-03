"""Tests for game_logic.py — written against current behaviour before any refactor."""

import pytest

import game_logic
from game_logic import GameState


@pytest.fixture()
def state():
    """Fresh GameState for every test."""
    return GameState()


# ---------------------------------------------------------------------------
# computer_shoots
# ---------------------------------------------------------------------------

class TestComputerShoots:
    def test_returns_tuple(self, state):
        result = game_logic.computer_shoots(state)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_fired_block_within_grid(self, state):
        for _ in range(50):
            s = GameState()
            x, y = game_logic.computer_shoots(s)
            assert 16 <= x <= 25
            assert 1 <= y <= 10

    def test_fired_block_removed_from_available_set(self, state):
        block = game_logic.computer_shoots(state)
        assert block not in state.computer_available_to_fire_set

    def test_available_set_shrinks_by_one_per_shot(self, state):
        before = len(state.computer_available_to_fire_set)
        game_logic.computer_shoots(state)
        assert len(state.computer_available_to_fire_set) == before - 1

    def test_prefers_around_last_hit_set_when_non_empty(self, state):
        target = (20, 5)
        state.around_last_computer_hit_set.add(target)
        for _ in range(100):
            if not state.around_last_computer_hit_set:
                break
            shot = game_logic.computer_shoots(state)
            assert shot == target

    def test_resets_available_set_when_empty(self, state):
        state.computer_available_to_fire_set.clear()
        result = game_logic.computer_shoots(state)
        x, y = result
        assert 16 <= x <= 25
        assert 1 <= y <= 10


# ---------------------------------------------------------------------------
# computer_first_hit
# ---------------------------------------------------------------------------

class TestComputerFirstHit:
    def test_mid_grid_adds_four_neighbours(self, state):
        game_logic.computer_first_hit(state=state, fired_block=(20, 5))
        assert state.around_last_computer_hit_set == {(19, 5), (21, 5), (20, 4), (20, 6)}

    def test_left_edge_no_left_neighbour(self, state):
        game_logic.computer_first_hit(state=state, fired_block=(16, 5))
        assert (15, 5) not in state.around_last_computer_hit_set
        assert (17, 5) in state.around_last_computer_hit_set

    def test_right_edge_no_right_neighbour(self, state):
        game_logic.computer_first_hit(state=state, fired_block=(25, 5))
        assert (26, 5) not in state.around_last_computer_hit_set
        assert (24, 5) in state.around_last_computer_hit_set

    def test_top_edge_no_upper_neighbour(self, state):
        game_logic.computer_first_hit(state=state, fired_block=(20, 1))
        assert (20, 0) not in state.around_last_computer_hit_set
        assert (20, 2) in state.around_last_computer_hit_set

    def test_bottom_edge_no_lower_neighbour(self, state):
        game_logic.computer_first_hit(state=state, fired_block=(20, 10))
        assert (20, 11) not in state.around_last_computer_hit_set
        assert (20, 9) in state.around_last_computer_hit_set

    def test_corner_adds_only_two_neighbours(self, state):
        game_logic.computer_first_hit(state=state, fired_block=(16, 1))
        assert state.around_last_computer_hit_set == {(17, 1), (16, 2)}

    def test_corner_bottom_right(self, state):
        game_logic.computer_first_hit(state=state, fired_block=(25, 10))
        assert state.around_last_computer_hit_set == {(24, 10), (25, 9)}


# ---------------------------------------------------------------------------
# computer_hits_twice
# ---------------------------------------------------------------------------

class TestComputerHitsTwice:
    def test_horizontal_ship_adds_ends(self, state):
        state.last_hits_list[:] = [(20, 5), (21, 5)]
        result = game_logic.computer_hits_twice(state)
        assert (19, 5) in result
        assert (22, 5) in result

    def test_vertical_ship_adds_ends(self, state):
        state.last_hits_list[:] = [(20, 4), (20, 5)]
        result = game_logic.computer_hits_twice(state)
        assert (20, 3) in result
        assert (20, 6) in result

    def test_horizontal_left_edge_no_left_end(self, state):
        state.last_hits_list[:] = [(16, 5), (17, 5)]
        result = game_logic.computer_hits_twice(state)
        assert (15, 5) not in result
        assert (18, 5) in result

    def test_horizontal_right_edge_no_right_end(self, state):
        state.last_hits_list[:] = [(24, 5), (25, 5)]
        result = game_logic.computer_hits_twice(state)
        assert (26, 5) not in result
        assert (23, 5) in result

    def test_vertical_top_edge_no_upper_end(self, state):
        state.last_hits_list[:] = [(20, 1), (20, 2)]
        result = game_logic.computer_hits_twice(state)
        assert (20, 0) not in result
        assert (20, 3) in result

    def test_vertical_bottom_edge_no_lower_end(self, state):
        state.last_hits_list[:] = [(20, 9), (20, 10)]
        result = game_logic.computer_hits_twice(state)
        assert (20, 11) not in result
        assert (20, 8) in result

    def test_three_hit_horizontal_ship(self, state):
        state.last_hits_list[:] = [(20, 5), (21, 5), (22, 5)]
        result = game_logic.computer_hits_twice(state)
        assert (19, 5) in result
        assert (23, 5) in result

    def test_returns_set(self, state):
        state.last_hits_list[:] = [(20, 5), (21, 5)]
        assert isinstance(game_logic.computer_hits_twice(state), set)


# ---------------------------------------------------------------------------
# update_dotted_and_hit_sets
# ---------------------------------------------------------------------------

class TestUpdateDottedAndHitSets:
    def test_hit_block_added_to_hit_blocks(self, state):
        game_logic.update_dotted_and_hit_sets(state=state, fired_block=(20, 5), computer_turn=True, diagonal_only=True)
        assert (20, 5) in state.hit_blocks

    def test_diagonal_only_adds_only_diagonals(self, state):
        game_logic.update_dotted_and_hit_sets(state=state, fired_block=(20, 5), computer_turn=True, diagonal_only=True)
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            assert (20 + dx, 5 + dy) in state.dotted_set
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            assert (20 + dx, 5 + dy) not in state.dotted_set

    def test_not_diagonal_only_adds_all_around(self, state):
        game_logic.update_dotted_and_hit_sets(state=state, fired_block=(20, 5), computer_turn=True, diagonal_only=False)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                assert (20 + dx, 5 + dy) in state.dotted_set | state.hit_blocks

    def test_hit_block_not_in_dotted_set(self, state):
        game_logic.update_dotted_and_hit_sets(state=state, fired_block=(20, 5), computer_turn=True, diagonal_only=False)
        assert (20, 5) not in state.dotted_set

    def test_computer_turn_uses_computer_grid_boundaries(self, state):
        game_logic.update_dotted_and_hit_sets(state=state, fired_block=(20, 5), computer_turn=True, diagonal_only=False)
        for x, y in state.dotted_set:
            assert 16 <= x <= 25

    def test_human_turn_uses_human_grid_boundaries(self, state):
        game_logic.update_dotted_and_hit_sets(state=state, fired_block=(5, 5), computer_turn=False, diagonal_only=False)
        for x, y in state.dotted_set:
            assert 1 <= x <= 10

    def test_edge_block_does_not_add_out_of_bounds_dots(self, state):
        game_logic.update_dotted_and_hit_sets(state=state, fired_block=(16, 1), computer_turn=True, diagonal_only=False)
        for x, y in state.dotted_set:
            assert 16 <= x <= 25
            assert 1 <= y <= 10

    def test_hit_block_added_to_hit_blocks_for_computer_not_to_shoot(self, state):
        game_logic.update_dotted_and_hit_sets(state=state, fired_block=(20, 5), computer_turn=True, diagonal_only=True)
        assert (20, 5) in state.hit_blocks_for_computer_not_to_shoot


# ---------------------------------------------------------------------------
# add_missed_block_to_dotted_set
# ---------------------------------------------------------------------------

class TestAddMissedBlockToDottedSet:
    def test_adds_to_dotted_set(self, state):
        game_logic.add_missed_block_to_dotted_set(state=state, fired_block=(20, 5))
        assert (20, 5) in state.dotted_set

    def test_adds_to_computer_not_to_shoot_set(self, state):
        game_logic.add_missed_block_to_dotted_set(state=state, fired_block=(20, 5))
        assert (20, 5) in state.dotted_set_for_computer_not_to_shoot


# ---------------------------------------------------------------------------
# is_ship_valid
# ---------------------------------------------------------------------------

class TestIsShipValid:
    def test_valid_ship_no_overlap(self, state):
        ship_set = {(3, 3), (3, 4)}
        used = {(1, 1), (2, 2)}
        assert game_logic.is_ship_valid(ship_set=ship_set, blocks_for_manual_drawing=used) is True

    def test_invalid_ship_overlaps_used_block(self, state):
        ship_set = {(3, 3), (3, 4)}
        used = {(3, 3)}
        assert game_logic.is_ship_valid(ship_set=ship_set, blocks_for_manual_drawing=used) is False

    def test_empty_ship_is_valid(self, state):
        assert game_logic.is_ship_valid(ship_set=set(), blocks_for_manual_drawing={(1, 1)}) is True

    def test_empty_used_blocks_always_valid(self, state):
        assert game_logic.is_ship_valid(ship_set={(5, 5)}, blocks_for_manual_drawing=set()) is True


# ---------------------------------------------------------------------------
# validate_ships_numbers
# ---------------------------------------------------------------------------

class TestValidateShipsNumbers:
    def test_can_add_first_ship_of_each_size(self, state):
        assert game_logic.validate_ships_numbers(ship=[1], num_ships_list=[0, 0, 0, 0]) is True
        assert game_logic.validate_ships_numbers(ship=[1, 2], num_ships_list=[0, 0, 0, 0]) is True
        assert game_logic.validate_ships_numbers(ship=[1, 2, 3], num_ships_list=[0, 0, 0, 0]) is True
        assert game_logic.validate_ships_numbers(ship=[1, 2, 3, 4], num_ships_list=[0, 0, 0, 0]) is True

    def test_cannot_add_ship_when_quota_reached(self, state):
        assert game_logic.validate_ships_numbers(ship=[1], num_ships_list=[4, 0, 0, 0]) is False
        assert game_logic.validate_ships_numbers(ship=[1, 2], num_ships_list=[0, 3, 0, 0]) is False
        assert game_logic.validate_ships_numbers(ship=[1, 2, 3], num_ships_list=[0, 0, 2, 0]) is False
        assert game_logic.validate_ships_numbers(ship=[1, 2, 3, 4], num_ships_list=[0, 0, 0, 1]) is False

    def test_can_add_when_one_slot_remains(self, state):
        assert game_logic.validate_ships_numbers(ship=[1], num_ships_list=[3, 0, 0, 0]) is True
        assert game_logic.validate_ships_numbers(ship=[1, 2], num_ships_list=[0, 2, 0, 0]) is True


# ---------------------------------------------------------------------------
# update_used_blocks
# ---------------------------------------------------------------------------

class TestUpdateUsedBlocks:
    def test_adds_ship_blocks_and_surroundings(self, state):
        collected = set()
        game_logic.update_used_blocks(ship=[(5, 5)], method=collected.add)
        expected = {(5 + i, 5 + j) for i in range(-1, 2) for j in range(-1, 2)}
        assert collected == expected

    def test_two_block_ship_covers_surroundings(self, state):
        collected = set()
        game_logic.update_used_blocks(ship=[(5, 5), (5, 6)], method=collected.add)
        for block in [(5, 5), (5, 6)]:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    assert (block[0] + i, block[1] + j) in collected


# ---------------------------------------------------------------------------
# check_hit_or_miss
# ---------------------------------------------------------------------------

class TestCheckHitOrMiss:
    def _make_computer(self):
        from elements.autoships import AutoShips
        return AutoShips(offset=0)

    def test_miss_returns_false(self, state):
        computer = self._make_computer()
        result = game_logic.check_hit_or_miss(
            state=state,
            fired_block=(5, 5),
            opponents_ships_list=[[(3, 3), (3, 4)]],
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3), (3, 4)]],
            opponents_ships_set={(3, 3), (3, 4)},
            computer=computer,
        )
        assert result is False

    def test_miss_adds_block_to_dotted_set(self, state):
        computer = self._make_computer()
        game_logic.check_hit_or_miss(
            state=state,
            fired_block=(5, 5),
            opponents_ships_list=[[(3, 3)]],
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3)]],
            opponents_ships_set={(3, 3)},
            computer=computer,
        )
        assert (5, 5) in state.dotted_set

    def test_hit_returns_true(self, state):
        computer = self._make_computer()
        result = game_logic.check_hit_or_miss(
            state=state,
            fired_block=(3, 3),
            opponents_ships_list=[[(3, 3), (3, 4)]],
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3), (3, 4)]],
            opponents_ships_set={(3, 3), (3, 4)},
            computer=computer,
        )
        assert result is True

    def test_hit_removes_block_from_ship_list(self, state):
        computer = self._make_computer()
        ships = [[(3, 3), (3, 4)]]
        game_logic.check_hit_or_miss(
            state=state,
            fired_block=(3, 3),
            opponents_ships_list=ships,
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3), (3, 4)]],
            opponents_ships_set={(3, 3), (3, 4)},
            computer=computer,
        )
        assert (3, 3) not in ships[0]

    def test_hit_removes_block_from_ships_set(self, state):
        computer = self._make_computer()
        ships_set = {(3, 3), (3, 4)}
        game_logic.check_hit_or_miss(
            state=state,
            fired_block=(3, 3),
            opponents_ships_list=[[(3, 3), (3, 4)]],
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3), (3, 4)]],
            opponents_ships_set=ships_set,
            computer=computer,
        )
        assert (3, 3) not in ships_set

    def test_destroyed_ship_updates_score(self, state):
        computer = self._make_computer()
        game_logic.check_hit_or_miss(
            state=state,
            fired_block=(3, 3),
            opponents_ships_list=[[(3, 3)]],
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3)]],
            opponents_ships_set={(3, 3)},
            computer=computer,
        )
        assert state.computer_destroyed_ships_count[1] == 1
        assert state.computer_destroyed_ships_count["#"] == 1

    def test_computer_hit_appends_to_last_hits_list(self, state):
        computer = self._make_computer()
        game_logic.check_hit_or_miss(
            state=state,
            fired_block=(20, 5),
            opponents_ships_list=[[(20, 5), (20, 6)]],
            computer_turn=True,
            opponents_ships_list_original_copy=[[(20, 5), (20, 6)]],
            opponents_ships_set={(20, 5), (20, 6)},
            computer=computer,
        )
        assert (20, 5) in state.last_hits_list

    def test_computer_destroy_clears_last_hits_list(self, state):
        computer = self._make_computer()
        state.last_hits_list[:] = [(20, 5)]
        game_logic.check_hit_or_miss(
            state=state,
            fired_block=(20, 5),
            opponents_ships_list=[[(20, 5)]],
            computer_turn=True,
            opponents_ships_list_original_copy=[[(20, 5)]],
            opponents_ships_set={(20, 5)},
            computer=computer,
        )
        assert state.last_hits_list == []

    def test_human_destroys_computer_ship_adds_to_destroyed_list(self, state):
        computer = self._make_computer()
        computer.ships = [[(3, 3)]]
        game_logic.check_hit_or_miss(
            state=state,
            fired_block=(3, 3),
            opponents_ships_list=[[(3, 3)]],
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3)]],
            opponents_ships_set={(3, 3)},
            computer=computer,
        )
        assert computer.ships[0] in state.destroyed_computer_ships


# ---------------------------------------------------------------------------
# update_destroyed_ships
# ---------------------------------------------------------------------------

class TestUpdateDestroyedShips:
    def test_increments_human_count_on_computer_turn(self, state):
        game_logic.update_destroyed_ships(
            state=state,
            ind=0,
            computer_turn=True,
            opponents_ships_list_original_copy=[[(20, 5), (20, 6)]],
        )
        assert state.human_destroyed_ships_count[2] == 1
        assert state.human_destroyed_ships_count["#"] == 1

    def test_increments_computer_count_on_human_turn(self, state):
        game_logic.update_destroyed_ships(
            state=state,
            ind=0,
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3), (3, 4), (3, 5)]],
        )
        assert state.computer_destroyed_ships_count[3] == 1
        assert state.computer_destroyed_ships_count["#"] == 1

    def test_adds_surrounding_dots_for_destroyed_ship(self, state):
        game_logic.update_destroyed_ships(
            state=state,
            ind=0,
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 5)]],
        )
        assert len(state.dotted_set | state.hit_blocks) > 0


# ---------------------------------------------------------------------------
# GameState.reset
# ---------------------------------------------------------------------------

class TestGameStateReset:
    def test_reset_clears_all_sets(self):
        state = GameState()
        state.hit_blocks.add((20, 5))
        state.dotted_set.add((20, 6))
        state.last_hits_list.append((20, 5))
        state.around_last_computer_hit_set.add((20, 4))
        state.destroyed_computer_ships.append([(20, 5)])
        state.human_destroyed_ships_count[1] = 3
        state.computer_destroyed_ships_count["#"] = 2
        state.reset()
        assert state.hit_blocks == set()
        assert state.dotted_set == set()
        assert state.last_hits_list == []
        assert state.around_last_computer_hit_set == set()
        assert state.destroyed_computer_ships == []
        assert state.human_destroyed_ships_count == {4: 0, 3: 0, 2: 0, 1: 0, "#": 0}
        assert state.computer_destroyed_ships_count == {4: 0, 3: 0, 2: 0, 1: 0, "#": 0}

    def test_reset_restores_full_available_fire_set(self):
        state = GameState()
        state.computer_available_to_fire_set.clear()
        state.reset()
        assert len(state.computer_available_to_fire_set) == 100
