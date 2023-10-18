# battleship.py test.py - this code is for testing CPU vs CPU game


# Import required libraries
import random  # For generating random numbers
import copy  # For creating deep copies of data structures
import os  # For clearing the terminal screen
import time  # For time-related functionalities
import re  # For handling user input expressions


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

