# battleship.py test.py - this code is for testing CPU vs CPU game


# Import required libraries
import random  # For generating random numbers
import copy  # For creating deep copies of data structures
import os  # For clearing the terminal screen
import time  # For time-related functionalities
import re  # For handling user input expressions
from difflib import SequenceMatcher
from typing import List, Optional


# Constants for map dimensions and default symbol
DEFAULT_MAP_HEIGHT = 10
DEFAULT_MAP_WIDTH = 10
DEFAULT_SYMBOL = '?'  # Symbol representing an empty cell in the map
DEFAULT_GAPS_BETWEEN_MAPS = True
DEFAULT_MAP_ROW_INDEXES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
DEFAULT_MAP_COLUMN_INDEXES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


# Define color codes for different ship statuses
DEFAULT_COLORS = {
	"DarkYellow": "\u001b[33m",  # Single cell ship
	"DarkBlue": "\u001b[34m",  # Horizontal ship
	"DarkGreen": "\u001b[32m",  # Vertical ship
	"DarkRed": "\u001b[31m",  # Damaged or Sunk ship
	"LightGray": "\u001b[37m",  # Miss
	"Reset": "\u001b[0m",  # Reset ANSI escape code in string
}

# Define symbols for different ship statuses
SHIP_SYMBOLS = {
	"Single": [DEFAULT_COLORS["DarkYellow"] + chr(0x25C6) + DEFAULT_COLORS[
		"Reset"]],
	"Horizontal": [
		DEFAULT_COLORS["DarkBlue"] + chr(0x25C0) + DEFAULT_COLORS["Reset"],
		DEFAULT_COLORS["DarkBlue"] + chr(0x25A4) + DEFAULT_COLORS["Reset"]
	],
	"Vertical": [
		DEFAULT_COLORS["DarkGreen"] + chr(0x25B2) + DEFAULT_COLORS["Reset"],
		DEFAULT_COLORS["DarkGreen"] + chr(0x25A5) + DEFAULT_COLORS["Reset"]
	],
	"Hit": [DEFAULT_COLORS["DarkRed"] + chr(0x25A6) + DEFAULT_COLORS[
		"Reset"]],
	"Miss": [DEFAULT_COLORS["LightGray"] + chr(0x2022) + DEFAULT_COLORS[
		"Reset"]],
	"SingleSunk": [DEFAULT_COLORS["DarkRed"] + chr(0x25C6) + DEFAULT_COLORS[
		"Reset"]],
	"HorizontalSunk": [
		DEFAULT_COLORS["DarkRed"] + chr(0x25C0) + DEFAULT_COLORS["Reset"],
		DEFAULT_COLORS["DarkRed"] + chr(0x25A4) + DEFAULT_COLORS["Reset"]
	],
	"VerticalSunk": [
		DEFAULT_COLORS["DarkRed"] + chr(0x25B2) + DEFAULT_COLORS["Reset"],
		DEFAULT_COLORS["DarkRed"] + chr(0x25A5) + DEFAULT_COLORS["Reset"]
	],
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


def levenshtein_ratio(a: str, b: str) -> float:
	"""
	Calculate the Levenshtein distance ratio between two strings.

	The ratio is a measure of similarity between two strings.
	A ratio of 1 means the strings are identical.

	Parameters:
		a (str): The first string for comparison.
		b (str): The second string for comparison.

	Returns:
		float: The Levenshtein distance ratio between the two strings.
	"""
	return SequenceMatcher(None, a, b).ratio()

def find_best_match(user_input: str, possible_commands: List[str]) -> Optional[str]:
	"""
	Find the best matching command based on user input and a list of possible commands.

	This function first normalizes the user input and each possible command.
	It then calculates the Levenshtein distance ratio between the normalized user input
	and each possible command to find the best match.

	Parameters:
		user_input (str): The user's input string.
		possible_commands (List[str]): A list of possible commands to match against.

	Returns:
		Optional[str]: The best-matching command, or None if no reasonable match is found.
	"""
	# Normalize the user input for comparison
	user_input = normalize_command(user_input)

	# Initialize variables to store the best match and its Levenshtein distance ratio
	max_ratio = -1
	best_match = None

	# Loop through each possible command to find the best match
	for command in possible_commands:
		# Normalize the possible command for comparison
		normalized_command = normalize_command(command)

		# Calculate the Levenshtein distance ratio between the normalized user input and the possible command
		ratio = levenshtein_ratio(user_input, normalized_command)

		# Update the best match and its ratio if the current ratio is higher
		if ratio > max_ratio:
			max_ratio = ratio
			best_match = command

	# A threshold is set for the Levenshtein distance ratio to consider a match as reasonable
	# This threshold can be adjusted as needed
	if max_ratio > 0.6:
		return best_match
	else:
		return None



