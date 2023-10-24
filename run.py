# battleship.py test.py – this code is for testing CPU vs CPU game

# Import required libraries
import random  # For generating random numbers
import copy  # For creating deep copies of data structures
import os  # For clearing the terminal screen
import time  # For time-related functionalities
import re  # For handling user input expressions
from difflib import SequenceMatcher
from typing import List, Optional, Union, Dict, Tuple, Callable
from icecream import ic
import math
import shutil
from collections import defaultdict

# Constants for map dimensions and default symbol
# DEFAULT_MAP_SETTINGS consist of 4 values:
# 1. Map Height - number of rows
# 2. Map Width - number of columns
# 3. Default symbol displayed on map, o prefer ? - as it is unknown what is
# hiding there
# 4. Gaps - gabes between ships, default value = True
DEFAULT_MAP_SETTINGS = [10,10,"?",True]

# DEFAULT_COORDINATE_STYLE consist of 2 lists:
# 1st: default input output style, row - column, player can change it in
# settings to be column - row
# 2nd: Row and column indexes labels, player can change it to letters
DEFAULT_COORDINATES_STYLE = [["Column", "Row"],
                             [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                               14, 15, 16, 17, 18, 19],
                              [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                               14, 15, 16, 17, 18, 19]]]

# ANSI color codes used for visual representation of different ship statuses
DEFAULT_COLORS: Dict[str, str] = {
    "DarkYellow": "\u001b[33m",
    "DarkBlue": "\u001b[34m",
    "DarkGreen": "\u001b[32m",
    "DarkRed": "\u001b[31m",
    "LightGray": "\u001b[37m",
    "Reset": "\u001b[0m",
}

# Unicode symbols used for visual representation of different ship statuses
DEFAULT_SHIP_SYMBOLS: Dict[str, List[str]] = {
    "Single": [chr(0x25C6)],
    "Horizontal": [chr(0x25C0), chr(0x25A4)],
    "Vertical": [chr(0x25B2), chr(0x25A5)],
    "Hit": [chr(0x25A6)],
    "Miss": [chr(0x2022)]
}

# Commands dictionary
# -------------------

# Creating a dictionary of commands and their possible similar expressions
# that a user might use
commands_dictionary = {
    'add ship': ['insert ship', 'place ship', 'ship add'],
    'delete ship': ['remove ship', 'erase ship', 'ship delete'],
    'change map size': ['resize map', 'adjust map', 'map dimensions'],
    'print fleet': ['show fleet', 'display fleet', 'fleet view'],
    'modify ship': ['edit ship', 'update ship', 'ship modify'],
    'modify fleet': ['edit fleet', 'update fleet', 'fleet modify'],
    'gaps between ships': ['ship spacing', 'distance between ships',
                           'ship gaps'],
    'start game': ['begin game', 'launch game', 'game start'],
    'reset settings': ['default settings', 'clear settings', 'settings reset'],
    'change coordinate labels': ['modify grid labels',
                                 'edit coordinate names', 'labels change']
}


# Helper Functions
# ----------------

def clear_terminal():
    """
    Clear the terminal screen.
    This function uses different commands for POSIX (Unix/Linux/macOS) and
    Windows systems.
    """
    if os.name == 'posix':  # Unix/Linux/macOS
        os.system('clear')
    elif os.name == 'nt':  # Windows
        os.system('cls')


# User Input Processing Functions
# -------------------------------

def input_normalize_string(text_input: str) -> str:
    """
    Normalize the command string for easier comparison.

    This function tokenizes the command string, sorts the tokens,
    and converts them to lowercase for case-insensitive comparison.

    Parameters:
        text_input (str): The command string to be normalized.

    Returns:
        str: The normalized command string.
    """
    return ' '.join(sorted(text_input.lower().split()))


def levenshtein_ratio(first_string: str, second_string: str) -> float:
    """
    Calculate the Levenshtein distance ratio between two strings.

    The ratio is a measure of similarity between two strings.
    A ratio of 1 means the strings are identical.

    Parameters:
        first_string (str): The first string for comparison.
        second_string (str): The second string for comparison.

    Returns:
        float: The Levenshtein distance ratio between the two strings.
    """
    return SequenceMatcher(None, first_string, second_string).ratio()


def find_best_match(user_input: str, possible_commands: List[str]) -> (
        Optional)[str]:
    """
    Find the best matching command based on user input and a list of possible
    commands.

    This function first normalizes the user input and each possible command.
    It then calculates the Levenshtein distance ratio between the normalized
    user input and each possible command to find the best match.

    Parameters:
        user_input (str): The user's input string
        possible_commands (List[str]): A list of possible commands to match
            against.

    Returns:
        Optional[str]:
        The best-matching command, or:
        None if no-reasonable match is found.
    """
    # Normalize the user input for comparison
    user_input = input_normalize_string(user_input)

    # Initialize variables to store the best match and its Levenshtein
    # distance ratio
    max_ratio = -1
    best_match = None

    # Loop through each possible command to find the best match
    for command in possible_commands:
        # Normalize the possible command for comparison
        normalized_command = input_normalize_string(command)

        # Calculate the Levenshtein distance ratio between the normalized
        # user input and the possible command
        ratio = levenshtein_ratio(user_input, normalized_command)

        # Update the best match and its ratio if the current ratio is higher
        if ratio > max_ratio:
            max_ratio = ratio
            best_match = command

    # A threshold is set for the Levenshtein distance ratio to consider a
    # match as reasonable This threshold can be adjusted as needed
    if max_ratio > 0.6:
        return best_match
    else:
        return None


# Ship managing functions:
# ------------------------


class Ship:
    """Represents a single ship in the Battleship game."""

    # noinspection PyAttributeOutsideInit
    def __init__(self, name: str, size: int) -> None:
        """
        Initialize a Ship object with its name and size.

        Parameters:
            name (str): The name of the ship (for example,
        "Destroyer").
            size (int): The size of the ship, representing how
        many cells it occupies.

        Variables:
            name (str): The name of the ship.
            size (int): The size of the ship in cells.
            cell_coordinates (List[Tuple[int, int]]): Coordinates (x, y) for
                each cell of the ship.
            sunk (bool): Indicates whether the ship is sunk or not.
            color (str): ANSI color code for the ship, based on its status.
            alignment (str): alignment of the ship ("Horizontal" or
                "Vertical").
        """
        self.name = name
        self.size = size
        self.cell_coordinates = []
        self.sunk = False
        self.color = None
        self.alignment = None
        self.deployed = False

        # Setting initial color and alignment based on ship size
        if self.size == 1:
            self.alignment = "Single"
            self.color = DEFAULT_COLORS["DarkYellow"]

    def set_cell_coordinates(self, coordinates) -> None:
        """
        Set the coordinates for each cell of the ship.

        Parameters: coordinates (List[List[int, int]]): A list of (x,
            y) tuples representing the coordinates for each cell.
        """
        self.cell_coordinates = coordinates

    def get_coordinates_by_single_coordinate(
            self, single_coordinate: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get the full list of coordinates for the ship based on a single
        coordinate.

        Parameters:
            single_coordinate (Tuple[int, int]): The single (x, y)
                coordinate to search for within the ship's cell_coordinates.

        Returns:
            List[Tuple[int, int]]: A list of (x, y) coordinates
                associated with the ship based on the provided single
                coordinate.

        This method searches for the provided single coordinate within the
        ship's cell_coordinates
        and returns the full list of coordinates
        associated with the ship.
        """
        coordinates_list = []
        if single_coordinate in self.cell_coordinates:
            coordinates_list = self.cell_coordinates
        return coordinates_list

    def set_alignment(self, alignment: str) -> None:
        """
        Set the alignment of the ship and update its color based on the
        alignment.

        Parameters:
            alignment (str): The alignment of the ship, either
            "Horizontal" or "Vertical".
        """
        self.alignment = alignment
        if alignment == "Horizontal":
            self.color = DEFAULT_COLORS["DarkBlue"]
        elif alignment == "Vertical":
            self.color = DEFAULT_COLORS["DarkGreen"]

    def set_sunk(self) -> None:
        """
        Update the ship's status to indicate that it has been sunk.

        This function performs two key tasks: 1. It changes the 'sunk'
        attribute of the Ship object to True, indicating that the ship is
        now sunk. 2. It updates the ship's color to red, signifying its sunk
        status on the game map.

        Note: Once a ship is marked as sunk, its color will remain red
        regardless of other status changes or updates.
        """
        self.sunk = True
        self.color = DEFAULT_COLORS["DarkRed"]

    def get_symbols(self) -> List[str]:
        """
        Get symbols for all ship cells based on its hit status and alignment.

        Returns:
            List[str]: A list of symbols for all cells of the ship,
                colored based on the ship's current status.

        This function performs the following key tasks:
            1. Determine the color based on whether the ship is sunk or not.
            2. Handle the case where the color or symbols are not defined.
            3. Determine the appropriate symbol for each cell of the ship
            based on its size and alignment.
            4. Generate a list of colored symbols.

        Note:
            The color of each symbol will be red if the ship is sunk.
            Warnings will be printed to the console if the color or symbols
            are not defined.
        """

        # Determine the color based on sunk status
        color = DEFAULT_COLORS.get("DarkRed") if self.sunk else self.color

        # Handle the case where color is None
        if color is None:
            print("Warning: color is None. Using default.")
            color = DEFAULT_COLORS.get("Default", "default_fallback_color")

        # Determine the symbol key based on the size and alignment of the ship
        symbol_key = self.alignment

        # Get the list of symbols for the ship based on its size and alignment
        symbols = DEFAULT_SHIP_SYMBOLS.get(symbol_key, ["default_symbol"])

        # Handle the case where symbols is None or empty
        if not symbols:
            print("Warning: symbols list is empty. Using default.")
            symbols = ["default_symbol"]

        # Initialize colored_symbols as an empty list
        colored_symbols = []

        # Generate colored symbols based on ship size and status
        for i in range(self.size):
            # Choose the appropriate symbol based on position
            symbol = symbols[0] if i == 0 else symbols[1]

            # Color the symbol and append to the list
            colored_symbols.append(color + symbol + DEFAULT_COLORS["Reset"])
        return colored_symbols


class Fleet:
    """
    Manages a collection of Ship objects, encapsulating them in a fleet
    for the Battleship game.
    """

    def __init__(self) -> None:
        """
        Initialize an empty Fleet object.
        Variables:
            ships (List[Ship]):
             A list to store the Ship objects that belong to this fleet.
        """
        self.ships: List[Ship] = []

    def add_ship(self, ship: Ship) -> None:
        """
        Add a Ship object to the fleet.
        Parameters:
            ship (Ship): The Ships object to be added to the fleet.
        """
        self.ships.append(ship)

    def remove_ship(self, name: str) -> bool:
        """
        Remove one instance of a ship by its name from the fleet.
        Parameters:
            name (str): The name of the ship to be removed.
        Returns:
            bool: True if the ship was successfully removed, False otherwise.
        """
        for i, ship in enumerate(self.ships):
            if ship.name == name:
                del self.ships[i]
                return True
        return False

    def get_ship(self, name: str, is_deployed: bool = False) \
            -> Union[Ship, None]:
        """
        Retrieve a Ship object from the fleet by its name and deployment
        status.

        Parameters:
            name (str): The name of the ship to retrieve.
            is_deployed (bool): Whether to retrieve a deployed or not deployed
                ship. Defaults to False, which retrieves not deployed ships.

        Returns:
            Ship or None: Returns the Ship object if found; returns None if
            not found.
        """
        for ship in self.ships:
            if ship.name == name and ship.deployed == is_deployed:
                return ship
        return None

    def get_ship_quantity(self, name: str) -> int:
        """
        Get the quantity of a specific type of ship in the fleet.
        Parameters:
            name (str): The name of the type of ship to count.
        Returns:
            int: The number of ships of this type in the fleet.
        """
        count = 0
        for ship in self.ships:
            if ship.name == name:
                count += 1
        return count

    def get_ship_quantity_by_sunk_status(self, name: str,
                                         is_sunk: bool = False) -> int:
        """
        Get the quantity of a specific type of ship in the fleet based on
        its sunk status.

        Parameters:
            name (str): The name of the type of ship to count.
            is_sunk (bool, optional): Whether to count ships that are sunk.
                Default is False, which counts not-sunk ships.

        Returns:
            int: The number of ships of this type in the fleet based on
                sunk status.
        """
        count = 0
        for ship in self.ships:
            if ship.name == name and ship.sunk == is_sunk:
                count += 1
        return count

    def get_ship_quantity_by_deployed_status(self, name: str,
                                             is_deployed: bool = False) -> int:
        """
        Get the quantity of a specific type of ship in the fleet based on 
        its deployed status.

        Parameters:
            name (str): The name of the type of ship to count.
            is_deployed (bool, optional): Whether to count ships that are
                deployed. Default is False, which counts not-deployed ships.

        Returns:
            int: The number of ships of this type in the fleet based on 
                deployed status.
        """
        count = 0
        for ship in self.ships:
            if ship.name == name and ship.deployed == is_deployed:
                count += 1
        return count

    def get_biggest_ship_by_deployed_status(self, is_deployed: bool = False) \
            -> Union[Ship, None]:
        """
        Get the biggest ship in the fleet based on the deployed status.

        Parameters:
            is_deployed (bool, optional): Whether to consider deployed ships.
                Default is False, which considers not-deployed ships.

        Returns:
            Union[Ship, None]: Returns the biggest deployed ship object if
            found;
            returns None if no deployed ships are found.

        This function iterates through the ships in the fleet, considering only
        the deployed or not-deployed ships based on the `is_deployed`
        parameter.
        It calculates the size of each ship and keeps track of the biggest one.
        If a deployed ship is found, it returns the entire Ship object;
        otherwise, it returns None.
        """
        biggest_ship = None
        biggest_size = 0

        for ship in self.ships:
            if ship.deployed == is_deployed and ship.size > biggest_size:
                biggest_ship = ship
                biggest_size = ship.size

        return biggest_ship

    def __str__(self) -> str:
        """
        Provide a string representation of the Fleet object.

        This method iterates through all the Ship objects in the fleet,
        enumerating them and displaying key attributes like name, size,
        coordinates, sunk status, and deployment status.

        Returns:
            str: A string representation summarizing the fleet's status.
        """

        # Initialize an output string with a title.
        output = "Fleet Status:\n"

        # Loop through each Ship object in the fleet.
        # The enumerate function provides an index starting from 1 for each
        # ship.
        for i, ship in enumerate(self.ships, 1):
            # Append the index, name, and size of each ship to the output
            # string.
            output += f"{i}. {ship.name} (Size: {ship.size})\n"

            # Append the coordinates of each ship to the output string.
            output += f"   Coordinates: {ship.cell_coordinates}\n"

            # Check the sunk status of the ship and append it to the output
            # string.
            output += f"   Sunk: {'Yes' if ship.sunk else 'No'}\n"

            # Check the deployment status of the ship and append it to the
            # output string.
            output += f"   Deployed: {'Yes' if ship.deployed else 'No'}\n"

        # Return the fully constructed output string.
        return output

    def __init__(self):
        # Initialize your ships attribute here, for example
        self.ships = []

    def gather_basic_info(self):
        """
        Gather basic information about each ship in the fleet.

        Returns:
            List[dict]: A list of dictionaries containing basic information about each ship.
        """
        ship_info = {}
        for ship in self.ships:
            name = ship.name
            if name not in ship_info:
                ship_info[name] = {"name": name, "size": ship.size, "qty": 0}
            ship_info[name]["qty"] += 1
        return [info for info in ship_info.values()]

    def add_deployed_qty(self, ship_info_list):
        """
        Add the quantity of deployed ships to the ship information list.

        Parameters:
            ship_info_list (List[dict]): The list containing ship information.
        """
        for info in ship_info_list:
            info['deployed_qty'] = sum(ship.deployed for ship in self.ships if ship.name == info['name'])

    def add_sunk_qty(self, ship_info_list):
        """
        Add the quantity of sunk ships to the ship information list.

        Parameters:
            ship_info_list (List[dict]): The list containing ship information.
        """
        for info in ship_info_list:
            info['sunk_qty'] = sum(ship.sunk for ship in self.ships if ship.name == info['name'])

    def format_coordinates(self, coordinates, game_coordinate_style):
        """
        Format the coordinates according to the game's coordinate style.

        Parameters:
            coordinates (List[tuple]): List of coordinates.
            game_coordinate_style (List): The game's coordinate style.

        Returns:
            List[str]: List of formatted coordinates.
        """
        formatted_coordinates = []
        for coord_set in coordinates:
            formatted_set = []
            for (row, col) in coord_set:
                row_label = game_coordinate_style[1][0][row]
                col_label = game_coordinate_style[1][1][col]
                if game_coordinate_style[0] == ["Row", "Column"]:
                    formatted_set.append(f"({row_label},{col_label})")
                else:
                    formatted_set.append(f"({col_label},{row_label})")
            formatted_coordinates.append(' '.join(formatted_set))
        return formatted_coordinates

    def add_coordinates_condition(self, ship_info_list, condition, game_coordinate_style):
        """
        Add coordinates condition to the ship information list.

        Parameters:
            ship_info_list (List[dict]): The list containing ship information.
            condition (str): The condition to filter the coordinates.
            game_coordinate_style (List): The game's coordinate style.
        """
        for info in ship_info_list:
            coordinates = [ship.cell_coordinates for ship in self.ships if
                           ship.name == info['name'] and getattr(ship, condition.split('_')[0])]
            info[condition] = self.format_coordinates(coordinates, game_coordinate_style)

    def print_fleet(self, conditions=[], game_coordinate_style=None):
        """
        Print the fleet information based on given conditions.

        Parameters:
            conditions (List[str], optional): List of conditions to filter the information.
            game_coordinate_style (List, optional): The game's coordinate style.
        """
        ship_info_list = self.gather_basic_info()

        # Map conditions to corresponding functions
        condition_func_map: dict[str, Callable] = {
            'deployed_qty': self.add_deployed_qty,
            'sunk_qty': self.add_sunk_qty,
            'deployed_coordinates': lambda ship_info:
            self.add_coordinates_condition(ship_info, 'deployed_coordinates', game_coordinate_style),
            'sunk_coordinates': lambda ship_info:
            self.add_coordinates_condition(ship_info, 'sunk_coordinates', game_coordinate_style)
        }

        # Apply each condition function to ship_info_list
        for condition in conditions:
            func = condition_func_map.get(condition)
            if func:
                func(ship_info_list)

        # Print the table header
        print("{:<20}{:<10}{:<10}".format("Name", "Size", "Qty"), end="")
        for condition in conditions:
            header = condition.split('_')[1][:3].upper()
            print(f"{header:<10}", end="")
        print()

        # Print the ship information
        for info in ship_info_list:
            print(f"{info['name']:<20}{info['size']:<10}{info['qty']:<10}", end="")
            for condition in conditions:
                if 'coordinates' not in condition:
                    print(f"{info.get(condition, 0):<10}", end="")
            print()

            for condition in conditions:
                if 'coordinates' in condition:
                    for coord_str in info.get(condition, []):
                        print(f"    {coord_str}")




def create_default_fleet() -> Fleet:
    """
    Create a default fleet with predefined ships.

    Returns:
        Fleet: A Fleet object populated with default Ship objects.

    This function performs the following key tasks:
    1. Initializes an empty Fleet object.
    2. Defines a list of default ships, specifying their names, sizes,
    and quantities.
    3. Iterates through the list of default ships,
    creating Ship objects and adding them to the fleet.
    """
    # Initialize an empty Fleet object
    fleet = Fleet()

    # Define a list of default ships with their names, sizes, and quantities
    default_ships = [
        {"name": "AircraftCarrier", "size": 5, "qty": 1},
        {"name": "Battleship", "size": 4, "qty": 1},
        {"name": "Cruiser", "size": 3, "qty": 1},
        {"name": "Submarine", "size": 3, "qty": 1},
        {"name": "Destroyer", "size": 2, "qty": 2},
        {"name": "Tug Boat", "size": 1, "qty": 4},

    ]

    # Iterate through the list of default ships
    for ship_info in default_ships:
        # Create and add each Ship object to the fleet based on its quantity
        for _ in range(ship_info["qty"]):
            ship = Ship(ship_info["name"], ship_info["size"])
            fleet.add_ship(ship)

    return fleet


# Map manipulating functions
# --------------------------
def create_map(height: int, width: int, symbol: str) -> List[List[str]]:
    """
    Initialize a 2D map with a default symbol.

    Parameters:
        height (int): The height of the map in cells.
        width (int): The width of the map in cells.
        symbol (str): The default symbol to fill each cell of the map with.

    Returns:
        List[List[str]]: A 2D list (map) where each cell is initialized
            with the given symbol.

    This function performs two key tasks: 1. Creates a 2D list (map) with
    dimensions specified by `height` and `width`. 2. Fill each cell in the
    2D list with the default `symbol`.
    """

    return [[symbol for _ in range(height)] for _ in range(width)]


def print_map(map_game):
    """
    Print the game map in a human-readable format.

    Args:
        map_game (list): A 2D list representing the game map,
                         where each cell contains the status of a ship
                         or water.

    Output:
        The function will print the game map to the console.
    """
    # Global variables for row and column indexes
    global DEFAULT_COORDINATES_STYLE

    # Print column headers (0, 1, 2, ..., N)
    print("   ", end="")
    for col_index in range(len(map_game[0])):
        print(f"{DEFAULT_COORDINATES_STYLE[1][0][col_index]}  ", end="")

    # Print a separator line between headers and table
    print("\n   " + "=" * (len(map_game[0]) * 3))

    # Loop through each row
    for row_index, row in enumerate(map_game):
        # Print row header
        print(f"{DEFAULT_COORDINATES_STYLE[1][1][row_index]} |", end=" ")

        # Loop through each cell in the row
        for value in row:
            # Print the cell value followed by two spaces
            print(f"{value}  ", end="")

        # Move to the next line at the end of each row
        print()


def find_max_label_length(map_size: int,
                          index_label: List[Union[int, str]]) -> int:
    """
    Find the maximum length of index labels for a given map size.

    Args:
        map_size: The size of the map (either height or width).
        index_label: List of labels for row or column indexes.

    Returns:
        int: Maximum length of the index labels for the given map size.
    """

    # Initialize max_length to 0
    max_length = 0

    # Loop through the index_label list up to map_size to find the maximum
    # label length
    for i in range(map_size):
        label_length = len(str(index_label[i]))

        # Update max_length if the current label is longer
        if label_length > max_length:
            max_length = label_length

    return max_length


def print_two_maps(map_left: List[List[str]], map_right: List[List[str]],
                   label_left: str, label_right: str, row_index_label,
                   column_index_label, gap: int = 10) -> None:
    """
    Print two 2D maps side-by-side with dynamically centered labels and a
    customizable gap.

    Args:
        map_left : A 2D list representing the first map.
        map_right: A 2D list representing the second map.
        label_left: Label for the first map.
        label_right: Label for the second map.
        row_index_label: Label indicating row index of the map
        column_index_label: Label indicating column index of the map

        gap: Number of blank spaces between the two maps. Default is 10.
    """

    # Constants for character dimensions and formatting
    char_width = len("X")

    # Calculate the maximum number of digits in row and column indexes
    num_digits_map_width = find_max_label_length(len(map_left[0]),
                                                 column_index_label)
    num_digits_map_height = find_max_label_length(len(map_left),
                                                  row_index_label)

    # Create a string of blank spaces for the gap between maps
    gap_str = ' ' * gap

    # Calculate the left-side offset for aligning map and row indexes
    row_index_separator = " | "
    print_map_left_offset = " " * (
            num_digits_map_height + len(row_index_separator))

    # Center-align the labels for both maps
    number_char_table_total = len(map_left[0]) * (
            num_digits_map_width + char_width + 1)
    label_left_centered = label_left.center(number_char_table_total)
    label_right_centered = label_right.center(number_char_table_total)

    # Print the centered labels for both maps
    print(f"{print_map_left_offset}{label_left_centered}{gap_str}"
          f"{print_map_left_offset}{label_right_centered}")

    # Print column headers for both maps
    print(print_map_left_offset, end=" ")
    for col_index in range(len(map_left[0])):
        print(str(column_index_label[col_index]).rjust(num_digits_map_width +
                                                       char_width), end=" ")
    print(gap_str, print_map_left_offset, end="")
    for col_index in range(len(map_right[0])):
        print(str(column_index_label[col_index]).rjust(
            num_digits_map_width + char_width), end=" ")
    print()

    # Print the horizontal separator line
    separator_length_left = len(map_left[0]) * (
            num_digits_map_width + char_width + 1)
    separator_length_right = len(map_right[0]) * (
            num_digits_map_width + char_width + 1)
    print(print_map_left_offset + "=" * separator_length_left, end=gap_str)
    print(" " + print_map_left_offset + "=" * separator_length_right)

    # Loop through each row to print map values
    for row_index, (row_left, row_right) in enumerate(
            zip(map_left, map_right)):
        print(str(row_index_label[row_index]).rjust(num_digits_map_height + 1),
              end=row_index_separator)
        for value in row_left:
            width = len(str(value))
            print(str(value).rjust(
                num_digits_map_width + char_width - (char_width - width)),
                end=" ")
        print(gap_str, end="")
        print(str(row_index_label[row_index]).rjust(num_digits_map_height + 1),
              end=row_index_separator)
        for value in row_right:
            width = len(str(value))
            print(str(value).rjust(
                num_digits_map_width + char_width - (char_width - width)),
                end=" ")
        print()


# Corrected function to include map_width and map_height in calculations
def map_calculate_max_dimensions(map_height: int, map_width: int, gap: int,
                                 row_index_label: List[Union[int, str]],
                                 column_index_label: List[
                                     Union[int, str]]) -> (int, int):
    """
    Calculate the maximum map dimensions that can fit in the terminal.

    Args:
        map_height (int): Current map height.
        map_width (int): Current map width.
        gap (int): Gap between the two maps.
        row_index_label (List[Union[int, str]]): Labels for the row indexes.
        column_index_label (List[Union[int, str]]): Labels for the column
        indexes.

    Returns:
        tuple: (max_map_width, max_map_height)
    """

    # Simulated terminal dimensions;
    # normally you would use shutil.get_terminal_size()
    terminal_size = (100, 30)  # (columns, lines)
    terminal_width, terminal_height = terminal_size

    # Width of each map cell (including spaces)
    cell_width = len("X") + 2  # "X" plus two spaces

    # Number of characters needed for row and column labels
    row_label_width = find_max_label_length(map_height, row_index_label)
    col_label_width = find_max_label_length(map_width, column_index_label)

    # Calculate max map width
    max_map_width = (terminal_width - gap - 2 * (row_label_width + 3)) // (
            2 * (col_label_width + cell_width))

    # Calculate max map height
    max_map_height = terminal_height - 3  # 1 row for column labels, 1 for
    # separator, 1 for map label

    return max_map_width, max_map_height


# CPU game play functions
# -----------------------


def cpu_deploy_all_ships(map_game: List[List[str]], fleet: Fleet, gaps=True):
    """
    Deploy all CPU ships on the map.

    This function deploys all the CPU's ships on a given game map based on
    the fleet configuration. It uses various helper functions to find suitable
    locations and alignments for each ship.

    Args:
        map_game (list): 2D map for the CPU.
        fleet (Fleet): Contains the CPU's fleet information.
        gaps (bool): By default gas are enabled on map, if player disables,
        it will be passed to this function

    Returns:
        bool: True if deployment is successful, False otherwise.
    """
    while True:
        try:
            # Get information about the biggest not deployed ship from the
            # fleet
            ship_obj = fleet.get_biggest_ship_by_deployed_status(False)

            if ship_obj is None:
                # If no ships left to deploy, break the loop and return True
                return True  # Deployment is complete
            else:
                ship_size = ship_obj.size

                # Attempt to deploy the ship and get alignment and coordinates
                return_result = cpu_deploy_single_ship(map_game, ship_size)

                if return_result is False:
                    # Can't deploy ships, no coordinates found, return False
                    return False

                alignment, coordinates_list = return_result

            ship_obj.set_cell_coordinates(coordinates_list)
            ship_obj.set_alignment(alignment)
            ship_obj.deployed = True

            # Get ship symbols and update the map
            symbols_list = ship_obj.get_symbols()

            if gaps:
                symbol = "x"

                map_game = map_allocate_empty_space_for_ship(map_game,
                                                             coordinates_list,
                                                             symbol)

            map_game = map_show_symbols(map_game, coordinates_list,
                                        symbols_list)
            print_map(map_game)
            print(fleet)

        except Exception as e:
            # Handle exceptions if needed
            print("An error occurred:", str(e))
            return False  # Return False on error


def map_show_symbols(map_game: List[List[str]],
                     coordinates_list: List[Tuple[int, int]],
                     symbols_list: List[str]) -> List[List[str]]:
    """
    Update the game map by placing the symbols of a ship at the specified
    coordinates.

    Parameters:
        map_game (List[List[str]]): The 2D game map.
        coordinates_list (List[Tuple[int, int]]): A list of coordinates
        where the ship will be placed.
        symbols_list (List[str]): A list of symbols that represent the
        ship's cells.

    Returns:
        List[List[str]]: The updated 2D game map.

    This function iterates over each coordinate in `coordinates_list`,
    retrieves the corresponding symbol from `symbols_list`, and updates
    `map_game` at that coordinate with the symbol.

    Note:
        - The length of `coordinates_list` and `symbols_list` should be the
        same.
        - Each coordinate in `coordinates_list` is a tuple (row, column)
        representing a cell in the 2D game map.
        - Each symbol in `symbols_list` is a string that represents the
        appearance of a ship cell.
    """

    # Loop through the list of coordinates and symbols to update the game map
    for i in range(len(coordinates_list)):
        row, column = coordinates_list[i]  # Extract the row and column for
        # the ith coordinate
        map_game[row][column] = symbols_list[i]  # Update the map at the ith
        # coordinate with the ith symbol

    return map_game  # Return the updated game map


def cpu_deploy_single_ship(map_game: List[List[str]], ship_size: int) -> (
        Union)[Tuple[str, List[Tuple[int, int]]], bool]:
    """
    Deploy a single ship of a given size on the game map.

    Parameters:
        map_game (List[List[str]]): The 2D game map.
        ship_size (int): The size of the ship to deploy.

    Returns:
        Union[Tuple[str, List[Tuple[int, int]]], bool]: A tuple containing
        the alignment and a list of coordinates where the ship is deployed,
        or False if deployment failed.

    This function performs the following key tasks:
        1. Call the helper function `cpu_deploy_single_ship_get_coordinates`
        to get potential coordinates and alignment for the ship.
        2. If no coordinates are found, return False.
        3. Randomly select one set of coordinates from the available options.
        4. Generate the full list of coordinates based on the selected
        starting coordinate and alignment.
        5. Return the alignment and full list of coordinates for the deployed
        ship.

    Note:
        - The function will return False if it's not possible to deploy the
        ship.
        - The alignment will be either "Horizontal" or "Vertical".
    """

    # Get potential coordinates and alignment for the ship
    return_result = cpu_deploy_get_coordinates(map_game, ship_size)

    # Check if coordinates are found
    if not return_result:
        return False  # No coordinates found, return False

    # Coordinates found, proceed with deployment
    else:
        # Extract alignment and list of potential starting coordinates
        alignment, coordinate_list = return_result

        # Randomly select a starting coordinate for the ship
        location = random.choice(coordinate_list)

        # Generate the full list of coordinates for the ship
        ship_coordinate_list = create_coordinate_list(location[0], location[
            1], alignment, ship_size)

        # Return the alignment and full list of coordinates for the deployed
        # ship
        return alignment, ship_coordinate_list


def search_coordinates(map_game: List[List[str]], ship_size: int,
                       alignment: str) -> Union[List[Tuple[int, int]], None]:
    """
    Search for suitable coordinates based on a given alignment.

    Args:
        map_game (List[List[str]]): The 2D game map.
        ship_size (int): The size of the ship.
        alignment (str): The alignment ("Horizontal" or "Vertical").

    Returns:
        List[Tuple[int, int]] or None: A list of coordinates if found,
        otherwise None.
    """
    if alignment == "Vertical":
        return search_pattern(map_game, ship_size, 1)
    elif alignment == "Horizontal":
        return search_pattern(map_game, 1, ship_size)
    return None


def cpu_deploy_get_coordinates(
        map_game: List[List[str]],
        ship_size: int
) -> Union[Tuple[str, List[Tuple[int, int]]], bool]:
    """
    Determine suitable coordinates for deploying a single ship on the game map.

    Parameters:
        map_game (List[List[str]]): The 2D game map.
        ship_size (int): The size of the ship to deploy.

    Returns:
        Union[Tuple[str, List[Tuple[int, int]]], bool]: A tuple containing
        the alignment ("Horizontal", "Vertical", or "Single") and a list of
        suitable coordinates for deploying the ship. Returns False if no
        suitable coordinates are found.
    """
    # Case for ship of size 1
    if ship_size == 1:
        result = search_pattern(map_game, 1, 1)
        if not result:
            return False
        return "Single", result

    # For ships greater than size 1
    alignments = ["Vertical", "Horizontal"]

    # Randomly pick an alignment and remove it from the list
    alignment = random.choice(alignments)
    alignments.remove(alignment)

    result = search_pattern(map_game,
                            1 if alignment == "Horizontal" else ship_size,
                            1 if alignment == "Vertical" else ship_size)
    if result:
        return alignment, result

    # Try the other alignment
    alignment = alignments[0]  # Only one item should be left
    result = search_pattern(map_game,
                            1 if alignment == "Horizontal" else ship_size,
                            1 if alignment == "Vertical" else ship_size)
    if result:
        return alignment, result

    return False  # No suitable coordinates found


def search_pattern(map_game, height, width):
    """
    Search for occurrences of a pattern of 'default symbol' on the map and
    return their coordinates.

    This function iterates through the game map to find all occurrences of a
    pattern
    of 'default symbol' of the specified height and width. The coordinates of
    the top-left
    corner of each found pattern are returned.

    Args:
        map_game (List[List[str]]): The 2D game map.
        height (int): The height of the pattern to search for.
        width (int): The width of the pattern to search for.

    Global Variables:
        DEFAULT_MAP_SETTINGS (List): Default settings for Map

    Returns:
        List[Tuple[int, int]]: A list of coordinates (row, col) where the
        pattern is found.
                               Returns an empty list if no pattern is found.
    """

    # Reference the global variable for the default symbol
    global DEFAULT_MAP_SETTINGS

    # Retrieve the dimensions of the game map
    map_height, map_width = len(map_game), len(map_game[0])

    # Initialize an empty list to collect coordinates where the pattern is
    # found
    coordinates = []

    # Create the pattern using list comprehension
    pattern = [DEFAULT_MAP_SETTINGS[2] * width for _ in range(height)]

    # Traverse the map to find matching patterns
    for row in range(map_height - height + 1):
        for col in range(map_width - width + 1):
            # Check if the section of the map matches the pattern
            if all(
                    map_game[row + i][col + j] == pattern[i][j]
                    for i in range(height)
                    for j in range(width)
            ):
                # If the pattern matches, add the coordinates to the list
                coordinates.append([row, col])
    return coordinates  # Return the list of coordinates where the pattern is


# found


# Various helping functions
# ------------------------------

def create_coordinate_list(row: int, column: int, alignment: str,
                           ship_size: int) -> List:
    """
    Create a list of coordinates where the ship will be placed on the map.

    This function generates a list of coordinates based on the starting row
    and column,
    the alignment of the ship, and the size of the ship.

    Args:
        row (int): The starting row index for the ship.
        column (int): The starting column index for the ship.
        alignment (str): The alignment of the ship ("Horizontal" or
        "Vertical").
        ship_size (int): The size of the ship.

    Returns:
        list: A list of coordinates where the ship will be placed.
    """

    # Initialize an empty list to store the coordinates
    coordinates_list = []

    # If the ship size is 1, it only occupies one cell
    if ship_size == 1:
        coordinates_list.append([row, column])

    # For larger ships, we need to calculate the additional coordinates based
    # on alignment
    else:
        # If the ship is aligned horizontally
        if alignment == "Horizontal":
            for cell in range(ship_size):
                coordinates_list.append([row, column + cell])

        # If the ship is aligned vertically
        if alignment == "Vertical":
            for cell in range(ship_size):
                coordinates_list.append([row + cell, column])
    return coordinates_list


def map_allocate_empty_space_for_ship(map_game: List[List[str]],
                                      coordinates_list: List, symbol: str):
    """
    Allocate empty space around a ship on a 2D map.

    This function modifies the given map_game to ensure that ships can't be
    deployed touching each other. It marks the empty space around a ship with
    'Miss' symbols. After all ships are deployed, these symbols will be
    changed back to 'default symbol'.

    Args:
        map_game (list): The 2D map where the ship will be deployed.
        coordinates_list (list): List of coordinates where the ship is
        located.
        symbol (str): The Symbol will be displayed on the game map

    Global Variables:
        SHIP_SYMBOLS (dict): Dictionary containing ship symbols.

    Returns:
        list: Modified game map with empty spaces around the ship.
    """

    # Access the global variable SHIP_SYMBOLS for ship symbols

    # Define the relative positions for empty space around a single cell
    blank_space = [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 0], [0, 1],
                   [1, -1], [1, 0], [1, 1]]

    # Initialize an empty list to store the coordinates for empty spaces
    blank_space_coordinates_list = []

    # Calculate the actual positions for empty space around each cell of the
    # ship
    for space in blank_space:
        blank_row, blank_column = space
        for coordinate in coordinates_list:
            new_row, new_column = coordinate
            new_blank_row, new_blank_column = (blank_row + new_row,
                                               blank_column + new_column)
            blank_space_coordinates_list.append([new_blank_row,
                                                 new_blank_column])

    # Update the map to allocate empty space around the ship
    for new_space in blank_space_coordinates_list:
        b_row, b_column = new_space
        if 0 <= b_row < len(map_game) and 0 <= b_column < len(map_game[0]):
            map_game[b_row][b_column] = symbol

    return map_game


# The code below for testing purposes
# -------------------------------


map_cpu_hidden = create_map(13, 13,
                            DEFAULT_MAP_SETTINGS[2])
map_cpu_display = create_map(13, 13,
                             DEFAULT_MAP_SETTINGS[2])
fleet_cpu = create_default_fleet()
print(fleet_cpu)

cpu_deploy_all_ships(map_cpu_display, fleet_cpu)

print(fleet_cpu)

print_two_maps(map_cpu_hidden, map_cpu_display, "Hidden", "Display",
               DEFAULT_COORDINATES_STYLE[1][0], DEFAULT_COORDINATES_STYLE[
                   1][1], 10)

game_coordinates_style = DEFAULT_COORDINATES_STYLE
fleet_cpu.print_fleet([],game_coordinates_style)
