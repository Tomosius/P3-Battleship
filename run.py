# battleship.py test.py - this code is for testing CPU vs CPU game


# Import required libraries
import random  # For generating random numbers
import copy  # For creating deep copies of data structures
import os  # For clearing the terminal screen
import time  # For time-related functionalities
import re  # For handling user input expressions
from difflib import SequenceMatcher
from typing import List, Optional, Union, Dict, Tuple
from icecream import ic

# Constants for map dimensions and default symbol
DEFAULT_MAP_HEIGHT = 10
DEFAULT_MAP_WIDTH = 10
DEFAULT_SYMBOL = '?'  # Symbol representing an empty cell in the map
DEFAULT_GAPS_BETWEEN_MAPS = True
DEFAULT_MAP_ROW_INDEXES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
DEFAULT_MAP_COLUMN_INDEXES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

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
    'change coordinate labels': ['modify grid labels', 'edit coordinate '
                                                       'names',
                                 'labels change']
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

    Parameters: user_input (str): The user's input string possible_commands
    (List[str]): A list of possible commands to match against.

    Returns: Optional[str]: The best-matching command, or None if no
    reasonable match is found.
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

        Parameters: name (str): The name of the ship (e.g., "Destroyer").
        Size (int): The size of the ship, representing how many cells it
        occupies.

        Attributes: name (str): The name of the ship.
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
        List[Tuple[int, int]]:
        A list of (x, y) tuples representing the coordinates for each cell.
        """
        return self.cell_coordinates

    def set_alignment(self, orientation: str) -> None:
        """
        Set the alignment of the ship and update its color based on the
        orientation.

        Parameters: orientation (str): The orientation of the ship, either
        "Horizontal" or "Vertical".
        """
        self.orientation = orientation
        if orientation == "Horizontal":
            self.color = DEFAULT_COLORS["DarkBlue"]
        elif orientation == "Vertal":
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
            position (int): The position of the cell within the ship, used to determine
            the appropriate symbol for that cell.

        Returns:
            str: The symbol for the cell, colored based on the ship's current status.

        This function performs the following key tasks:
        1. Checks if the ship is sunk.
        2. Determines the appropriate symbol for the ship based on its size and orientation.
        3. Colors the symbol based on the ship's status (e.g., red if sunk).

        Note: The color of the symbol will be red if the ship is sunk or if the cell at
        the given `position` is hit.
            """
        # Determine the color based on sunk status
        if self.sunk:
            color = DEFAULT_COLORS["DarkRed"]
        else:
            color = self.color

        # Determine the symbol key based on the size and orientation of the ship
        symbol_key = self.orientation

        # Choose the appropriate symbol for the cell based on its position in the ship
        symbol = SHIP_SYMBOLS[symbol_key][0 if position == 0 else 1]

        # Return the colored symbol
        return color + symbol + DEFAULT_COLORS["Reset"]





