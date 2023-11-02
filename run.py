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
from collections import Counter
import string
from io import StringIO
import sys

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

DEFAULT_SHIPS = [
    {"name": "AircraftCarrier", "size": 5, "qty": 1},
    {"name": "Battleship", "size": 4, "qty": 1},
    {"name": "Cruiser", "size": 3, "qty": 1},
    {"name": "Submarine", "size": 3, "qty": 1},
    {"name": "Destroyer", "size": 2, "qty": 2},
    {"name": "Tug Boat", "size": 1, "qty": 4},

]

# Game instructions and settings, presented as lists
LIST_INSTRUCTIONS = [
    "1. Ships can be \u001b[34mHORIZONTAL\u001b[0m or \u001b["
    "32mVERTICAL\u001b[0m",
    "2. Ships can \u001b[31mNOT\u001b[0m be touching each other",
    "3.Default game map is size 10 by 10",
    "4.Coordinate Entering style:",
    "COLUMN , COMMA, ROW",
    "5. \u001b[31mDAMAGED\u001b[0m ships will be green color",
    "",
    "To adjust game settings type \u001b[33mY\u001b["
    "0m",
    "",
    "To start game just press \u001b["
    "33mENTER\u001b[0m"]
# Game settings adjustment text
LIST_GAME_SETTINGS_CHANGES= [
    "To change game \u001b[33mFLEET\u001b[0m type \u001b[31mF\u001b[0m ",
    "If you want to change \u001b[33mMAP\u001b[0m type \u001b[31mM\u001b[0m ",
    "To change \u001b[33mCOORDINATES\u001b[0m  style type \u001b["
    "31mS\u001b[0m ",
    "",
    "You can select changes by typing, E.g.:",
    "",
    "    \u001b[33mmodify fleet\u001b[0m",
    "",
    "To return back type \u001b[31m0\u001b[0m - zero"
]

# Commands dictionary
# -------------------

# Creating a dictionary of commands and their possible similar expressions
# that a user might use
DICTIONARY_COMMANDS = {
    'modify fleet': ['edit fleet', 'update fleet', 'fleet modify'],
    'print fleet': ['show fleet', 'display fleet', 'fleet view'],
    'modify ship': ['edit ship', 'ship edit', 'update ship', 'ship edit',
                    'ship modify', 'change ship', 'ship change'],
    'add ship': ['insert ship', 'place ship', 'ship add'],
    'delete ship': ['remove ship', 'erase ship', 'ship delete'],
    'change map size': ['resize map', 'adjust map', 'map dimensions'],
    'gaps between ships': ['ship spacing', 'distance between ships',
                           'ship gaps'],
    'change coordinate labels': ['modify grid labels',
                                 'edit coordinate names', 'labels change'],
    'change input': ['change input', 'input change', 'swap input',
                     'input swap'],
    'start game': ['begin game', 'launch game', 'game start'],
    'reset settings': ['default settings', 'clear settings',"settings reset"],
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


def validate_user_input(input_str, parts, type=None):
    """
    Validates user input by splitting it into a specified number of parts and
    optionally verifies their type.

    Parameters:
        input_str (str): The user-provided input string.
        parts (int): The expected number of parts to split the input into.
        type (str, optional): The expected data type for each part, currently
        supports only 'integer'.

    Returns:
        tuple: A tuple containing three elements:
            - A boolean indicating if the input is valid.
            - A tuple of the split parts.
            - A list of string messages indicating validation for each part.
    """

    # Use a regular expression to split the input into parts by any
    # non-alphanumeric character,
    # while also removing any empty strings.
    split_input = re.split(r'[^A-Za-z0-9]+', input_str)
    # Initialize a flag to keep track of whether the entire input is valid
    input_valid = True

    # Initialize a list to hold text that describes the validation status for
    # each part
    output_text = []

    # Check if the number of parts obtained from the split operation matches
    # the expected number of parts
    if len(split_input) != parts:
        output_text.append(f'Input should be split into {parts} parts.')
        return False, tuple(split_input), output_text

    # If a specific data type is expected for each part, perform type
    # validation
    if type == 'integer':
        for i, part in enumerate(split_input):
            # Check if the part is an integer
            if not part.isdigit():
                output_text.append(f'Your input "{part}" is NOT an Integer.')
                input_valid = False  # Mark the input as invalid if even one
            # part fails the type check
            else:
                # Convert the part to an integer for future use
                split_input[i] = int(part)

    # Return the final validity flag, the tuple of validated parts, and the
    # list of validation messages
    return input_valid, tuple(split_input), output_text


def input_normalize_string(text_input):
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


def levenshtein_ratio(first_string, second_string):
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


def find_unique_words(possible_commands):
    """
    Find words that appear only once across all possible commands.

    Parameters:
        possible_commands (List[str]): A list of possible commands to search.

    Returns:
        set: A set of unique words.
    """
    all_words = [word for command in possible_commands for word in command.split()]
    word_count = Counter(all_words)
    return {word for word, count in word_count.items() if count == 1}

def find_best_match(user_input, possible_commands):
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
        None if no reasonable match is found.
    """
    # Normalize the user input for comparison
    normalized_user_input = input_normalize_string(user_input)

    # Find unique words from the list of possible commands
    unique_words = find_unique_words(possible_commands)

    # Initialize variables to store the best unique word match and its Levenshtein distance ratio
    best_unique_word = None
    max_unique_word_ratio = -1

    # Check if the user input contains or nearly matches any unique word
    for word in normalized_user_input.split():
        if word in unique_words:
            return next(command for command in possible_commands if word in command.split())

        # Check for near-matches with unique words
        for unique_word in unique_words:
            ratio = levenshtein_ratio(word, unique_word)
            if ratio > max_unique_word_ratio:
                max_unique_word_ratio = ratio
                best_unique_word = unique_word

    # Check for unique words that are substrings of words in the user input
    for unique_word in unique_words:
        for word in normalized_user_input.split():
            if unique_word in word or word in unique_word:
                return next(command for command in possible_commands if unique_word in command.split())

    # If a near-match with a unique word is found, return the corresponding command
    if max_unique_word_ratio > 0.85:
        return next(command for command in possible_commands if best_unique_word in command.split())

    # Initialize variables to store the best match and its Levenshtein distance ratio
    max_ratio = -1
    best_match = None

    # Loop through each possible command to find the best match
    for command in possible_commands:
        # Normalize the possible command for comparison
        normalized_command = input_normalize_string(command)

        # Calculate the Levenshtein distance ratio between the normalized user input and the possible command
        ratio = levenshtein_ratio(normalized_user_input, normalized_command)

        # Update the best match and its ratio if the current ratio is higher
        if ratio > max_ratio:
            max_ratio = ratio
            best_match = command

    # A threshold is set for the Levenshtein distance ratio to consider a match as reasonable
    if max_ratio > 0.6:
        return best_match
    else:
        return None


# Managing Game Map and other Settings:
# -------------------------------------

class game_settings:
    """Class to hold default map settings for the Battleship game.

    Attributes:
        height (int): The height of the map (number of rows).
        width (int): The width of the map (number of columns).
        symbol (str): The default symbol to display on the map.
        gaps (bool): Whether to include gaps between ships.
        input_style (list): Input-output style ['Row', 'Column'] or ['Column', 'Row'].
        row_label_symbol (str or int): Symbol used for row labels.
        column_label_symbol (str or int): Symbol used for column labels.
        row_labels (list): List of row index labels.
        col_labels (list): List of column index labels.
    """

    def __init__(self,
                 height=10,
                 width=10,
                 symbol="?",
                 gaps=True,
                 input_style=["Row", "Column"],
                 row_label_symbol="1",
                 column_label_symbol="1",
                 maps_gap = 5):
        """
        Initialize the default map settings with default or provided values.

        Args:
            height (int): The height of the map (number of rows).
            width (int): The width of the map (number of columns).
            symbol (str): The default symbol to display on the map.
            gaps (bool): Whether to include gaps between ships.
            input_style (list): Input-output style.
            row_label_symbol (str or int): Symbol used for row labels.
            column_label_symbol (str or int): Symbol used for column labels.
        """
        self._height = height
        self._width = width
        self.symbol = symbol
        self.gaps = gaps
        self.maps_gap = maps_gap
        self.input_style = input_style.copy()  # Create a copy to avoid reference issues
        self.row_label_symbol = row_label_symbol
        self.column_label_symbol = column_label_symbol
        self.row_labels = []
        self.col_labels = []
        self.update_labels()

    def update_labels(self):
        """Update row_labels and col_labels based on current settings."""
        self.row_labels = self.generate_labels(self.row_label_symbol, self._height)
        self.col_labels = self.generate_labels(self.column_label_symbol, self._width)

    def generate_labels(self, symbol, length):
        """
        Generate and return labels based on the provided symbol and length.

        Args:
            symbol (str or int): The symbol to determine the type of labels.
            length (int): The length to determine the number of labels.

        Returns:
            list: Generated labels.
        """
        if str(symbol).isdigit():
            return list(range(0, length + 1))
        else:
            return list(string.ascii_uppercase)[:length]

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        self.update_labels()

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self.update_labels()

    def __str__(self):
        """
        Return a string representation of the current settings.

        Returns:
            str: A formatted string displaying the current settings.
        """
        return (f"Height: {self.height}, Width: {self.width}, Symbol: {self.symbol}, "
                f"Gaps: {self.gaps}, IO Style: {self.input_style}, "
                f"Row Labels: {self.row_labels}, Column Labels: {self.col_labels}, "
                f"Row Label Symbol: {self.row_label_symbol}, Column Label Symbol: {self.column_label_symbol}")

    def clone(self):
        """
        Create a copy of the current object with the same settings.

        Returns:
            game_settings: A new game_settings object with the same settings.
        """
        return game_settings(
            height=self.height,
            width=self.width,
            symbol=self.symbol,
            gaps=self.gaps,
            input_style=self.input_style.copy(),
            row_label_symbol=self.row_label_symbol,
            column_label_symbol=self.column_label_symbol
        )






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

    def get_coordinates_by_single_coordinate(self, single_coordinate):
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

    def set_alignment(self, alignment):
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

    def set_sunk(self):
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

    def get_symbols(self):
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

    def __init__(self):
        """
        Initialize an empty Fleet object.
        Variables:
            ships (List[Ship]):
             A list to store the Ship objects that belong to this fleet.
        """
        self.ships: List[Ship] = []

    def add_ship(self, ship):
        """
        Add a Ship object to the fleet.
        Parameters:
            ship (Ship): The Ships object to be added to the fleet.
        """
        self.ships.append(ship)

    def remove_ship(self, name):
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

    def get_ship(self, name, is_deployed):
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

    def get_ship_quantity(self, name):
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

    def get_ship_quantity_by_sunk_status(self, name, is_sunk):
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

    def get_ship_quantity_by_deployed_status(self, name, is_deployed):
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

    def get_biggest_ship_by_deployed_status(self, is_deployed):
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

    def __str__(self):
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
            List[dict]: A list of dictionaries containing basic information
            about each ship.
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
            info['deployed_qty'] = sum(ship.deployed for ship in self.ships if
                                       ship.name == info['name'])

    def add_sunk_qty(self, ship_info_list):
        """
        Add the quantity of sunk ships to the ship information list.

        Parameters:
            ship_info_list (List[dict]): The list containing ship information.
        """
        for info in ship_info_list:
            info['sunk_qty'] = sum(
                ship.sunk for ship in self.ships if ship.name == info['name'])

    def format_coordinates(self, coordinates, game_map_settings):
        """
        Format the coordinates according to the game's coordinate style.

        Parameters:
            coordinates (List[tuple]): List of coordinates.
            game_map_settings (List): The game's map style.

        Returns:
            List[str]: List of formatted coordinates.
        """
        formatted_coordinates = []
        for coord_set in coordinates:
            formatted_set = []
            for (row, col) in coord_set:
                row_label = game_map_settings[5][0][row]
                col_label = game_map_settings[5][1][col]
                if game_map_settings[4] == ["Row", "Column"]:
                    formatted_set.append(f"({row_label},{col_label})")
                else:
                    formatted_set.append(f"({col_label},{row_label})")
            formatted_coordinates.append(' '.join(formatted_set))
        return formatted_coordinates

    def add_coordinates_condition(self, ship_info_list, condition,
                                  game_map_settings):
        """
        Add coordinates condition to the ship information list.

        Parameters:
            ship_info_list (List[dict]): The list containing ship information.
            condition (str): The condition to filter the coordinates.
            game_map_settings (List): The game's coordinate style.
        """
        for info in ship_info_list:
            coordinates = [ship.cell_coordinates for ship in self.ships if
                           ship.name == info['name'] and
                           getattr(ship, condition.split('_')[0])]
            info[condition] = self.format_coordinates(coordinates,
                                                      game_map_settings)

    def print_fleet(self, conditions="", game_map_settings=None):
        """
        Print the fleet information based on given conditions.

        Parameters:
            conditions (List[str], optional): List of conditions to filter
            the information.
            game_map_settings (List, optional): The game's coordinate style.
        """
        ship_info_list = self.gather_basic_info()

        # Map conditions to corresponding functions
        condition_func_map: dict[str, Callable] = {
            'deployed_qty': self.add_deployed_qty,
            'sunk_qty': self.add_sunk_qty,
            'deployed_coordinates': lambda ship_info:
            self.add_coordinates_condition(ship_info, 'deployed_coordinates',
                                           game_map_settings),
            'sunk_coordinates': lambda ship_info:
            self.add_coordinates_condition(ship_info, 'sunk_coordinates',
                                           game_map_settings)
        }

        # Apply each condition function to ship_info_list
        for condition in conditions:
            func = condition_func_map.get(condition)
            if func:
                func(ship_info_list)

        # Print the table header
        print("{:<20}{:<10}{:<10}".format("Name", "Size", "Qty"), end="")
        for condition in conditions:
            if condition == 'deployed_qty':
                header = 'Deployed QTY'
            elif condition == 'sunk_qty':
                header = 'Sunk QTY'
            else:
                header = condition.split('_')[1][:3].upper()

            print(f"{header:<10}", end="")
        print()

        # Print the ship information
        for info in ship_info_list:
            print(f"{info['name']:<20}{info['size']:<10}{info['qty']:<10}",
                  end="")
            for condition in conditions:
                if 'coordinates' not in condition:
                    print(f"{info.get(condition, 0):<10}", end="")
            print()

            self.fleet_print_coordinates(conditions, info)

    def fleet_print_coordinates(self, conditions, info):
        """
        Print the coordinates for each ship based on the given conditions.

        Parameters:
            conditions (List[str]): List of conditions to filter the
            information. Expected to contain 'deployed_coordinates' and/or
            'sunk_coordinates'.
            info (Dict[str, any]): Dictionary containing ship information
            including 'deployed_coordinates' and 'sunk_coordinates' if they
            exist.

        This function is intended to be called within `print_fleet` after
        printing the basic ship information. It prints the coordinates for
        each ship that match the specified conditions in the `conditions`
        list. The coordinates are printed as additional lines below each
        ship's basic information.
        """
        for condition in conditions:
            if 'coordinates' in condition:
                for coord_str in info.get(condition, []):
                    print(f"    {coord_str}")




def create_fleet(fleet=None) -> Fleet:
    """
   Create a fleet with a given configuration or with predefined ships if no configuration is provided.

   Parameters:
       fleet (Fleet, optional): An existing fleet from which to derive the configuration.
                                If None, the default configuration is used.

   Returns:
       Fleet: A Fleet object populated with Ship objects as per the provided configuration or default if None.
   """
    fleet_config = []
    if fleet:
        # Extract the configuration from the existing fleet
        for ship in fleet.ships:
            fleet_config.append({"name": ship.name, "size": ship.size, "qty": 1})
    else:
        # Use the default configuration
        fleet_config = DEFAULT_SHIPS

    new_fleet = Fleet()

    # Create Ship objects based on the provided or default configuration
    for ship_info in fleet_config:
        for _ in range(ship_info["qty"]):
            ship = Ship(ship_info["name"], ship_info["size"])
            new_fleet.add_ship(ship)

    return new_fleet






# Map manipulating functions
# --------------------------
def create_map(height, width, symbol):
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

    return [[symbol for _ in range(width)] for _ in range(height)]


def find_max_label_length(map_size, index_label):
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


def print_two_maps(map_left, map_right, label_left, label_right,
                   row_index_label, column_index_label, gap=10):
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
    print("")

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


def print_map_and_list(map_left, list_text, label_left, label_instructions,
                       row_index_label, column_index_label, gap=10):
    """
    Print a 2D map on the left and a list of instructions on the right with
    dynamically centered labels and a customizable gap.

    Args:
        map_left: A 2D list representing the map.
        list_text: A list of strings representing the instructions.
        label_left: Label for the map.
        label_instructions: Label for the instructions.
        game_map_settings: Game map settings including row and column index
        labels.
        gap: Number of blank spaces between the map and instructions.
        Default is 10.
    """
    char_width = len("X")

    num_digits_map_width = find_max_label_length(len(map_left[0]),
                                                 column_index_label)
    num_digits_map_height = find_max_label_length(len(map_left),
                                                  row_index_label)
    gap_str = ' ' * gap
    row_index_separator = " | "
    print_map_left_offset = " " * (
            num_digits_map_height + len(row_index_separator))
    number_char_table_total = len(map_left[0]) * (
            num_digits_map_width + char_width + 1)
    label_left_centered = label_left.center(number_char_table_total)
    print(f"{print_map_left_offset}{label_left_centered}{gap_str}"
          f"{print_map_left_offset}{label_instructions.center(40)}")
    print(print_map_left_offset, end=" ")
    for col_index in range(len(map_left[0])):
        print(str(column_index_label[col_index]).rjust(
            num_digits_map_width + char_width), end=" ")
    print(gap_str)
    separator_length_left = len(map_left[0]) * (
            num_digits_map_width + char_width + 1)
    print(print_map_left_offset + "=" * separator_length_left, end=gap_str)
    print("")
    for row_index, row_left in enumerate(map_left):
        print(str(row_index_label[row_index]).rjust(num_digits_map_height + 1),
              end=row_index_separator)
        for value in row_left:
            width = len(str(value))
            print(str(value).rjust(
                num_digits_map_width + char_width - (char_width - width)),
                end=" ")
        print(gap_str, end="")
        instruction = list_text[row_index] if row_index < len(
            list_text) else ''
        print(instruction.ljust(40), end="")
        print()
    for row_index in range(len(map_left), len(list_text)):
        print(" " * (num_digits_map_height + len(row_index_separator) +
                     len(map_left[0]) * (
                             num_digits_map_width + char_width + 1) +
                     gap), end="")
        print(list_text[row_index].ljust(40))


def find_max_column_width(table):
    """
    Find the maximum width for each column in the table.

    Args:
        table: A 2D list representing the table.

    Returns:
        List[int]: A list of maximum widths for each column.
    """
    max_widths = [0] * len(table[0])
    for row in table:
        for i, cell in enumerate(row):
            max_widths[i] = max(max_widths[i], len(str(cell)))
    return max_widths

def print_map_and_table(map_left, table, label_left, label_table,
                        row_index_label, column_index_label, gap: int = 10):
    """
    Print a 2D map on the left and a table on the right with dynamically
    centered labels and a customizable gap.

    Args:
        map_left: A 2D list representing the map.
        table: A 2D list representing the table. The first row contains headers.
        label_left: Label for the map.
        label_table: Label for the table.
        game_map_settings: Game map settings including row and column index labels.
        gap: Number of blank spaces between the map and table. Default is 10.
    """
    # Constants for character dimensions and formatting
    char_width = len("X")

    num_digits_map_width = find_max_label_length(len(map_left[0]), column_index_label)
    num_digits_map_height = find_max_label_length(len(map_left), row_index_label)
    max_col_widths = find_max_column_width(table)
    gap_str = ' ' * gap
    row_index_separator = " | "
    print_map_left_offset = " " * (num_digits_map_height + len(row_index_separator))
    number_char_map_total = len(map_left[0]) * (num_digits_map_width + char_width + 1)
    label_left_centered = label_left.center(number_char_map_total)
    label_table_centered = label_table.center(sum(max_col_widths) + len(max_col_widths) - 1)

    # Print the centered labels for both map and table
    print(f"{print_map_left_offset}{label_left_centered}{gap_str}{label_table_centered}")

    # Print column headers for the map
    print(print_map_left_offset, end=" ")
    for col_index in range(len(map_left[0])):
        print(str(column_index_label[col_index]).rjust(num_digits_map_width + char_width), end=" ")
    print(gap_str, end="")

    # Print the table headers
    for i, header in enumerate(table[0]):
        print(str(header).ljust(max_col_widths[i]), end=" " if i < len(table[0]) - 1 else "\n")

    # Print the horizontal separator line for the map
    separator_length_left = len(map_left[0]) * (num_digits_map_width + char_width + 1)
    print(print_map_left_offset + "=" * separator_length_left, end=gap_str)

    # Print the horizontal separator line for the table
    print("=" * (sum(max_col_widths) + len(max_col_widths) - 1))

    # Loop through each row to print map values and table rows
    for row_index, row_left in enumerate(map_left):
        print(str(row_index_label[row_index]).rjust(num_digits_map_height + 1), end=row_index_separator)
        for value in row_left:
            width = len(str(value))
            print(str(value).rjust(num_digits_map_width + char_width - (char_width - width)), end=" ")
        print(gap_str, end="")

        # Print the table row if it exists
        if row_index < len(table) - 1:  # Skip the header row
            table_row = table[row_index + 1]
            for i, cell in enumerate(table_row):
                print(str(cell).ljust(max_col_widths[i]), end=" " if i < len(table_row) - 1 else "\n")
        else:
            print()

    # If there are more rows in the table than the map, print the remaining rows
    for row_index in range(len(map_left), len(table) - 1):  # Skip the header row
        print(" " * (num_digits_map_height + len(row_index_separator) + len(map_left[0]) * (num_digits_map_width + char_width + 1) + gap), end="")
        table_row = table[row_index + 1]
        for i, cell in enumerate(table_row):
            print(str(cell).ljust(max_col_widths[i]), end=" " if i < len(table_row) - 1 else "\n")







def map_calculate_max_dimensions(height, width, label_left,
                                 label_right, row_index_label, column_index_label, gap):
    """
    Check if two maps of given dimensions and content will fit in the terminal using the simulation approach.
    Automatically fetches the terminal dimensions.

    Args:
        map_left, map_right, label_left, label_right, row_index_label, column_index_label, gap: Same as for print_two_maps

    Returns:
        bool: Whether the two maps will fit in the terminal.
    """

    try:
        # Redirect stdout to capture the output in a string
        old_stdout = sys.stdout
        new_stdout = StringIO()
        sys.stdout = new_stdout

        map_left = create_map(height, width, "x")
        # Run the print_two_maps function to simulate printing
        print_two_maps(map_left, map_left, label_left, label_right,
                       row_index_label, column_index_label, gap)

        # Reset stdout and get the captured string
        sys.stdout = old_stdout
        output_str = new_stdout.getvalue()


        # Automatically get terminal dimensions
        rows, columns = os.popen('stty size', 'r').read().split()
        terminal_width = int(columns)

        # Debug print statements


        # Check if any line in the captured output exceeds the terminal width
        will_fit = all(len(line) <= terminal_width for line in output_str.splitlines())

        return will_fit

    except Exception as e:
        return False






# CPU game play functions
# -----------------------


def cpu_deploy_all_ships(map_game, fleet, gaps, symbol):
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

                map_show_only_ships(map_game, symbol_space, symbol)
                # If no ships left to deploy, break the loop and return True
                return map_game  # Deployment is complete
            else:
                ship_size = ship_obj.size

                # Attempt to deploy the ship and get alignment and coordinates
                return_result = cpu_deploy_single_ship(map_game, ship_size,
                                                       symbol)

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
                symbol_space= "x"

                map_game = map_allocate_empty_space_for_ship(map_game,
                                                             coordinates_list,
                                                             symbol_space)

            map_game = map_show_symbols(map_game, coordinates_list,
                                        symbols_list)
        except Exception as e:
            # Handle exceptions if needed
            return False  # Return False on error


def map_show_only_ships(map, symbol_to_remove, default_symbol):
    for i in range(len(map)):
        for j in  range(len(map[0])):
            if map[i][j] == symbol_to_remove:
                map[i][j] = default_symbol
    return map

def map_show_symbols(map_game, coordinates_list, symbols_list):
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


def cpu_deploy_single_ship(map_game, ship_size, symbol):
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
    return_result = cpu_deploy_get_coordinates(map_game, ship_size, symbol)

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


def cpu_deploy_get_coordinates(map_game, ship_size, symbol):
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
        result = search_pattern(map_game, 1, 1, symbol)
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
                            1 if alignment == "Vertical" else ship_size, symbol)
    if result:
        return alignment, result

    # Try the other alignment
    alignment = alignments[0]  # Only one item should be left
    result = search_pattern(map_game,
                            1 if alignment == "Horizontal" else ship_size,
                            1 if alignment == "Vertical" else ship_size,
                            symbol)
    if result:
        return alignment, result

    return False  # No suitable coordinates found


def search_pattern(map_game, height, width, symbol_to_search):
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


    Returns:
        List[Tuple[int, int]]: A list of coordinates (row, col) where the
        pattern is found.
                               Returns an empty list if no pattern is found.
    """


    # Retrieve the dimensions of the game map
    map_height, map_width = len(map_game), len(map_game[0])

    # Initialize an empty list to collect coordinates where the pattern is
    # found
    coordinates = []

    # Create the pattern using list comprehension
    pattern = [symbol_to_search * width for _ in range(height)]

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

def create_coordinate_list(row, column, alignment, ship_size):
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


def map_allocate_empty_space_for_ship(map_game, coordinates_list, symbol):
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


"""Game Intro functions
---------------------"""


def print_acid_effect():
    """
    Prints a text art of an acid-like effect to the terminal.

    This function performs the following steps:
    1. Clears the terminal screen for a clean start.
    2. Prints each character of the `acid_text` string one by one with a
    slight delay.
    3. Waits for a short moment to let the user view the effect.
    4. Clears the terminal screen again.

    Note: The function uses the `os` and `time` modules.
    """
    # ASCII art representation of the acid effect

    acid_logo = """
                              _  |____________|  _
                       _=====| | |            | | |==== _
                 =====| |.---------------------------. | |====
   <--------------------'   .  .  .  .  .  .  .  .   '--------------/
     \\                                                             /
      \\_______________________________________________WWS_________/
  wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
   wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww

    """

    # Step 1: Clear the terminal
    clear_terminal()

    # Step 2: Print the text character by character
    for char in acid_logo:
        print(char, end='', flush=True)  # Using flush=True to force the
        # output to be printed
        time.sleep(0.005)  # Delay of 0.005 seconds for each character

    # Step 3: Wait for a moment to let the user view the effect
    time.sleep(1)

    # Step 4: Clear the terminal again
    clear_terminal()





"""
Game Instructions and settings
------------------------------
"""


def game_instructions():
    # Print Acid affect
    # print_acid_effect()

    # Create an instance with default settings
    current_game_settings = game_settings() # creating game settings
    current_game_fleet = create_fleet() #  creating default fleet


    while True:
        clear_terminal()
        tmp_fleet = create_fleet(current_game_fleet)
        tmp_map = tmp_ships_on_map(tmp_fleet, current_game_settings.height,
                                   current_game_settings.width,
                                   current_game_settings.gaps,
                                   current_game_settings.symbol)

        (print_map_and_list(tmp_map, LIST_INSTRUCTIONS, "Ships on Map",
                            "Instructions", current_game_settings.row_labels,
                            current_game_settings.col_labels, 5))

        try:
            user_input = input()
            if user_input.upper() in ["Y", "YES"]:
                current_game_settings, current_game_fleet = game_change_settings(
                    current_game_settings,
                                     current_game_fleet)

        except KeyboardInterrupt:
            clear_terminal()
            print("You have terminated program")
            return False  # Return False to indicate interruption



def tmp_ships_on_map(fleet_config, height, width, gaps, symbol):
    """
    Generate a temporary fleet of ships and display them on a map.
    This function provides a new map with a different pattern of ships each
    time.

    Args:
        game_settings: The settings for the game map.

    Returns:
        Union[bool, Tuple[List[List[Union[str, int]]], List]]:
            Returns False if the CPU cannot deploy all the ships.
            Otherwise, returns a tuple containing the updated game map and
            game settings.
    """

    # Create a default fleet for the game
    while True
        # Create a new game map of size 10x10
        tmp_map_game = create_map(height, width, symbol)
        tmp_fleet = create_fleet(fleet_config)

        # Deploy all ships on the game map
        tmp_map_game = cpu_deploy_all_ships(tmp_map_game, tmp_fleet, gaps,
                                          symbol)

        # Check if all ships were successfully deployed
        if not tmp_map_game:
            print("CPU cannot deploy all ships; they do not fit.")
            continue # continue till map is generated
        else:
            return tmp_map_game




def game_change_settings(game_settings, default_fleet):

    while True:
        clear_terminal()
        tmp_map = tmp_ships_on_map(default_fleet, game_settings.height,
                                   game_settings.width, game_settings.gaps,
                                   game_settings.symbol)

        print_map_and_list(tmp_map, LIST_GAME_SETTINGS_CHANGES, "Ships on Map",
                           "Settings", game_settings.row_labels,
                           game_settings.col_labels, 5)

        try:
            user_input = input()
            if len(user_input) == 1:
                if user_input == "0":
                    return game_settings, default_fleet
                print(user_input)
                if user_input.upper() == "M":
                    game_settings, default_fleet = settings_map_size_change(game_settings,
                                                              default_fleet)
                if user_input.upper() == "S":
                    game_settings, default_fleet = settings_coordinates(game_settings,
                                                          default_fleet)

            else:
                user_command_input(game_settings, default_fleet, user_input)


        except KeyboardInterrupt:
            clear_terminal()
            print("You have terminated game settings changes, I will return "
                  "back settings that I have at the moment")
            return False  # Return False to indicate interruption









def user_command_input(game_map_settings, default_fleet, user_input):

    while True:
        user_command = find_best_match(user_input.lower(), DICTIONARY_COMMANDS)
        clear_terminal()
        tmp_map = tmp_ships_on_map(default_fleet, game_map_settings.height,
                                   game_map_settings.width,
                                   game_map_settings.gaps,
                                   game_map_settings.symbol)
        if user_command == None:
            user_input_list = ["I am sorry but i did not understand",
                               "what You wanted to say", "",
                               "Please try following commands:", "",
                               "modify fleet    print fleet",
                               "modify ship    add ship    delete ship",
                               "change map size    gaps between ships",
                               "change coordinate labels    change input",
                               "start game    reset settings"]

        else:
            user_input_list = [f' You have entered: {user_input}', "",
                               "I believe you wanted to say:", "",
                               f'    {user_command}', "",
                               "If I am correct, just press ENTER", "",
                               "type 0 to go back"]

        print_map_and_list(tmp_map, user_input_list, "Ships on Map",
                           "User Command", game_map_settings.row_labels,
                           game_map_settings.col_labels, 5)

        try:
            user_input = input()
            if user_input.strip() == "":
                execute_user_command(user_command, game_map_settings, default_fleet)
            if len(user_input) == 1:
                if user_input == 0:
                    return game_map_settings, default_fleet
                print(user_input)


        except KeyboardInterrupt:
            clear_terminal()
            print("You have terminated game settings changes")
            return False # Return False to indicate interruption

def execute_user_command(user_command, game_settings, default_fleet):
    if user_command == "modify fleet":
        print("function to execute modify fleet")
    elif user_command == "print fleet":
        print("function to execute print fleet")
    elif user_command == "modify ship":
        print("function to execute modify ship")
    elif user_command == "add ship":
        print("function to execute add ship")
    elif user_command == "delete ship":
        print("function to execute delete ship")
    elif user_command == "change map size":
        game_map_settings = settings_map_size_change(game_settings, default_fleet)
    elif user_command == "gaps between ships":
        print("function to execute gaps between ships")
    elif user_command == "change coordinate labels":
        print("function to execute change coordinate labels")
    elif user_command == "change input":
        print("function to execute change input")
    elif user_command == "start game":
        print("function to execute start game")
    elif user_command == "reset settings":
        print("function to execute reset settings")


def settings_coordinates(game_settings, default_fleet):
    if game_settings.row_label_symbol.isnumeric():
        row_label_symbol = "Number"
    else:
        row_label_symbol = "Letter"
    if game_settings.column_label_symbol.isnumeric():
        column_label_symbol = "Number"
    else:
        column_label_symbol = "Letter"
    text_list = ["Current game Coordinate system is:",
                 f'Row labels are {row_label_symbol}',
                 f'Columns are {column_label_symbol}', "",
                 f'User input is {game_settings.input_style[0]} and '
                 f'{game_settings.input_style[1]}',"",
                 "To change Labels type L",
                 "To change input style press I"]
    while True:
        clear_terminal()
        tmp_map = tmp_ships_on_map(default_fleet, game_settings.height,
                                   game_settings.width, game_settings.gaps,
                                   game_settings.symbol)
        try:
            print_map_and_list(tmp_map, text_list, "Ships on Map",
                               "Change Map Size", game_settings.row_labels,
                               game_settings.col_labels, game_settings.maps_gap)
            user_input = input()
            if len(user_input) == 1:
                if user_input == "0":
                    return game_settings, default_fleet
                elif user_input.upper() == "L":
                    print("hhh")






        except KeyboardInterrupt:
            print("Game adjustment interrupted.")
            return False










def settings_map_size_change(game_settings, default_fleet):
    text_list = ["Current game settings are set to:","",
                 "Map Dimensions:", "",
                 f'Height: {game_settings.height}  Width: {game_settings.width}',"",
                 "If you would like to change it,",
                 "please type height and width",
                 "separated by comma"]
    while True:
        clear_terminal()
        tmp_map = tmp_ships_on_map(default_fleet, game_settings.height,
                                   game_settings.width,
                                   game_settings.gaps,
                                   game_settings.symbol)
        try:

            print_map_and_list(tmp_map, text_list, "Ships on Map",
                               "Change Map Size", game_settings.row_labels,
                               game_settings.col_labels, game_settings.maps_gap)

            user_input = input()
            if user_input == "0":
                return game_settings, default_fleet
            input_valid, split_input, output_text = validate_user_input(
                user_input, 2, "integer")
            if input_valid:
                # if input is valid, first we will check if map can be
                # fitted on terminal:

                # create tmp game settings
                height = int(split_input[0])
                width = int(split_input[1])
                tmp_game_settings = game_settings.clone()
                tmp_game_settings.height = height
                tmp_game_settings.width = width
                check_fit = map_calculate_max_dimensions(height,
                                                         width, "left",
                                                         "right",
                                                         tmp_game_settings.row_labels, tmp_game_settings.col_labels, tmp_game_settings.maps_gap)
                if not check_fit:
                    t_rows, t_columns = os.popen('stty size', 'r').read(

                    ).split()
                    terminal_height = int(t_rows)
                    terminal_width = int(t_columns)
                    text_list = ["Sorry, but map with given dimensions:",
                                 f'Height: {height} and Width: {width}', "",
                                 "Can't align on terminal with dimensions:",
                                 f'Width: {terminal_width} and Height: '
                                 f'{terminal_height}']
                    # now we will check if same map can be fitted,
                    # if coordinate labels are letters not integers:
                    if tmp_game_settings.column_label_symbol.isdigit():
                        tmp_game_settings.column_label_symbol = "a" # seting
                        # column labels symbol to letter
                        tmp_game_settings.width = width # generating list
                        # of column symbols
                        check_fit_2 = map_calculate_max_dimensions(height,
                                                                   width, "left",
                                                                   "right",
                                                                   tmp_game_settings.row_labels, tmp_game_settings.col_labels, tmp_game_settings.maps_gap)
                        if not check_fit_2:
                            add_text_list = ["",
                                             "Although there is way around "
                                             "it:", "",
                                             "You could switch Column Index "
                                             "Labels",
                                             "from numbers to letters"]
                            text_list.extend(add_text_list)
                elif check_fit:
                    #now will apply new heigth and width to
                    # tmp_game_map_settings, so it will regenerate labels if map
                    # check if map is bigger, if so create new labels
                    tmp_map = create_map(split_input[0],split_input[1],
                                         game_settings.symbol)
                    tmp_fleet = create_fleet()
                    tmp_map_game = check_fleet_fits_map(tmp_map, tmp_fleet,
                                                        tmp_game_settings.symbol,
                                                        tmp_game_settings.gaps)
                    if not tmp_map_game:
                        text_list = ["Sorry but I DON'T recommend",
                                     "Decreasing Map size with current fleet","",
                                     "If You still want to reduce Map",
                                     "I suggest reducing fleet first",
                                     "type :","",
                                     "change Fleet"]
                    else: # if all ships fit the fleet, we will apply new map
                        # dimensions to game setings
                        game_settings.height = tmp_game_settings.height
                        game_settings.width = tmp_game_settings.width
                        text_list = ["Current game settings are set to:","",
                                     "Map Dimensions:", "",
                                     f'Height: {game_settings.height}  Width: {game_settings.width}',"",
                                     "If you would like to change it,",
                                     "please type height and width",
                                     "separated by comma"]
            else:
                text_list = ["You have entered:", user_input, "",
                             "Sorry but your entered information is ",
                             "Not valid", "",
                             "I have found these errors:",""]
                text_list.extend(output_text)


            # Handle keyboard interrupts to exit the game gracefully
        except KeyboardInterrupt:
            print("Game adjustment interrupted.")
            return False





def check_fleet_fits_map(map_game, fleet_config, symbol, gaps):
    # this function will use cpu_deploy_all_ships in loop for 50 times,
    # till ships are deployed, if after 50 attempts no luck to deploy all of
    # them, it means ships do not fit on map, player has to reduce fleet
    for _ in range(50):
        tmp_fleet = create_fleet(fleet_config)

        # Create a new game map of size 10x10
        tmp_map = map_game

        # Deploy all ships on the game map
        map_game = cpu_deploy_all_ships(tmp_map, tmp_fleet,
                                        gaps, symbol)
        if not map_game:
            continue
        else:
            return map_game
    return False # if after 50 attempts fleet doe4s not fit map, we return
    # false












"""Initial game start functions
-----------------------------"""


def start_game():
    # Print Acid affect
    # print_acid_effect()

    # create game map settings just for current game session
    global DEFAULT_MAP_SETTINGS
    current_game_settings = game_settings()

    game_fleet_settings = create_fleet()

    map_cpu_display = create_map(current_game_settings.height,
                                 current_game_settings.width,
                                 current_game_settings.symbol)

    map_cpu_display = cpu_deploy_all_ships(map_cpu_display,
                                           game_fleet_settings,
                                           current_game_settings.gaps,
                                           current_game_settings.symbol)
    if not map_cpu_display:
        print(" cpu can not deploy all ships, do not fit")
        return False

    """print_map_and_list(map_cpu_display, LIST_INSTRUCTIONS, "Ships on Map",
                       "Instructions", game_map_settings, 10)"""

    print_two_maps(map_cpu_display, map_cpu_display, "Hidden", "Display",
                   current_game_settings.row_labels,
                   current_game_settings.col_labels,
                   10)

    # game_fleet_settings.print_fleet(["deployed_qty",
    # "deployed_coordinates"], game_map_settings)


game_instructions()

#start_game()

tomosius_setup = game_settings()
tomosius_fleet = create_fleet()
"""tomosius_setup.row_label_symbol = "a"
tomosius_setup.column_label_symbol = "a"
tomosius_setup.height = 10
tomosius_setup.width = 11

tomosius_map = tmp_ships_on_map(tomosius_fleet, tomosius_setup.height,
                                tomosius_setup.width, tomosius_setup.gaps,
                                tomosius_setup.symbol)
tomas_check = map_calculate_max_dimensions(tomosius_setup.height,
                                           tomosius_setup.width, "jonas", "etras",
                                           tomosius_setup.row_labels,
                                           tomosius_setup.col_labels,
                                           tomosius_setup.maps_gap)
print(tomas_check)

print_two_maps(tomosius_map, tomosius_map, "jonas", "etras",
               tomosius_setup.row_labels, tomosius_setup.col_labels, tomosius_setup.maps_gap)

rows, columns = os.popen('stty size', 'r').read().split()
terminal_height = int(rows)
terminal_width = int(columns)
ic(terminal_height, terminal_width)"""
#tomas = settings_map_size_change(tomosius_setup)
