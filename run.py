# battleship.py test.py – this code is for testing CPU vs CPU game

# Import required libraries
import random  # For generating random numbers
import copy  # For creating deep copies of data structures
import os  # For clearing the terminal screen
import time  # For time-related functionalities
import re  # For handling user input expressions
from difflib import SequenceMatcher
from typing import List, Optional, Union, Dict, Tuple
import icecream
import math
import shutil

# Constants for map dimensions and default symbol
DEFAULT_MAP_HEIGHT = 10
DEFAULT_MAP_WIDTH = 10
DEFAULT_SYMBOL = '?'  # Symbol representing an empty cell in the map
DEFAULT_GAPS_BETWEEN_MAPS = True

DEFAULT_MAP_ROW_INDEXES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                           15, 16, 17, 18, 19]
DEFAULT_MAP_COLUMN_INDEXES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                              15, 16, 17, 18, 19]

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
SHIP_SYMBOLS: Dict[str, List[str]] = {
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

def normalize_string(text_input: str) -> str:
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
    user_input = normalize_string(user_input)

    # Initialize variables to store the best match and its Levenshtein
    # distance ratio
    max_ratio = -1
    best_match = None

    # Loop through each possible command to find the best match
    for command in possible_commands:
        # Normalize the possible command for comparison
        normalized_command = normalize_string(command)

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


class Fleet:
    """Manages a collection of Ship objects, encapsulating them in a fleet
    for the Battleship game."""

    def __init__(self) -> None:
        """Initialize an empty Fleet object.
        Attributes:
            ships (List[Ship]): A list to store the Ship objects that belong to this fleet.
        """
        self.ships: List[Ship] = []

    def add_ship(self, ship: Ship) -> None:
        """Add a Ship object to the fleet.
        Parameters:
            ship (Ship): The Ship object to be added to the fleet.
        """
        self.ships.append(ship)

    def remove_ship(self, name: str) -> bool:
        """Remove one instance of a ship by its name from the fleet.
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

    def get_ship(self, name: str) -> Union[Ship, None]:
        """Retrieve a Ship object from the fleet by its name.
        Parameters:
            name (str): The name of the ship to retrieve.
        Returns:
            Ship or None: Returns the Ship object if found; returns None if not found.
        """
        for ship in self.ships:
            if ship.name == name:
                return ship
        return None

    def get_ship_quantity(self, name: str) -> int:
        """Get the quantity of a specific type of ship in the fleet.
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

    def get_ship_quantity_by_sunk_status(self, name: str, is_sunk: bool = False) -> int:
        """Get the quantity of a specific type of ship in the fleet based on its sunk status.

        Parameters:
            name (str): The name of the type of ship to count.
            is_sunk (bool, optional): Whether to count ships that are sunk.
                                      Default is False, which counts not-sunk ships.

        Returns:
            int: The number of ships of this type in the fleet based on sunk status.
        """
        count = 0
        for ship in self.ships:
            if ship.name == name and ship.sunk == is_sunk:
                count += 1
        return count

    def get_ship_quantity_by_deployed_status(self, name: str, is_deployed: bool = False) -> int:
        """Get the quantity of a specific type of ship in the fleet based on its deployed status.

        Parameters:
            name (str): The name of the type of ship to count.
            is_deployed (bool, optional): Whether to count ships that are deployed.
                                          Default is False, which counts not-deployed ships.

        Returns:
            int: The number of ships of this type in the fleet based on deployed status.
        """
        count = 0
        for ship in self.ships:
            if ship.name == name and ship.deployed == is_deployed:
                count += 1
        return count


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
        # The enumerate function provides an index starting from 1 for each ship.
        for i, ship in enumerate(self.ships, 1):

            # Append the index, name, and size of each ship to the output string.
            output += f"{i}. {ship.name} (Size: {ship.size})\n"

            # Append the coordinates of each ship to the output string.
            output += f"   Coordinates: {ship.cell_coordinates}\n"

            # Check the sunk status of the ship and append it to the output string.
            output += f"   Sunk: {'Yes' if ship.sunk else 'No'}\n"

            # Check the deployment status of the ship and append it to the output string.
            output += f"   Deployed: {'Yes' if ship.deployed else 'No'}\n"

        # Return the fully constructed output string.
        return output




def create_default_fleet() -> Fleet:
    """
    Create a default fleet with predefined ships.

    Returns:
        Fleet: A Fleet object populated with default Ship objects.

    This function performs the following key tasks:
    1. Initializes an empty Fleet object.
    2. Defines a list of default ships, specifying their names, sizes, and quantities.
    3. Iterates through the list of default ships, creating Ship objects and adding them to the fleet.
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
    ]

    # Iterate through the list of default ships
    for ship_info in default_ships:
        # Create and add each Ship object to the fleet based on its quantity
        for _ in range(ship_info["qty"]):
            ship = Ship(ship_info["name"], ship_info["size"])
            fleet.add_ship(ship)

    return fleet


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


def print_map(map_game, row_labels, column_labels):
    """
    Print the game map in a human-readable format.

    Args:
        map_game (list): A 2D list representing the game map, where each
            cell contains the status of a ship or water.
        row_labels (list): A list of labels for the rows.
        column_labels (list): A list of labels for the
            columns.

    Output:
        The function will print the game map to the console.
    """

    # Validate input arguments
    try:
        assert len(row_labels) == len(map_game[0]), \
            "Row labels must match the number of columns in the map."
        assert len(column_labels) == len(map_game), \
            "Column labels must match the number of rows in the map."
    except AssertionError as e:
        print(f"Error: {e}")
        return

    # Print column headers (e.g., A, B, C, ..., Z)
    print("   ", end="")
    for col_label in row_labels:
        print(f"{col_label}  ", end="")

    # Print a separator line between headers and table
    print("\n   " + "=" * (len(row_labels) * 3))

    # Loop through each row
    for row_index, row in enumerate(map_game):
        # Print row header (e.g., 1, 2, 3, ..., N)
        print(f"{column_labels[row_index]} |", end=" ")

        # Loop through each cell in the row
        for cell_value in row:
            print(f"{cell_value}  ", end="")

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
def calculate_max_map_dimensions(map_height: int, map_width: int, gap: int,
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

# Various game helping functions
# ------------------------------

def create_coordinate_list(row, column, alignment, ship_size):
    """
    Create a list of coordinates where the ship will be placed on the map.

    This function generates a list of coordinates based on the starting row
    and column,
    the alignment of the ship, and the size of the ship.

    Args:
        row (int): The starting row index for the ship.
        column (int): The starting column index for the ship.
        alignment (str): The orientation of the ship ("Horizontal" or
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


def map_allocate_empty_space_for_ship(map_game, coordinates_list, symbol):
    """
    Allocate empty space around a ship on a 2D map.

    This function modifies the given map_game to ensure that ships cannot be
    deployed touching each other. It marks the empty space around a ship with
    'Miss' symbols. After all ships are deployed, these symbols will be
    changed back to DEFAULT_SYMBOL.

    Args:
        map_game (list): The 2D map where the ship will be deployed.
        coordinates_list (list): List of coordinates where the ship is
        located.

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


