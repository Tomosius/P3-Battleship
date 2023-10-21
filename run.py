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

def normalize_command(command: str) -> str:
    """
    Normalize the command string for easier comparison.

    This function tokenizes the command string, sorts the tokens,
    and converts them to lowercase for case-insensitive comparison.

    Parameters:
        command (str): The command string to be normalized.

    Returns:
        str: The normalized command string.
    """
    return ' '.join(sorted(command.lower().split()))


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
    user_input = normalize_command(user_input)

    # Initialize variables to store the best match and its Levenshtein
    # distance ratio
    max_ratio = -1
    best_match = None

    # Loop through each possible command to find the best match
    for command in possible_commands:
        # Normalize the possible command for comparison
        normalized_command = normalize_command(command)

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

    def __init__(self, name: str, size: int) -> None:
        """
        Initialize a Ship object with its name and size.

        Parameters:
            name (str): The name of the ship (for example,
        "Destroyer").
            size (int): The size of the ship, representing how
        many cells it occupies.

        Attributes:
            name (str): The name of the ship.
            size (int): The size of the ship in cells.
            cell_coordinates (List[Tuple[int, int]]): Coordinates (x, y) for
            each cell of the ship.
            hits (List[bool]): Tracks the hit status for each cell of the ship.
            sunk (bool): Indicates whether the ship is sunk or not.
            color (str): ANSI color code for the ship, based on its status.
            orientation (str): Orientation of the ship ("Horizontal" or
            "Vertical").
        """
        self.name = name
        self.size = size
        self.cell_coordinates = []
        self.sunk = False
        self.color = None
        self.orientation = None

        # Setting initial color and orientation based on ship size
        if self.size == 1:
            self.orientation = "Single"

    def set_cell_coordinates(self, coordinates: List[Tuple[int, int]]) -> None:
        """
        Set the coordinates for each cell of the ship.

        Parameters: coordinates (List[Tuple[int, int]]): A list of (x,
        y) tuples representing the coordinates for each cell.
        """
        self.cell_coordinates = coordinates

    def get_all_coordinates(self) -> List[Tuple[int, int]]:
        """
        Retrieve the coordinates of all cells in the ship.

        Returns:
            List[Tuple[int, int]]: A list of (x, y) tuples representing the
            coordinates for each cell.
        """
        return self.cell_coordinates

    def set_alignment(self, orientation: str) -> None:
        """
        Set the alignment of the ship and update its color based on the
        orientation.

        Parameters:
            orientation (str): The orientation of the ship, either
            "Horizontal" or "Vertical".
        """
        self.orientation = orientation
        if orientation == "Horizontal":
            self.color = DEFAULT_COLORS["DarkBlue"]
        elif orientation == "Vertical":
            self.color = DEFAULT_COLORS["DarkGreen"]
        else:
            self.color = DEFAULT_COLORS["DarkYellow"]

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

    def get_symbol(self, position: int) -> str:
        """
        Get the symbol for a ship cell based on its hit status and orientation.

        Parameters:
            position (int): The position of the cell within the
            ship, used to determine the appropriate symbol for that cell.

        Returns:
            str: The symbol for the cell, colored based on the ship's
            current status.

        This function performs the following key tasks:
        1. Check if the ship
        is sunk.
        2. Determines the appropriate symbol for the ship based on
        its size and orientation.
        3. Colors the symbol based on the ship's
        status (for example, red if sunk).

        Note: The color of the symbol will be red if the ship is sunk or if
        the cell at the given `position` is hit.
        """
        # Determine the color based on sunk status
        if self.sunk:
            color = DEFAULT_COLORS["DarkRed"]
        else:
            color = self.color

        # Determine the symbol key based on the size and orientation of the
        # ship
        symbol_key = self.orientation

        # Choose the appropriate symbol for the cell based on its position
        # in the ship
        symbol = SHIP_SYMBOLS[symbol_key][0 if position == 0 else 1]

        # Return the colored symbol
        return color + symbol + DEFAULT_COLORS["Reset"]


class Fleet:
    """Manages a collection of Ship objects, encapsulating them in a fleet
    for the Battleship game."""

    def __init__(self) -> None:
        """
        Initialize an empty Fleet object, designed to manage multiple ships
        in a game.

        Attributes:
            ships (List[Ship]): A list to store the Ship objects
            that belong to this fleet.

        Starts empty.
        """
        self.ships: List[Ship] = []

    def add_ship(self, ship: Ship) -> None:
        """
        Add a Ship object to the fleet, expanding the fleet's capabilities
        and size.

        Parameters:
            ship (Ship): The Ship object to be added to the fleet,
            containing details like name, size, etc.

        Note:
            This function modifies the internal 'ships' list by appending
            the new Ship object to it.
        """
        self.ships.append(ship)

    def get_ship(self, name: str) -> Union[Ship, None]:
        """
        Retrieve a Ship object from the fleet by its name, allowing for
        individual ship manipulation.

        Parameters:
            name (str): The name of the ship to retrieve, as specified
            during the Ship object creation.

        Returns:
            Ship or None: Returns the Ship object if found within the fleet;
            returns None if not found.
        """
        for ship in self.ships:
            if ship.name == name:
                return ship
        return None


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



def calculate_max_map_dimensions(map_height: int, map_width: int, gap: int) -> (int, int):
    """
    Calculate the maximum map dimensions that can fit in the terminal.

    Args:
        map_height (int): Current map height.
        map_width (int): Current map width.
        gap (int): Gap between the two maps.

    Returns:
        tuple: (max_map_width, max_map_height)
    """

    # Get terminal size
    terminal_size = shutil.get_terminal_size()
    terminal_width = terminal_size.columns
    terminal_height = terminal_size.lines

    # Width of each map cell (including spaces)
    cell_width = len("X") + 2  # "X" plus two spaces

    # Number of characters needed for row labels
    row_label_width = len(str(map_height - 1))

    # Calculate max map width
    max_map_width = math.floor(
        (terminal_width - gap - 2 * (row_label_width + 3)) / (2 * cell_width)
    )

    # Calculate max map height
    max_map_height = terminal_height - 3  # 1 row for column labels, 1 for separator, 1 for map label

    return max_map_width, max_map_height





def find_max_label_length(map_size: int, index_label: List[Union[int, str]]) -> int:
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

    # Loop through the index_label list up to map_size to find the maximum label length
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
        print(str(column_index_label[col_index]).rjust(num_digits_map_width + char_width), end=" ")
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




player_map = create_map(16, 13, DEFAULT_SYMBOL)
print_two_maps(player_map, player_map, "jonas", "petras",
               DEFAULT_MAP_ROW_INDEXES, DEFAULT_MAP_COLUMN_INDEXES, 10)

