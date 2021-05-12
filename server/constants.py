from enum import IntEnum
from collections import OrderedDict
import string

class GameState(IntEnum):
    LOBBY = 1
    SETUP_BOARDS = 2
    TURN_START = 3
    TURN_END = 4

# global state object for the app.
STATE = {
    # game_state stores the current state of the game's finite state machine
    "game_state": GameState.LOBBY, 
    # whether a state has changed in the last game update
    "entering_state": True, 
    "game_boards": OrderedDict(),
    "attacks": {}
}

# Users are all connected clients
USERS = set()
# Players are clients who are actively playing the game (i.e. they are assigned to a board)
PLAYERS = set()

MAX_UPDATES_PER_SECOND = 60
UPDATE_DELAY_DELTA = 1./MAX_UPDATES_PER_SECOND

AXIS_NUMBERS=range(1, 11)
AXIS_LETTERS=string.ascii_uppercase[0:10]
