from enum import Enum


class AlignmentOptions(int, Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    MANUAL = 3


class OrientationOptions(int, Enum):
    VERTICAL = 0
    HORIZONTAL = 1


class SPECIAL_KEYS(int, Enum):
    ENTER = 10
    ESCAPE = 27
    BACKSPACE = 127
    