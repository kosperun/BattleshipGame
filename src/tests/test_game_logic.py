"""Tests for game_logic.py — written against current behaviour before any refactor."""

import importlib
import sys
import pytest


def reload_game_logic():
    """Reload game_logic so every test starts with clean global state."""
    if "game_logic" in sys.modules:
        del sys.modules["game_logic"]
    import game_logic
    return game_logic


@pytest.fixture(autouse=True)
def gl():
    """Fresh game_logic module for every test."""
    module = reload_game_logic()
    return module


# ---------------------------------------------------------------------------
# computer_shoots
# ---------------------------------------------------------------------------

class TestComputerShoots:
    def test_returns_tuple(self, gl):
        result = gl.computer_shoots()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_fired_block_within_grid(self, gl):
        for _ in range(50):
            x, y = gl.computer_shoots()
            assert 16 <= x <= 25
            assert 1 <= y <= 10

    def test_fired_block_removed_from_available_set(self, gl):
        block = gl.computer_shoots()
        assert block not in gl.computer_available_to_fire_set

    def test_available_set_shrinks_by_one_per_shot(self, gl):
        before = len(gl.computer_available_to_fire_set)
        gl.computer_shoots()
        assert len(gl.computer_available_to_fire_set) == before - 1

    def test_prefers_around_last_hit_set_when_non_empty(self, gl):
        target = (20, 5)
        gl.around_last_computer_hit_set.add(target)
        # Shoot 100 times; every shot must come from the priority set
        for _ in range(100):
            if not gl.around_last_computer_hit_set:
                break
            shot = gl.computer_shoots()
            # shot came from around_last_computer_hit_set or it was already removed
            assert shot == target

    def test_resets_available_set_when_empty(self, gl):
        gl.computer_available_to_fire_set.clear()
        result = gl.computer_shoots()
        x, y = result
        assert 16 <= x <= 25
        assert 1 <= y <= 10


# ---------------------------------------------------------------------------
# computer_first_hit
# ---------------------------------------------------------------------------

class TestComputerFirstHit:
    def test_mid_grid_adds_four_neighbours(self, gl):
        gl.computer_first_hit(fired_block=(20, 5))
        assert gl.around_last_computer_hit_set == {(19, 5), (21, 5), (20, 4), (20, 6)}

    def test_left_edge_no_left_neighbour(self, gl):
        gl.computer_first_hit(fired_block=(16, 5))
        assert (15, 5) not in gl.around_last_computer_hit_set
        assert (17, 5) in gl.around_last_computer_hit_set

    def test_right_edge_no_right_neighbour(self, gl):
        gl.computer_first_hit(fired_block=(25, 5))
        assert (26, 5) not in gl.around_last_computer_hit_set
        assert (24, 5) in gl.around_last_computer_hit_set

    def test_top_edge_no_upper_neighbour(self, gl):
        gl.computer_first_hit(fired_block=(20, 1))
        assert (20, 0) not in gl.around_last_computer_hit_set
        assert (20, 2) in gl.around_last_computer_hit_set

    def test_bottom_edge_no_lower_neighbour(self, gl):
        gl.computer_first_hit(fired_block=(20, 10))
        assert (20, 11) not in gl.around_last_computer_hit_set
        assert (20, 9) in gl.around_last_computer_hit_set

    def test_corner_adds_only_two_neighbours(self, gl):
        gl.computer_first_hit(fired_block=(16, 1))
        assert gl.around_last_computer_hit_set == {(17, 1), (16, 2)}

    def test_corner_bottom_right(self, gl):
        gl.computer_first_hit(fired_block=(25, 10))
        assert gl.around_last_computer_hit_set == {(24, 10), (25, 9)}


# ---------------------------------------------------------------------------
# computer_hits_twice
# ---------------------------------------------------------------------------

class TestComputerHitsTwice:
    def test_horizontal_ship_adds_ends(self, gl):
        gl.last_hits_list[:] = [(20, 5), (21, 5)]
        result = gl.computer_hits_twice()
        assert (19, 5) in result
        assert (22, 5) in result

    def test_vertical_ship_adds_ends(self, gl):
        gl.last_hits_list[:] = [(20, 4), (20, 5)]
        result = gl.computer_hits_twice()
        assert (20, 3) in result
        assert (20, 6) in result

    def test_horizontal_left_edge_no_left_end(self, gl):
        gl.last_hits_list[:] = [(16, 5), (17, 5)]
        result = gl.computer_hits_twice()
        assert (15, 5) not in result
        assert (18, 5) in result

    def test_horizontal_right_edge_no_right_end(self, gl):
        gl.last_hits_list[:] = [(24, 5), (25, 5)]
        result = gl.computer_hits_twice()
        assert (26, 5) not in result
        assert (23, 5) in result

    def test_vertical_top_edge_no_upper_end(self, gl):
        gl.last_hits_list[:] = [(20, 1), (20, 2)]
        result = gl.computer_hits_twice()
        assert (20, 0) not in result
        assert (20, 3) in result

    def test_vertical_bottom_edge_no_lower_end(self, gl):
        gl.last_hits_list[:] = [(20, 9), (20, 10)]
        result = gl.computer_hits_twice()
        assert (20, 11) not in result
        assert (20, 8) in result

    def test_three_hit_horizontal_ship(self, gl):
        gl.last_hits_list[:] = [(20, 5), (21, 5), (22, 5)]
        result = gl.computer_hits_twice()
        assert (19, 5) in result
        assert (23, 5) in result

    def test_returns_set(self, gl):
        gl.last_hits_list[:] = [(20, 5), (21, 5)]
        assert isinstance(gl.computer_hits_twice(), set)


# ---------------------------------------------------------------------------
# update_dotted_and_hit_sets
# ---------------------------------------------------------------------------

class TestUpdateDottedAndHitSets:
    def test_hit_block_added_to_hit_blocks(self, gl):
        gl.update_dotted_and_hit_sets(fired_block=(20, 5), computer_turn=True, diagonal_only=True)
        assert (20, 5) in gl.hit_blocks

    def test_diagonal_only_adds_only_diagonals(self, gl):
        gl.update_dotted_and_hit_sets(fired_block=(20, 5), computer_turn=True, diagonal_only=True)
        # Diagonal neighbours should be dotted
        for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            assert (20 + dx, 5 + dy) in gl.dotted_set
        # Direct neighbours should NOT be dotted (diagonal_only=True)
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            assert (20 + dx, 5 + dy) not in gl.dotted_set

    def test_not_diagonal_only_adds_all_around(self, gl):
        gl.update_dotted_and_hit_sets(fired_block=(20, 5), computer_turn=True, diagonal_only=False)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue
                assert (20 + dx, 5 + dy) in gl.dotted_set | gl.hit_blocks

    def test_hit_block_not_in_dotted_set(self, gl):
        gl.update_dotted_and_hit_sets(fired_block=(20, 5), computer_turn=True, diagonal_only=False)
        assert (20, 5) not in gl.dotted_set

    def test_computer_turn_uses_computer_grid_boundaries(self, gl):
        # Block on the human grid (x=1-10) should not be dotted when computer_turn=True
        gl.update_dotted_and_hit_sets(fired_block=(20, 5), computer_turn=True, diagonal_only=False)
        for x, y in gl.dotted_set:
            assert 16 <= x <= 25

    def test_human_turn_uses_human_grid_boundaries(self, gl):
        gl.update_dotted_and_hit_sets(fired_block=(5, 5), computer_turn=False, diagonal_only=False)
        for x, y in gl.dotted_set:
            assert 1 <= x <= 10

    def test_edge_block_does_not_add_out_of_bounds_dots(self, gl):
        gl.update_dotted_and_hit_sets(fired_block=(16, 1), computer_turn=True, diagonal_only=False)
        for x, y in gl.dotted_set:
            assert 16 <= x <= 25
            assert 1 <= y <= 10

    def test_hit_block_added_to_hit_blocks_for_computer_not_to_shoot(self, gl):
        gl.update_dotted_and_hit_sets(fired_block=(20, 5), computer_turn=True, diagonal_only=True)
        assert (20, 5) in gl.hit_blocks_for_computer_not_to_shoot


# ---------------------------------------------------------------------------
# add_missed_block_to_dotted_set
# ---------------------------------------------------------------------------

class TestAddMissedBlockToDottedSet:
    def test_adds_to_dotted_set(self, gl):
        gl.add_missed_block_to_dotted_set(fired_block=(20, 5))
        assert (20, 5) in gl.dotted_set

    def test_adds_to_computer_not_to_shoot_set(self, gl):
        gl.add_missed_block_to_dotted_set(fired_block=(20, 5))
        assert (20, 5) in gl.dotted_set_for_computer_not_to_shoot


# ---------------------------------------------------------------------------
# is_ship_valid
# ---------------------------------------------------------------------------

class TestIsShipValid:
    def test_valid_ship_no_overlap(self, gl):
        ship_set = {(3, 3), (3, 4)}
        used = {(1, 1), (2, 2)}
        assert gl.is_ship_valid(ship_set=ship_set, blocks_for_manual_drawing=used) is True

    def test_invalid_ship_overlaps_used_block(self, gl):
        ship_set = {(3, 3), (3, 4)}
        used = {(3, 3)}
        assert gl.is_ship_valid(ship_set=ship_set, blocks_for_manual_drawing=used) is False

    def test_empty_ship_is_valid(self, gl):
        assert gl.is_ship_valid(ship_set=set(), blocks_for_manual_drawing={(1, 1)}) is True

    def test_empty_used_blocks_always_valid(self, gl):
        assert gl.is_ship_valid(ship_set={(5, 5)}, blocks_for_manual_drawing=set()) is True


# ---------------------------------------------------------------------------
# validate_ships_numbers
# ---------------------------------------------------------------------------

class TestValidateShipsNumbers:
    def test_can_add_first_ship_of_each_size(self, gl):
        # num_ships_list index = ship_length - 1; value = count already placed
        assert gl.validate_ships_numbers(ship=[1], num_ships_list=[0, 0, 0, 0]) is True      # 1-block, need 4
        assert gl.validate_ships_numbers(ship=[1, 2], num_ships_list=[0, 0, 0, 0]) is True   # 2-block, need 3
        assert gl.validate_ships_numbers(ship=[1, 2, 3], num_ships_list=[0, 0, 0, 0]) is True # 3-block, need 2
        assert gl.validate_ships_numbers(ship=[1, 2, 3, 4], num_ships_list=[0, 0, 0, 0]) is True # 4-block, need 1

    def test_cannot_add_ship_when_quota_reached(self, gl):
        # 4 one-block ships already placed, quota is 4
        assert gl.validate_ships_numbers(ship=[1], num_ships_list=[4, 0, 0, 0]) is False
        # 3 two-block ships already placed, quota is 3
        assert gl.validate_ships_numbers(ship=[1, 2], num_ships_list=[0, 3, 0, 0]) is False
        # 2 three-block ships already placed, quota is 2
        assert gl.validate_ships_numbers(ship=[1, 2, 3], num_ships_list=[0, 0, 2, 0]) is False
        # 1 four-block ship already placed, quota is 1
        assert gl.validate_ships_numbers(ship=[1, 2, 3, 4], num_ships_list=[0, 0, 0, 1]) is False

    def test_can_add_when_one_slot_remains(self, gl):
        assert gl.validate_ships_numbers(ship=[1], num_ships_list=[3, 0, 0, 0]) is True
        assert gl.validate_ships_numbers(ship=[1, 2], num_ships_list=[0, 2, 0, 0]) is True


# ---------------------------------------------------------------------------
# update_used_blocks
# ---------------------------------------------------------------------------

class TestUpdateUsedBlocks:
    def test_adds_ship_blocks_and_surroundings(self, gl):
        collected = set()
        gl.update_used_blocks(ship=[(5, 5)], method=collected.add)
        expected = {(5 + i, 5 + j) for i in range(-1, 2) for j in range(-1, 2)}
        assert collected == expected

    def test_two_block_ship_covers_surroundings(self, gl):
        collected = set()
        gl.update_used_blocks(ship=[(5, 5), (5, 6)], method=collected.add)
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

    def test_miss_returns_false(self, gl):
        computer = self._make_computer()
        ships = [[(3, 3), (3, 4)]]
        ships_copy = [[(3, 3), (3, 4)]]
        ships_set = {(3, 3), (3, 4)}
        result = gl.check_hit_or_miss(
            fired_block=(5, 5),
            opponents_ships_list=ships,
            computer_turn=False,
            opponents_ships_list_original_copy=ships_copy,
            opponents_ships_set=ships_set,
            computer=computer,
        )
        assert result is False

    def test_miss_adds_block_to_dotted_set(self, gl):
        computer = self._make_computer()
        ships = [[(3, 3)]]
        gl.check_hit_or_miss(
            fired_block=(5, 5),
            opponents_ships_list=ships,
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3)]],
            opponents_ships_set={(3, 3)},
            computer=computer,
        )
        assert (5, 5) in gl.dotted_set

    def test_hit_returns_true(self, gl):
        computer = self._make_computer()
        ships = [[(3, 3), (3, 4)]]
        result = gl.check_hit_or_miss(
            fired_block=(3, 3),
            opponents_ships_list=ships,
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3), (3, 4)]],
            opponents_ships_set={(3, 3), (3, 4)},
            computer=computer,
        )
        assert result is True

    def test_hit_removes_block_from_ship_list(self, gl):
        computer = self._make_computer()
        ships = [[(3, 3), (3, 4)]]
        gl.check_hit_or_miss(
            fired_block=(3, 3),
            opponents_ships_list=ships,
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3), (3, 4)]],
            opponents_ships_set={(3, 3), (3, 4)},
            computer=computer,
        )
        assert (3, 3) not in ships[0]

    def test_hit_removes_block_from_ships_set(self, gl):
        computer = self._make_computer()
        ships_set = {(3, 3), (3, 4)}
        gl.check_hit_or_miss(
            fired_block=(3, 3),
            opponents_ships_list=[[(3, 3), (3, 4)]],
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3), (3, 4)]],
            opponents_ships_set=ships_set,
            computer=computer,
        )
        assert (3, 3) not in ships_set

    def test_destroyed_ship_updates_score(self, gl):
        computer = self._make_computer()
        gl.check_hit_or_miss(
            fired_block=(3, 3),
            opponents_ships_list=[[(3, 3)]],
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3)]],
            opponents_ships_set={(3, 3)},
            computer=computer,
        )
        assert gl.computer_destroyed_ships_count[1] == 1
        assert gl.computer_destroyed_ships_count["#"] == 1

    def test_computer_hit_appends_to_last_hits_list(self, gl):
        computer = self._make_computer()
        gl.check_hit_or_miss(
            fired_block=(20, 5),
            opponents_ships_list=[[(20, 5), (20, 6)]],
            computer_turn=True,
            opponents_ships_list_original_copy=[[(20, 5), (20, 6)]],
            opponents_ships_set={(20, 5), (20, 6)},
            computer=computer,
        )
        assert (20, 5) in gl.last_hits_list

    def test_computer_destroy_clears_last_hits_list(self, gl):
        computer = self._make_computer()
        gl.last_hits_list[:] = [(20, 5)]
        gl.check_hit_or_miss(
            fired_block=(20, 5),
            opponents_ships_list=[[(20, 5)]],
            computer_turn=True,
            opponents_ships_list_original_copy=[[(20, 5)]],
            opponents_ships_set={(20, 5)},
            computer=computer,
        )
        assert gl.last_hits_list == []

    def test_human_destroys_computer_ship_adds_to_destroyed_list(self, gl):
        computer = self._make_computer()
        computer.ships = [[(3, 3)]]
        gl.check_hit_or_miss(
            fired_block=(3, 3),
            opponents_ships_list=[[(3, 3)]],
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3)]],
            opponents_ships_set={(3, 3)},
            computer=computer,
        )
        assert computer.ships[0] in gl.destroyed_computer_ships


# ---------------------------------------------------------------------------
# update_destroyed_ships
# ---------------------------------------------------------------------------

class TestUpdateDestroyedShips:
    def test_increments_human_count_on_computer_turn(self, gl):
        gl.update_destroyed_ships(
            ind=0,
            computer_turn=True,
            opponents_ships_list_original_copy=[[(20, 5), (20, 6)]],
        )
        assert gl.human_destroyed_ships_count[2] == 1
        assert gl.human_destroyed_ships_count["#"] == 1

    def test_increments_computer_count_on_human_turn(self, gl):
        gl.update_destroyed_ships(
            ind=0,
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 3), (3, 4), (3, 5)]],
        )
        assert gl.computer_destroyed_ships_count[3] == 1
        assert gl.computer_destroyed_ships_count["#"] == 1

    def test_adds_surrounding_dots_for_destroyed_ship(self, gl):
        gl.update_destroyed_ships(
            ind=0,
            computer_turn=False,
            opponents_ships_list_original_copy=[[(3, 5)]],
        )
        # The function calls update_dotted_and_hit_sets with diagonal_only=False
        # so surrounding blocks should be in dotted_set or hit_blocks
        assert len(gl.dotted_set | gl.hit_blocks) > 0
