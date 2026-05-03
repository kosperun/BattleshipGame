"""Creates human ships automatically."""

from random import choice, randint

from elements.constants import GRID_SIZE, Y_MAX, Y_MIN


class AutoShips:
    """
    Randomly create all player's ships on a grid
    ----------
    Attributes:
        offset (int): Where the grid starts (in number of blocks)
                (typically 0 for computer and 15 for human)
        available_blocks (set of tuples): coordinates of all blocks
                that are available for creating ships (updated every time a ship is created)
        ships_set (set of tuples): all blocks that are occupied by ships
        ships (list of lists): list of all individual ships (as lists)
    ----------
    Methods:
        __create_start_block(available_blocks):
            Randomly chooses a block from which to start creating a ship.
            Randomly chooses horizontal or vertical type of a ship
            Randomly chooses direction (from the start block) - straight or reverse
            Returns three randomly chosen values
        __create_ship(number_of_blocks, available_blocks):
            Creates a ship of given length (number_of_blocks) starting from the start block
                returned by the previous method, using type of ship and direction (changing it
                if going outside of grid) returned by previous method.
                Checks if the ship is valid (not adjacent to other ships and within the grid)
                and adds it to the list of ships.
            Returns: a list of tuples with a new ship's coordinates
        __get_new_block_for_ship(self, coor, direction, orientation, ship_coordinates):
            Checks if new individual blocks that are being added to a ship in the previous method
                are within the grid, otherwise changes the direction.
            Returns:
                direction (int): straight or reverse
                incremented/decremented coordinate of the last/first block in a ship under construction
        __is_ship_valid(new_ship):
            Check if all of a ship's coordinates are within the available blocks set.
            Returns: True or False
        __add_new_ship_to_set(new_ship):
            Adds all blocks in a ship's list to the ships_set
        __update_available_blocks_for_creating_ships(new_ship):
            Removes all blocks occupied by a ship and around it from the available blocks set
        __populate_grid():
            Creates needed number of each type of ships by calling the create_ship method.
                Adds every ship to the ships list, ships_set and updates the available blocks.
            Returns: the list of all ships
    """

    def __init__(self, offset: int) -> None:
        """
        Parameters:
        offset (int): Where the grid starts (in number of blocks)
                (typically 0 for computer and 15 for human)
        available_blocks (set of tuples): coordinates of all blocks
                that are avaiable for creating ships (updated every time a ship is created)
        ships_set (set of tuples): all blocks that are occupied by ships
        ships (list of lists): list of all individual ships (as lists)"""

        self.offset = offset
        self.available_blocks = {(x, y) for x in range(1 + self.offset, GRID_SIZE + 1 + self.offset) for y in range(Y_MIN, Y_MAX + 1)}
        self.ships_set = set()
        self.ships = self.__populate_grid()
        self.orientation = None
        self.direction = None

    def __create_start_block(self, available_blocks: set[tuple]) -> tuple:
        """
        Randomly chooses a block from which to start creating a ship.
        Randomly chooses horizontal or vertical type of a ship
        Randomly chooses direction (from the start block) - straight or reverse
        Args:
            available_blocks (set of tuples): coordinates of all blocks
                that are available for creating ships (updated every time a ship is created)
        Returns:
            int: x coordinate of a random block
            int: y coordinate of a random block
            int: 0=horizontal (change x), 1=vertical (change y)
            int: 1=straight, -1=reverse
        """
        self.orientation = randint(0, 1)
        # -1 is left or down, 1 is right or up
        self.direction = choice((-1, 1))
        x, y = choice(tuple(available_blocks))
        return x, y, self.orientation, self.direction

    def __create_ship(self, number_of_blocks: int, available_blocks: set[tuple]) -> list:
        """
        Creates a ship of given length (number_of_blocks) starting from the start block
                returned by the previous method, using type of ship and direction (changing it
                if going outside of grid) returned by previous method.
                Checks if the ship is valid (not adjacent to other ships and within the grid)
                and adds it to the list of ships.
        Args:
            number_of_blocks (int): length of a needed ship
            available_blocks (set): free blocks for creating ships
        Returns:
            list: a list of tuples with a new ship's coordinates
        """
        ship_coordinates = []
        x, y, self.orientation, self.direction = self.__create_start_block(available_blocks)
        for _ in range(number_of_blocks):
            ship_coordinates.append((x, y))
            if not self.orientation:
                self.direction, x = self.__get_new_block_for_ship(x, self.direction, self.orientation, ship_coordinates)
            else:
                self.direction, y = self.__get_new_block_for_ship(y, self.direction, self.orientation, ship_coordinates)
        if self.__is_ship_valid(ship_coordinates):
            return ship_coordinates
        return self.__create_ship(number_of_blocks, available_blocks)

    def __get_new_block_for_ship(self, coor: int, direction: int, orientation: int, ship_coordinates: list) -> tuple:
        """
        Checks if new individual blocks that are being added to a ship in the previous method
                are within the grid, otherwise changes the direction.
        Args:
            coor (int): x or y coordinate to increment/decrement
            direction (int): 1 or -1
            orientation (int): 0 or 1
            ship_coordinates (list): coordinates of unfinished ship
        Returns:
            direction (int): straight or reverse
            incremented/decremented coordinate of the last/first block in a ship under construction (int)
        """
        self.direction = direction
        self.orientation = orientation
        if (coor <= 1 - self.offset * (self.orientation - 1) and self.direction == -1) or (
            coor >= 10 - self.offset * (self.orientation - 1) and self.direction == 1
        ):
            self.direction *= -1
            return self.direction, ship_coordinates[0][self.orientation] + self.direction
        return self.direction, ship_coordinates[-1][self.orientation] + self.direction

    def __is_ship_valid(self, new_ship: list) -> bool:
        """
        Check if all of a ship's coordinates are within the available blocks set.
        Args:
            new_ship (list): list of tuples with a newly created ship's coordinates
        Returns:
            bool: True or False
        """
        ship = set(new_ship)
        return ship.issubset(self.available_blocks)

    def __add_new_ship_to_set(self, new_ship: list) -> None:
        """
        Adds all blocks in a ship's list to the ships_set
        Args:
            new_ship (list): list of tuples with a newly created ship's coordinates
        """
        self.ships_set.update(new_ship)

    def __update_available_blocks_for_creating_ships(self, new_ship: list) -> None:
        """
        Removes all blocks occupied by a ship and around it from the available blocks set
        Args:
            new_ship ([type]): list of tuples with a newly created ship's coordinates
        """
        for elem in new_ship:
            for k in range(-1, 2):
                for m in range(-1, 2):
                    if self.offset < (elem[0] + k) < GRID_SIZE + 1 + self.offset and Y_MIN - 1 < (elem[1] + m) < Y_MAX + 1:
                        self.available_blocks.discard((elem[0] + k, elem[1] + m))

    def __populate_grid(self) -> list:
        """
        Creates needed number of each type of ships by calling the create_ship method.
                Adds every ship to the ships list, ships_set and updates the available blocks.
        Returns:
            list: the 2d list of all ships
        """
        ships_coordinates_list = []
        for number_of_blocks in range(4, 0, -1):
            for _ in range(5 - number_of_blocks):
                new_ship = self.__create_ship(number_of_blocks, self.available_blocks)
                ships_coordinates_list.append(new_ship)
                self.__add_new_ship_to_set(new_ship)
                self.__update_available_blocks_for_creating_ships(new_ship)
        return ships_coordinates_list
