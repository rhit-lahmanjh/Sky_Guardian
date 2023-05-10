from enum import Enum

class State(Enum):
    Grounded = 1
    Takeoff = 2
    Land = 3
    Wander = 4
    Scan = 9
    Hover = 10
    Drift = 11
    NoPad = 12