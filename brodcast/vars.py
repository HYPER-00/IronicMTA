from enum import Enum

class AseVersion(Enum):
    """
        Ase Queries Versions
        * 1.Y  => Normal
        * 1.Yn => For mta developers & other versions
    """
    v1_5  = "1.5"
    v1_5n = "1.5n"

    v1_6 = "1.6"
    v1_6n = "1.6n"

class BuildType(Enum):
    """
        MTA Server Build Types
    """
    custom = 1
    experimental = 3
    unstable = 5
    untested = 7
    release = 9
