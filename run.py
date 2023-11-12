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

start_time = time.time()  # tamer will start with game



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
                              supports 'integer' and 'alpha' for single UK
                              alphabet letters.

    Returns:
        tuple: A tuple containing three elements:
            - A boolean indicating if the input is valid.
            - A tuple of the split parts after type conversion if applicable.
            - A list of string messages indicating validation status for
            each part.
    """

    # Use a regular expression to split the input into parts by any
    # non-alphanumeric character, removing any empty strings.
    split_input = re.split(r'[^A-Za-z0-9]+', input_str)
    # Initialize a flag to keep track of whether the entire input is valid
    input_valid = True

    # Initialize a list to hold text that describes the validation status
    # for each part
    output_text = []

    # Check if the number of parts obtained from the split operation matches
    # the expected number of parts
    if len(split_input) != parts:
        output_text.append(f'I need you to type in {parts} values.')
        return False, tuple(split_input), output_text

    # If a specific data type is expected for each part, perform type validation
    if type == 'integer':
        for i, part in enumerate(split_input):
            # Check if the part is an integer
            if not part.isdigit():
                output_text.append(f'Your input "{part}" is NOT an Integer.')
                input_valid = False
            else:
                # Convert the part to an integer for future use
                split_input[i] = int(part)
    elif type == 'alpha':
        for i, part in enumerate(split_input):
            # Check if the part is a single letter in the UK alphabet
            if not part.isalpha() or len(part) != 1:
                output_text.append(f'Your input "{part}" is NOT a single alphabet letter.')
                input_valid = False
            # No conversion needed for alphabet characters
    elif type is not None:
        # Raise an error if an unsupported type is specified
        raise ValueError(f"Unsupported type '{type}'. Supported types are 'integer' and 'alpha'.")

    # Return the final validity flag, the tuple of validated parts, and the list of validation messages
    return input_valid, tuple(split_input), output_text


def validate_values(value1, value2):
    """
    Validates two values to check whether each is a single-digit number or a 
    single-letter alphabet. Returns a list of warnings if any of these 
    checks fail, with each part of the message not exceeding 38 characters.

    Parameters:
        value1: The first value to be validated.
        value2: The second value to be validated.

    Returns:
        list: A list of warnings if the values do not comply with the type rules.
              An empty list indicates no warnings.
    """
    warnings = []

    # Function to add warnings in two parts
    def add_warnings(value):
        warnings.extend([f'You have entered {value}', "which is neither a digit nor a letter."])

    # Check each value and add warnings if it's neither a digit nor an alphabet letter
    if not (value1.isdigit() or value1.isalpha()):
        add_warnings(value1)
    if not (value2.isdigit() or value2.isalpha()):
        add_warnings(value2)

    return warnings






# Define the normalization function
def input_normalize_string(text_input):
    return ' '.join(sorted(text_input.lower().split()))

# Define the function to find unique words
def find_unique_words(command_dict):
    all_words = [word for commands in command_dict.values() for command in commands for word in command.split()]
    word_count = Counter(all_words)
    return {word for word, count in word_count.items() if count == 1}

# Define the main function to find the best match
def find_best_match(user_input, command_dict):
    normalized_input = input_normalize_string(user_input)
    unique_words = find_unique_words(command_dict)

    # If the input is exactly one of the unique words, return the corresponding full command
    if normalized_input in unique_words:
        for key, values in command_dict.items():
            for value in values:
                if normalized_input in value:
                    return [key]

    # If the input matches a unique word in any of the commands, return that command
    for unique_word in unique_words:
        if unique_word in normalized_input:
            for key, values in command_dict.items():
                for value in values:
                    if unique_word in value:
                        return [key]

    # If the input is a substring of any of the commands, return those command keys
    partial_matches = [key for key, values in command_dict.items() if any(normalized_input in command for command in values)]
    if partial_matches:
        return partial_matches

    # Otherwise, check for the closest match in the entire command dictionary
    max_ratio = 0
    best_match = None
    for key, values in command_dict.items():
        for command in values:
            ratio = SequenceMatcher(None, normalized_input, input_normalize_string(command)).ratio()
            if ratio > max_ratio:
                max_ratio = ratio
                best_match = key

    return [best_match] if best_match else None


def create_ship_dictionary_from_fleet(fleet):
    """
    Creates a dictionary from a Fleet instance where the keys are ship names and the values are
    lists containing the ship names in various common formats (e.g., with spaces, lowercase).

    Parameters:
        fleet (Fleet): An instance of the Fleet class.

    Returns:
        dict: A dictionary suitable for use with the find_best_match_v2 function.
    """
    ship_dictionary = {}
    for ship in fleet.ships:
        name_variants = [
            ship.name,                     # Original
            ship.name.replace(" ", ""),    # Without spaces
            ship.name.lower(),             # Lowercase
            ship.name.replace(" ", "").lower() # Lowercase without spaces
        ]
        # Add all variants to the dictionary pointing to the original ship name
        ship_dictionary[ship.name] = list(set(name_variants))  # Remove duplicates
    return ship_dictionary






# Managing Game Map and other Settings:
# -------------------------------------


class BattleshipGameInfo:
    """
    A class to represent the game state in Battleship, tracking actions for both players and CPUs.

    Attributes:
        actions (list of dict): List of dictionaries storing details of each action.
        timer (float): Time elapsed or remaining in the game.

    Methods:
        update_action(player_type, row, column, outcome): Updates the game state with the latest action.
        get_latest_action_by_player_type(player_type): Retrieves the latest action for a specific player type.
        start_timer(), update_timer(), stop_timer(): Timer management methods.
        reset_game(): Resets the entire game state for a new game.
    """

    def __init__(self):
        """
        Constructs all the necessary attributes for the BattleshipGameInfo object.
        """
        self.actions = []  # List to store actions
        self.timer = 0.0

    def update_action(self, player_type, row, column, outcome):
        """
        Updates the game state with the latest action.

        Args:
            player_type (str): The type of the player ('cpu' or 'player').
            row (int): The row number of the action.
            column (int): The column number of the action.
            outcome (str): Description of the action's outcome.
        """
        action = {
            "player_type": player_type,
            "row": row,
            "column": column,
            "outcome": outcome
        }
        self.actions.append(action)

    def get_latest_action_by_player_type(self, player_type):
        """
        Retrieves the details of the latest action for a given player type.

        Args:
            player_type (str): The type of the player ('cpu' or 'player').

        Returns:
            str: A formatted string containing the details of the latest action for the specified player type.
                 Returns a message if no action has been recorded for the player type.
        """
        for action in reversed(self.actions):
            if action['player_type'] == player_type:
                return (f"Time: {self.timer:.2f} seconds, "
                        f"Player Type: {action['player_type']}, "
                        f"Row: {action['row']}, Column: {action['column']}, "
                        f"Outcome: {action['outcome']}")
        return "No action has been recorded for this player type."

    def start_timer(self):
        """
        Starts the game timer.
        """
        self.timer_start = time.time()

    def update_timer(self):
        """
        Updates the timer with the elapsed time since the timer was started.
        """
        if hasattr(self, 'timer_start'):
            self.timer = time.time() - self.timer_start
        else:
            print("Timer has not been started.")

    def stop_timer(self):
        """
        Stops the timer and updates the timer attribute with the total time elapsed.
        """
        self.update_timer()
        if hasattr(self, 'timer_start'):
            del self.timer_start

    def reset_game(self):
        """
        Resets the entire game state to its initial values.
        This includes clearing the action logs and resetting the timer.
        """
        self.actions = []
        self.timer = 0.0
        if hasattr(self, 'timer_start'):
            del self.timer_start

    def __str__(self):
        """
        String representation of the current game state.

        Returns:
            str: Formatted game state information.
        """
        action_strings = [f"{action['player_type']} at Row: {action['row']}, Column: {action['column']} - {action['outcome']}"
                          for action in self.actions]
        actions_str = "\n".join(action_strings)
        return (f"Timer: {self.timer:.2f} seconds\nActions:\n{actions_str}")


class game_settings:
    """Class to hold default map settings for the Battleship game.

    Attributes:
        height (int): The height of the map (number of rows).
        width (int): The width of the map (number of columns).
        symbol (str): The default symbol to display on the map.
        gaps (bool): Whether to include gaps between ships.
        input_style (list): Input-output style ['Row', 'Column'] or [
        'Column', 'Row'].
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
            ships (List[Ship]): A list to store the Ship objects that belong to this fleet.
        """
        self.ships = []

    def add_ship(self, ship):
        """
        Add a Ship object to the fleet.
        Parameters:
            ship (Ship): The Ship object to be added to the fleet.
        """
        self.ships.append(ship)

    def remove_ships_by_name(self, name):
        """
        Remove all instances of ships with a given name from the fleet.

        Parameters:
            name (str): The name of the ships to be removed.

        Returns:
            int: The number of ships that were removed.
        """
        initial_ship_count = len(self.ships)
        self.ships = [ship for ship in self.ships if ship.name != name]
        removed_ship_count = initial_ship_count - len(self.ships)
        return removed_ship_count

    def get_ship(self, name, is_deployed=False):
        """
        Retrieve a Ship object from the fleet by its name and deployment status.
        Parameters:
            name (str): The name of the ship to retrieve.
            is_deployed (bool): Whether to retrieve a deployed ship (default False).
        Returns:
            Ship or None: The Ship object if found; None if not found.
        """
        for ship in self.ships:
            if ship.name == name and ship.deployed == is_deployed:
                return ship
        return None

    def get_ship_quantity(self, name, is_sunk=None, is_deployed=None):
        """
        Get the quantity of a specific type of ship in the fleet, with optional
        filters for sunk and deployed status.
        Parameters:
            name (str): The name of the ship to count.
            is_sunk (bool): If specified, filter ships by sunk status.
            is_deployed (bool): If specified, filter ships by deployed status.
        Returns:
            int: The number of ships of the specified type and status.
        """
        return sum(
            ship.name == name and
            (is_sunk is None or ship.sunk == is_sunk) and
            (is_deployed is None or ship.deployed == is_deployed)
            for ship in self.ships
        )

    def get_biggest_ship_by_deployed_status(self, is_deployed=False):
        """
        Get the biggest ship in the fleet based on deployed status.
        Parameters:
            is_deployed (bool): Whether to consider deployed ships (default False).
        Returns:
            Ship or None: The biggest ship object if found; None otherwise.
        """
        return max(
            (ship for ship in self.ships if ship.deployed == is_deployed),
            key=lambda x: x.size,
            default=None
        )

    def get_biggest_ship_by_sunk_status(self, is_sunk=False):
        """
        Get the biggest ship in the fleet based on sunk status.
        Parameters:
            is_sunk (bool): Whether to consider sunk ships (default
            False).
        Returns:
            Ship or None: The biggest ship object if found; None otherwise.
        """
        return max(
            (ship for ship in self.ships if ship.sunk == is_sunk),
            key=lambda x: x.size,
            default=None
        )

    def __str__(self):
        """
        Provide a string representation of the Fleet object.
        Returns:
            str: A string representation summarizing the fleet's status.
        """
        return "\n".join(
            f"{i+1}. {ship.name} (Size: {ship.size})\n"
            f"   Coordinates: {ship.cell_coordinates}\n"
            f"   Sunk: {'Yes' if ship.sunk else 'No'}\n"
            f"   Deployed: {'Yes' if ship.deployed else 'No'}"
            for i, ship in enumerate(self.ships)
        )

    def gather_basic_info(self):
        """
        Gather basic information about each ship in the fleet and sort by size.
        Returns:
            List[dict]: A sorted list of dictionaries containing basic information about each ship.
        """
        ship_info = {}
        for ship in self.ships:
            name = ship.name
            if name not in ship_info:
                ship_info[name] = {"name": name, "size": ship.size, "qty": 0}
            ship_info[name]["qty"] += 1

        # Convert the dictionary to a list and sort by ship size, descending
        ship_info_list = list(ship_info.values())
        ship_info_list.sort(key=lambda x: x['size'], reverse=True)

        return ship_info_list


    def apply_conditions_to_info(self, ship_info_list, conditions, game_settings):
        """
        Apply conditions to the ship information list.
        Parameters:
            ship_info_list (List[dict]): The list containing ship information.
            conditions (List[str]): The list of conditions to apply.
            game_settings (GameSettings): The game's coordinate style.
        """
        for condition in conditions:
            if condition == 'deployed_qty':
                self.add_quantity_condition(ship_info_list, 'deployed')
            elif condition == 'sunk_qty':
                self.add_quantity_condition(ship_info_list, 'sunk')
            elif 'coordinates' in condition:
                self.add_coordinates_condition(ship_info_list, condition, game_settings)

    def add_quantity_condition(self, ship_info_list, status_type):
        """
        Add the quantity of ships with a specific status (deployed/sunk) to the ship information list.
        Parameters:
            ship_info_list (List[dict]): The list containing ship information.
            status_type (str): The status type to filter by ('deployed' or 'sunk').
        """
        for info in ship_info_list:
            info[f"{status_type}_qty"] = self.get_ship_quantity(
                name=info['name'],
                is_sunk=True if status_type == 'sunk' else None,
                is_deployed=True if status_type == 'deployed' else None
            )

    def add_coordinates_condition(self, ship_info_list, condition, game_settings):
        """
        Add coordinates condition to the ship information list.
        Parameters:
            ship_info_list (List[dict]): The list containing ship information.
            condition (str): The condition to filter the coordinates.
            game_settings (GameSettings): The game's coordinate style.
        """
        status_type = condition.replace('_coordinates', '')
        for info in ship_info_list:
            ships = [ship for ship in self.ships if ship.name == info['name']]
            if status_type:
                ships = [ship for ship in ships if getattr(ship, status_type)]
            coordinates = [ship.cell_coordinates for ship in ships]
            info[condition] = self.format_coordinates(coordinates, game_settings)

    def format_coordinates(self, coordinates, game_settings):
        """
        Format the coordinates according to the game's coordinate style.
        Parameters:
            coordinates (List[tuple]): List of coordinates.
            game_settings (GameSettings): The game's map settings.
        Returns:
            List[str]: List of formatted coordinates.
        """
        # Implement coordinate formatting based on game settings.
        # This code assumes that 'game_settings' provides the necessary properties and methods.
        return game_settings.format_coordinates(coordinates)

    def fleet_to_table(self, game_settings, conditions):
        """
        Generate and return a table representation of the fleet information based on game settings and conditions.
        Parameters:
            game_settings (GameSettings): The game settings to use for formatting.
            conditions (List[str]): The list of conditions applied.
        Returns:
            List[List[Any]]: The table of ship information.
        """
        ship_info_list = self.gather_basic_info()
        self.apply_conditions_to_info(ship_info_list, conditions, game_settings)
        return self.convert_info_to_table(ship_info_list, conditions)

    def convert_info_to_table(self, ship_info_list, conditions):
        """
        Convert ship information list to a table format.
        Parameters:
            ship_info_list (List[dict]): The list containing ship information.
            conditions (List[str]): The list of conditions applied.
        Returns:
            List[List[Any]]: The table of ship information.
        """
        header = ["Name", "Size", "Qty"]
        header.extend(condition.replace('_', ' ').title() for condition in conditions)
        table = [header]
        for info in ship_info_list:
            row = [info['name'], info['size'], info['qty']]
            row.extend(info.get(condition, '') for condition in conditions)
            table.append(row)
        return table



    def add_new_ship(self, base_name, size, quantity):
        """
        Add a specified number of new ships to the fleet with a given base name and size.

        Parameters:
            base_name (str): The base name for the new ships.
            size (int): The size of the new ships.
            quantity (int): The quantity of new ships to be added.

        Note:
            This method does not append an index to the ship's name. If the base name
            already exists, it will simply add another ship with the same name.

        Returns:
            list: A list of the successfully added Ship objects.
        """
        added_ships = []
        for _ in range(quantity):
            # Create the new Ship object and add it to the fleet
            new_ship = Ship(name=base_name, size=size)
            self.add_ship(new_ship)
            added_ships.append(new_ship)

        return added_ships






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
        game_settings: Game map settings including row and column index
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
        game_settings: Game map settings including row and column index
        labels.
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
    symbol_allocate_space= "x"
    while True:
        try:
            # Get information about the biggest not deployed ship from the
            # fleet
            ship_obj = fleet.get_biggest_ship_by_deployed_status(False)

            if ship_obj is None:

                map_show_only_ships(map_game, symbol_allocate_space, symbol)
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
                map_game = map_allocate_empty_space_for_ship(
                    map_game, coordinates_list, symbol_allocate_space)

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
                            1 if alignment == "Vertical" else ship_size,
                            symbol)
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
                current_game_settings, current_game_fleet \
                    =game_change_settings( current_game_settings,
                                           current_game_fleet)
            else:
                return current_game_settings, current_game_fleet

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
    while True:
        # Create a new game map of size 10x10
        tmp_map_game = create_map(height, width, symbol)
        tmp_fleet = create_fleet(fleet_config)

        # Deploy all ships on the game map
        tmp_map_game = cpu_deploy_all_ships(tmp_map_game, tmp_fleet, gaps,
                                          symbol)

        # Check if all ships were successfully deployed
        if not tmp_map_game:
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
                elif user_input.upper() == "M":
                    game_settings, default_fleet = settings_map_size_change(
                        game_settings, default_fleet)
                elif user_input.upper() == "S":
                    game_settings, default_fleet = settings_coordinates(
                        game_settings, default_fleet)
                elif user_input.upper() == "F":
                    game_settings, default_fleet = settings_fleet(game_settings, default_fleet)



            else:
                user_command_input(game_settings, default_fleet, user_input)


        except KeyboardInterrupt:
            clear_terminal()
            print("You have terminated game settings changes, I will return "
                  "back settings that I have at the moment")
            return False  # Return False to indicate interruption









def user_command_input(game_settings, default_fleet, user_input):

    while True:
        user_command = find_best_match(user_input.lower(), DICTIONARY_COMMANDS)
        clear_terminal()
        tmp_map = tmp_ships_on_map(default_fleet, game_settings.height,
                                   game_settings.width,
                                   game_settings.gaps,
                                   game_settings.symbol)
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
                           "User Command", game_settings.row_labels,
                           game_settings.col_labels, 5)

        try:
            user_input = input()
            if user_input.strip() == "":
                execute_user_command(user_command, game_settings,
                                     default_fleet)
            if len(user_input) == 1:
                if user_input == 0:
                    return game_settings, default_fleet
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
        game_settings = settings_map_size_change(game_settings,
                                                     default_fleet)
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
                               game_settings.col_labels,
                               game_settings.maps_gap)
            user_input = input()
            if len(user_input) == 1:
                if user_input == "0":
                    return game_settings, default_fleet
                elif user_input.upper() == "L":
                    game_settings, default_fleet =  settings_label_change(
                        game_settings, default_fleet)
                elif user_input.upper() == "I":
                    game_settings, default_fleet = settings_input(
                        game_settings, default_fleet)






        except KeyboardInterrupt:
            print("Game adjustment interrupted.")
            return False



def settings_label_change(game_settings, default_fleet):
    value_0, value_1 = input_output_swap("Row", "Column",
                                         game_settings.input_style[0],
                                         game_settings.input_style[1])
    string_0 = "Row labels are presented as: {}".format("DIGIT" if
                                                       game_settings.row_label_symbol.isdigit() else "LETTER")
    string_1 = "Column labels are presented as: {}".format("DIGIT" if
                                                           game_settings.column_label_symbol.isdigit() else "LETTER")
    string_0, string_1 = input_output_swap(string_0, string_1,
                                           game_settings.input_style[0],
                                           game_settings.input_style[1])



    text_list = [
        "Current settings for MAP:",
        "",
        string_0,
        string_1,
        "",
        "If you want to change it, please type in:",
        f'{value_0}, {value_1} symbols, example:',
        f'A,1 = {value_0} - Letters, {value_1} - Digits',"",
        "To go to previous menu type 0"]
    while True:
        clear_terminal()
        tmp_map = tmp_ships_on_map(default_fleet, game_settings.height,
                                   game_settings.width,
                                   game_settings.gaps,
                                   game_settings.symbol)
        try:
            print_map_and_list(tmp_map, text_list, "Ships on Map",
                               "Change Map Labels",
                               game_settings.row_labels,
                               game_settings.col_labels,
                               game_settings.maps_gap)
            user_input = input()
            #prcessing user input:
            input_valid, split_input, output_text = validate_user_input(
                    user_input, 2,)
            if input_valid:  # if user entered 2 values, we will identify
            # are they numbers or letters, and are they valid
                input_0, input_1 = input_output_swap(split_input[0],
                                                      split_input[1], game_settings.input_style[0],
                                                      game_settings.input_style[1])
                warnings = validate_values(input_0, input_1)
                if not warnings:
                    game_settings.row_label_symbol = input_0
                    game_settings.column_label_symbol = input_1
                    game_settings.update_labels()


                    value_0, value_1 = input_output_swap("Row", "Column",
                                                         game_settings.input_style[0],
                                                         game_settings.input_style[1])
                    string_0 = "Row labels are presented as: {}".format("DIGIT" if
                                                                        game_settings.row_label_symbol.isdigit() else "LETTER")
                    string_1 = "Column labels are presented as: {}".format("DIGIT" if
                                                                           game_settings.column_label_symbol.isdigit() else "LETTER")
                    string_0, string_1 = input_output_swap(string_0, string_1,
                                                           game_settings.input_style[0],
                                                           game_settings.input_style[1])



                    text_list = [
                        "Current settings for MAP:",
                        "",
                        string_0,
                        string_1,
                        "",
                        "If you want to change it, please type in:",
                        f'{value_0}, {value_1} symbols, example:',
                        f'A,1 = {value_0} - Letters, {value_1} - Digits',"",
                        "To go to previous menu type 0"]







                else:
                    text_list = ["Sorry but there is an error:","",]
                    text_list.extend(warnings)
            else:
                text_list = output_text
                print("tomas")
                print(output_text)
            if user_input == "0":
                return game_settings, default_fleet



        except KeyboardInterrupt:
            print("Game adjustment interrupted.")
            return False


def settings_input(game_settings, default_fleet):
    """
    Prompt the user to change the input style settings for the game.

    This function displays the current input style and allows the user to input
    a new style. If the input is valid and represents a change, the input style
    is updated.

    Args:
        game_settings (game_settings): The game settings object to be updated.
        default_fleet (list): The default fleet configuration.

    Returns:
        tuple: Updated game settings and default fleet if the user does not interrupt.
        bool: False if the user interrupts with a KeyboardInterrupt.
    """

    # Determine the current input style based on the default settings
    value_0, value_1 = input_output_swap("Row", "Column",
                                         game_settings.input_style[0],
                                         game_settings.input_style[1])

    text_list = [
        "Current input style:",
        f'{value_0} , {value_1}', "",
        "To change, type:",
        f'{value_1},{value_0} or {value_1[0]},{value_0[0]}', "",
        "This changes IO style.",
        "Type 0 for previous menu."
    ]

    while True:
        clear_terminal()
        tmp_map = tmp_ships_on_map(default_fleet, game_settings.height,
                                   game_settings.width, game_settings.gaps,
                                   game_settings.symbol)
        try:
            print_map_and_list(tmp_map, text_list, "Ships on Map",
                               "Change Input Style",
                               game_settings.row_labels,
                               game_settings.col_labels,
                               game_settings.maps_gap)
            user_input = input()
            if user_input == "0":
                return game_settings, default_fleet
            elif user_input.strip() == "":
                value_0, value_1 = input_output_swap("Row", "Column",
                                                     game_settings.input_style[0],
                                                     game_settings.input_style[1])
                text_list = [
                    "Current input style:",
                    f'{value_0} , {value_1}', "",
                    "To change, type:",
                    f'{value_1},{value_0} or {value_1[0]},{value_0[0]}', "",
                    "This changes IO style.",
                    "Type 0 for previous menu."
                ]
            else:


                # Check if user has input just 2 values
                input_valid, split_input, output_text = validate_user_input(
                    user_input, 2)
                if input_valid:
                    # checking if those given 2 values are row and column,
                    # or at least first letters of those words:
                    if (split_input[0][0].upper() == value_1[0].upper() and
                            split_input[1][0].upper() == value_0[0].upper()):
                        # Update the input style based on user input
                        game_settings.input_style = [value_1, value_0]

                    # Update the prompt text to reflect the changes
                    value_0, value_1 = game_settings.input_style
                    text_list = [
                        "Current input style:",
                        f'{value_0} , {value_1}', "",
                        "To change, type:",
                        f'{value_1},{value_0} or {value_1[0]},{value_0[0]}', "",
                        "This changes IO style.",
                        "Type 0 for previous menu."
                    ]

                else:
                    # If values are not understood, show the error message
                    text_list = output_text

        except KeyboardInterrupt:
            print("Game adjustment interrupted.")
            return False



def input_output_swap(input_style1, input_style2, default_style1, default_style2):
    """
    Swap input styles if they are in the reverse order of the default styles.

    This function is intended to be used after the input styles have been validated.
    It checks if the provided input styles are in the reverse order compared to the
    default styles. If they are, the input styles are swapped to match the default
    order; otherwise, they are returned as provided.

    Args:
        input_style1 (str): The first input style potentially to swap.
        input_style2 (str): The second input style potentially to swap.
        default_style1 (str): The first default style to compare against.
        default_style2 (str): The second default style to compare against.

    Returns:
        (str, str): A tuple of two strings representing the input styles in the correct order.
    """
    # Simplify comparison by using the first character of each style, capitalized.

    if default_style1 == "Row" and default_style2 == "Column":
        return input_style1, input_style2
    else:
        return input_style2, input_style1




def settings_map_size_change(game_settings, default_fleet):
    text_list = ["Current game settings are set to:","",
                 "Map Dimensions:", "",
                 f'Height: {game_settings.height} Width:'
                 f' {game_settings.width}',"",
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
                check_fit = map_calculate_max_dimensions(
                    height, width, "left", "right",
                    tmp_game_settings.row_labels,
                    tmp_game_settings.col_labels, tmp_game_settings.maps_gap)
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
                        tmp_game_settings.column_label_symbol = "a" # setting
                        # column labels symbol to letter
                        tmp_game_settings.width = width # generating list
                        # of column symbols
                        check_fit_2 = map_calculate_max_dimensions(
                            height, width, "left", "right",
                            tmp_game_settings.row_labels,
                            tmp_game_settings.col_labels,
                            tmp_game_settings.maps_gap)
                        if not check_fit_2:
                            add_text_list = ["",
                                             "Although there is way around "
                                             "it:", "",
                                             "You could switch Column Index "
                                             "Labels",
                                             "from numbers to letters"]
                            text_list.extend(add_text_list)
                elif check_fit:
                    #now will apply new height and width to
                    # tmp_game_settings, so it will regenerate labels if
                    # map
                    # check if map is bigger, if so create new labels
                    tmp_map = create_map(split_input[0],split_input[1],
                                         game_settings.symbol)
                    tmp_fleet = create_fleet(default_fleet)
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
                        # dimensions to game settings
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


def settings_fleet(game_settings, default_fleet):
    text_list = [["    Add ship - type A"],["    Modify Ship - type M"],
                 ["    Delete ship - type D"],["    Return to previous Menu - "
                                               "type 0"]]
    while True:
        clear_terminal()
        tmp_map = tmp_ships_on_map(default_fleet, game_settings.height,
                                   game_settings.width,
                                   game_settings.gaps,
                                   game_settings.symbol)
        try:

            fleet_table = default_fleet.fleet_to_table(game_settings,
                                                       [])
            fleet_table.extend(text_list)
            print_map_and_table(tmp_map, fleet_table, "Ships On Map",
                                "Fleet", game_settings.row_labels, game_settings.col_labels, game_settings.maps_gap)


            user_input = input()
            if len(user_input) == 1:
                if user_input == "0":
                    return game_settings, default_fleet
                elif user_input.upper() == "A":
                    game_settings, default_fleet = settings_fleet_add_ship(game_settings, default_fleet)
                elif user_input.upper() == "M":
                    game_settings, default_fleet = settings_fleet_change_ship(game_settings, default_fleet)
                elif user_input.upper() == "D":
                    game_settings, default_fleet = settings_fleet_delete_ship(
                        game_settings, default_fleet)

        except KeyboardInterrupt:
            print("Game adjustment interrupted.")
            return False



def settings_fleet_delete_ship(game_settings, default_fleet):
    fleet_table = default_fleet.fleet_to_table(game_settings,
                                               [])
    text_list = [["To Delete ship type in ship name"],
                 ["Or type in ship index number:"],
                 [f'Egzample 1 - {fleet_table[1][0]}'],
                 ["Return to previous menu type - 0"]]
    while True:
        clear_terminal()
        tmp_map = tmp_ships_on_map(default_fleet, game_settings.height,
                                   game_settings.width,
                                   game_settings.gaps,
                                   game_settings.symbol)
        try:

            fleet_table = default_fleet.fleet_to_table(game_settings,
                                                       [])
            fleet_index = len(fleet_table)
            fleet_table.extend(text_list)
            print_map_and_table(tmp_map, fleet_table, "Ships On Map",
                                " Delete ship from Fleet",
                                game_settings.row_labels, game_settings.col_labels, game_settings.maps_gap)



            user_input = input()
            if len(user_input) >0:
                if user_input.isdigit():
                    if user_input == "0":
                        return game_settings, default_fleet

                    elif 1 <= int(user_input) <= int(fleet_index):
                        ship_name = fleet_table[int(user_input)][0]
                        ship_size = fleet_table[int(user_input)][1]
                        ship_qty = fleet_table[int(user_input)][2]
                        default_fleet.remove_ships_by_name(ship_name)
                        text_list = [["You have removed ship:"],
                                     [ship_name, ship_size, ship_qty],[""],
                                     ["Return to previous menu type - 0"]]

                    else:
                        text_list = [[f'You have entered {user_input}'],
                                     ["There is no ship with such index"]]

                else:
                    if user_input.upper() == "Y":
                        default_fleet.remove_ships_by_name(ship_name[0])
                        text_list = [["You have removed ship:"],
                             [ship_name, ship_size, ship_qty],[""],
                             ["Return to previous menu type - 0"]]
                    else:


                        ship_dictionary = create_ship_dictionary_from_fleet(default_fleet)

                        ship_name = find_best_match(user_input, ship_dictionary)

                        if ship_name is not None:
                            ship_test = default_fleet.get_ship(ship_name[0])
                            ship_size = ship_test.size
                            ship_qty = default_fleet.get_ship_quantity(
                                ship_name[0])
                            text_list = [["You have selcted to delete:"],
                                         [ship_name[0], ship_size, ship_qty],
                                         ["To delete it type Y"],
                                         ["Return to previous menu type - 0"]]

                        else:
                            text_list = [["Sorry I did not understand your "
                                          "input"],
                                         ["Please try again typing ship name"],
                                         [""],
                                         ["Return to previous menu type - 0"]]



            else:
                fleet_table = default_fleet.fleet_to_table(game_settings,
                                                           [])
                text_list = [["To Delete ship type in ship name"],
                             ["Or type in ship index number:"],
                             [f'Egzample 1 - {fleet_table[1][0]}'],
                             ["Return to previous menu type - 0"]]


        except KeyboardInterrupt:
            print("Game adjustment interrupted.")
            return False



def settings_fleet_change_ship(game_settings, default_fleet):
    fleet_table = default_fleet.fleet_to_table(game_settings,
                                               [])
    text_list = [["To Modify ship type in ship name"],
                 ["Or type in ship index number:"],
                 [f'Egzample 1 - {fleet_table[1][0]}'],
                 ["Return to previous menu type - 0"]]
    while True:
        clear_terminal()
        tmp_map = tmp_ships_on_map(default_fleet, game_settings.height,
                                   game_settings.width,
                                   game_settings.gaps,
                                   game_settings.symbol)
        try:

            fleet_table = default_fleet.fleet_to_table(game_settings,
                                                       [])
            fleet_index = len(fleet_table)
            fleet_table.extend(text_list)
            print_map_and_table(tmp_map, fleet_table, "Ships On Map",
                                " Change Ship in Fleet",
                                game_settings.row_labels, game_settings.col_labels, game_settings.maps_gap)



            user_input = input()
            if len(user_input) >0:
                if user_input.isdigit():
                    if user_input == "0":
                        return game_settings, default_fleet

                    elif 1 <= int(user_input) <= int(fleet_index):
                        ship_name = fleet_table[int(user_input)][0]
                        game_settings, default_fleet = settings_fleet_change_selected_ship(game_settings,
                                                            default_fleet,
                                                            ship_name)





                    else:
                        text_list = [[f'You have entered {user_input}'],
                                     ["There is no ship with such index"]]

                else:
                    if user_input.upper() == "Y":
                        text_list = [["You have removed ship:"],
                                     [ship_name, ship_size, ship_qty],[""],
                                     ["Return to previous menu type - 0"]]
                    else:


                        ship_dictionary = create_ship_dictionary_from_fleet(default_fleet)

                        ship_name = find_best_match(user_input, ship_dictionary)

                        if ship_name is not None:
                            ship_test = default_fleet.get_ship(ship_name[0])
                            ship_size = ship_test.size
                            ship_qty = default_fleet.get_ship_quantity(
                                ship_name[0])
                            text_list = [["You have selcted to delete:"],
                                         [ship_name[0], ship_size, ship_qty],
                                         ["To change it type Y"],
                                         ["Return to previous menu type - 0"]]

                        else:
                            text_list = [["Sorry I did not understand your "
                                          "input"],
                                         ["Please try again typing ship name"],
                                         [""],
                                         ["Return to previous menu type - 0"]]


            else:
                fleet_table = default_fleet.fleet_to_table(game_settings,
                                                           [])
                text_list = [["To Delete ship type in ship name"],
                             ["Or type in ship index number:"],
                             [f'Egzample 1 - {fleet_table[1][0]}'],
                             ["Return to previous menu type - 0"]]


        except KeyboardInterrupt:
            print("Game adjustment interrupted.")
            return False



def settings_fleet_change_selected_ship(game_settings, default_fleet,
                                        ship_name):
    ship_info = default_fleet.get_ship(ship_name)
    ship_size = ship_info.size
    ship_qty = default_fleet.get_ship_quantity(ship_name)
    text_list = [["To change ship Enter Values:"],[""],
                 ["2 Values:"],["Size, QTY"],[""],
                 ["3 Values:"],["New Name, Size, QTY"],[""],
                 ["To go back type 0"]]
    while True:
        try:
            fleet_table = [['Name', 'Size', 'Qty'],
                           [ship_name, ship_size, ship_qty]]
            fleet_table.extend(text_list)
            clear_terminal()
            tmp_map = tmp_ships_on_map(default_fleet, game_settings.height,
                                       game_settings.width,
                                       game_settings.gaps,
                                       game_settings.symbol)
            print_map_and_table(tmp_map, fleet_table, "Ships On Map",
                                " Your selected Ship",
                                game_settings.row_labels, game_settings.col_labels,
                                game_settings.maps_gap)
            user_input = input()
            if user_input == "0":
                return game_settings, default_fleet
            else:
                input_parts = re.split(r'[^A-Za-z0-9]+', user_input)

                # now we shall check how many values user has used, if 2:
                if len(input_parts) == 2:
                    input_valid, split_input, output_text = (
                        validate_user_input(
                            user_input, 2, "integer"))
                    if input_valid:
                        # if both values are integers, we will test if given
                        # ship modification in fleet will fit on map:
                        new_ship_name = ship_name
                        new_ship_size = split_input[0]
                        new_ship_qty = split_input[1]
                        test_map = create_map(game_settings.height,
                                              game_settings.width,
                                              game_settings.symbol)
                        test_fleet = create_fleet(default_fleet)
                        test_fleet.remove_ships_by_name(ship_name)
                        test_fleet.add_new_ship(new_ship_name, new_ship_size,
                                                new_ship_qty)
                        result = check_fleet_fits_map(test_map,
                                                      test_fleet,
                                                      game_settings.symbol,
                                                      game_settings.maps_gap)
                        if not result:
                            text_list = [[""],["I do not recommend such ship:"],
                                         [new_ship_name, new_ship_size,
                                          new_ship_qty],
                                         ["Try smaller size or "
                                          "quantity"], ["To go back type 0"]]
                        else:
                            default_fleet = create_fleet(test_fleet)
                            return game_settings, default_fleet

                    else:
                        text_list = [""]
                        text_list.append(output_text)
                elif len(input_parts) == 3:
                    new_ship_size = int(input_parts[1])
                    new_ship_qty = int(input_parts[2])
                    size_qty_string = ', '.join([str(new_ship_size),
                                                 str(new_ship_qty)])
                    new_ship_name = input_parts[0]
                    input_valid, split_input, output_text = (
                        validate_user_input(
                            size_qty_string, 2, "integer"))
                    if input_valid:
                        # if both values are integers, we will test if given
                        # ship modification in fleet will fit on map:
                        new_ship_size = split_input[0]
                        new_ship_qty = split_input[1]
                        test_map = create_map(game_settings.height,
                                              game_settings.width,
                                              game_settings.symbol)
                        test_fleet = create_fleet(default_fleet)
                        test_fleet.remove_ships_by_name(ship_name)
                        test_fleet.add_new_ship(new_ship_name, new_ship_size,
                                                new_ship_qty)
                        result = check_fleet_fits_map(test_map,
                                                      test_fleet,
                                                      game_settings.symbol,
                                                      game_settings.maps_gap)
                        if not result:
                            text_list = [[""], ["I do not recommend such ship:"],
                                         [new_ship_name, new_ship_size,
                                          new_ship_qty],
                                         ["Try smaller size or "
                                          "quantity"], ["To go back type 0"]]
                        else:
                            default_fleet = create_fleet(test_fleet)
                            return game_settings, default_fleet

                    else:
                        text_list = [""]
                        text_list.append(output_text)
                else:

                    text_list = [["To change ship Enter Values:"],
                                 ["2 Values:"], ["Size, QTY"],
                                 ["3 Values:"], ["New Name, Size, QTY"], [""],
                                 ["ERROR. You have entered:"],
                                 [f'{len(input_parts)} number of values'],
                                 ["To go back type 0"]]






        except KeyboardInterrupt:
            print("Game adjustment interrupted.")
            return False





def settings_fleet_add_ship(game_settings, default_fleet):
    text_list = [["Type ship name, size and quantity"],
                 ["Egzample: Tugboat,1,4"], ["To go back type 0"]]
    while True:
        clear_terminal()
        tmp_map = tmp_ships_on_map(default_fleet, game_settings.height,
                                   game_settings.width,
                                   game_settings.gaps,
                                   game_settings.symbol)
        try:

            fleet_table = default_fleet.fleet_to_table(game_settings,
                                                       [])
            fleet_table.extend(text_list)
            print_map_and_table(tmp_map, fleet_table, "Ships On Map",
                                " Add Ship to Fleet",
                                game_settings.row_labels, game_settings.col_labels, game_settings.maps_gap)


            user_input = input()
            if len(user_input) > 0:
                if user_input == "0":
                    return game_settings, default_fleet
                # checking if user has provided 3 values
                input_valid, split_input, output_text = validate_user_input(
                    user_input, 3)
                if input_valid:
                    #checking if ship name is unique to fleet:
                    ship_name = split_input[0]
                    ship_test = default_fleet.get_ship(ship_name)
                    if not ship_test:
                        # checking if last 2 values are integers
                        ship_size = int(split_input[1])
                        ship_qty = int(split_input[2])
                        size_qty_string = ', '.join([str(ship_size),
                                                     str(ship_qty)])
                        input_valid, split_input, output_text = (
                            validate_user_input(
                                size_qty_string, 2, "integer"))
                        if input_valid:

                            # now all validation is done, we will check if
                            # modified fleet will fit on map
                            # generating temporary map and fleet
                            test_map = create_map(game_settings.height,
                                                  game_settings.width,
                                                 game_settings.symbol)
                            test_fleet = create_fleet(default_fleet)
                            test_fleet.add_new_ship(ship_name, ship_size, ship_qty)
                            result = check_fleet_fits_map(test_map,
                                                        test_fleet,
                                                          game_settings.symbol, game_settings.maps_gap)
                            if not result:
                                text_list = [["I do not recommend such ship:"],
                                             [ship_name, ship_size, ship_qty],
                                             ["Try smaller size or "
                                              "quantity"], ["To go back type 0"]]
                            else:
                                default_fleet = create_fleet(test_fleet)



                        else:
                            text_list = []
                            text_list.append(output_text)
                    else:
                        text_list.append([f'{split_input[0]} already exists '
                                          f'in fleet'])





                else:
                    text_list.append(output_text)
            else:
                text_list = [["Type ship name, size and quantity"],
                             ["Egzample: Tugboat,1,4"], ["To go back type 0"]]




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





""" CPU move functions
----------------------"""

def cpu_move(map_hidden, map_display,fleet, cpu_actions_log, game_settings,
             game_log):
    #checking is there any recorded hit shots in log:
    player_name = "CPU"
    if len(cpu_actions_log) == 0:
        ship_obj = fleet.get_biggest_ship_by_sunk_status(False)

        if ship_obj is None:
            print("Game Over")
            return  map_hidden, map_display, fleet
        else:
            ship_size = ship_obj.size


    else:
        print("keep killing exsisting ship")


def cpu_find_biggest_ship_on_map(map_game, size, symbol):
    """
    Searches for the biggest ship on the map represented by a specific symbol.

    Args:
    map_game (list): The game map or grid.
    size (int): The initial size parameter for the ship.
    symbol (str): The symbol representing the ship.

    Returns:
    list: List of center coordinates of the largest ship found.
    """
    # Initialize an empty list for storing coordinates
    coordinates_list = []

    # Begin with the maximum possible size
    width = size * 2 - 1
    height = size * 2 - 1

    # Main loop to find the biggest ship
    while True:
        coordinates_list = search_pattern(map_game, height, width, symbol)

        # If coordinates are found, calculate their center and return
        if coordinates_list:
            return get_coordinates_center(height, width, coordinates_list)

        # If not found, reduce the dimensions and search again
        else:
            width -= 1
            coordinates_list = search_pattern(map_game, height, width, symbol)
            if coordinates_list:
                width_center_list = get_coordinates_center(height, width,
                                                       coordinates_list)
            else:
                width_center_list = []

            # Restore width and reduce height for the next search
            width += 1
            height -= 1
            coordinates_list = search_pattern(map_game, height, width, symbol)
            if coordinates_list:
                height_center_list = get_coordinates_center(height, width,
                                                        coordinates_list)
            else:
                height_center_list = []

            # Combine results from width and height reductions
            center_list = width_center_list + height_center_list

            # Return if centers are found
            if center_list:
                return center_list
            else:
                width -=1 # reducing width, height is already reduced

            # Check for minimum dimensions to avoid infinite loop
            if width < size or height < size:
                break

    return []  # Return an empty list if no ship is found


def get_coordinates_center(height, width, coordinates_list):
    """
    Calculates the center coordinates for a given height and width of a grid,
    and applies this calculation to a list of coordinates.

    Args:
        height (int): The height of the grid.
        width (int): The width of the grid.
        coordinates_list (list of tuples): A list of coordinates (row, column).

    Returns:
        list of tuples: A list containing the center coordinates.
    """
    center_rows = calculate_center(height)
    center_columns = calculate_center(width)

    center_list = []
    for coord_row, coord_column in coordinates_list:
        for center_row in center_rows:
            for center_column in center_columns:
                final_row = coord_row + center_row
                final_column = coord_column + center_column
                center_list.append((final_row, final_column))

            return center_list


def calculate_center(dimension):
    """
    Calculates the center points for a given dimension.

    Args:
        dimension (int): The dimension of the grid (either height or width).
    Returns:
        list: A list of center point(s).
    """

    if dimension % 2 == 1:
        return [dimension // 2]
    else:
        return [dimension // 2 - 1, dimension // 2]


"""Initial game start functions
-----------------------------"""


def start_game():
    # Print Acid affect
    # print_acid_effect()

    # create game map settings just for current game session
    game_settings, default_fleet = game_instructions()
    game_log = BattleshipGameInfo()

#start_game()


def cpu_loop():
    game_log = BattleshipGameInfo()