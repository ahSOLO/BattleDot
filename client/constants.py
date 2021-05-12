from enum import IntEnum
import string

class GameState(IntEnum):
    LOBBY = 1
    SETUP_BOARDS = 2
    TURN_START = 3
    TURN_END = 4

class ClientState(IntEnum):
    DEFAULT = 0
    LOBBY_UNREADY = 1
    LOBBY_READY = 2
    NEW_OPPONENT = 3
    BEFORE_MOVE = 4
    AFTER_MOVE = 5
    OBSERVER = 6

STATE = {"websocket": None, "client_state" : ClientState.DEFAULT, "previous_targets" : set()}

MAX_UPDATES_PER_SECOND = 60
UPDATE_DELAY_DELTA = 0 # 1./MAX_UPDATES_PER_SECOND

AXIS_NUMBERS=range(1, 11)
AXIS_LETTERS=string.ascii_uppercase[0:10]