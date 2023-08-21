from enum import Enum


class HttpDownloadTypes:
    """
        Http download types
        * Disables
        * Enables Port
        * Enables URL
    """

    def __init__(self) -> None:
        self.HTTP_DOWNLOAD_DISABLES = 0
        self.HTTP_DOWNLOAD_ENABLED_PORT = 1
        self.HTTP_DOWNLOAD_ENABLED_URL = 2


class PacketTypes:
    """
        Packet Types
        * Element RPC
        * Main Packets
        * Packet ID
    """

    def __init__(self) -> None:
        self.ELEMENT_RPC = 1
        self.MAIN_PACKETS = 2
        self.PACKET_ID = 3

class AseVersion(Enum):
    """
        Ase Queries Versions
        * 1.Y  => Normal
        * 1.Yn => For mta developers & other versions
    """
    v1_5 = "1.5"
    v1_5n = "1.5n"

    v1_6 = "1.6"
    v1_6n = "1.6n"


class BuildType(Enum):
    """
        MTA Server Build Types
    """
    CUSTOM = 1
    EXPERIMENTAL = 3
    UNSTABLE = 5
    UNTESTED = 7
    RELEASE = 9

class QueryTypes(Enum):
    """Local Server List Ase Query Types"""
    Full = b'x'
    Light = b'b'
    LightRelease = b'r'
    XFire = b'x'
    Version = b'v'

class PlayerDisconnectedTypes(Enum):
    NO_REASON = 0
    INVALID_PASSWORD = 1
    INVALID_NICKNAME = 2
    BANNED_SERIAL = 3
    BANNED_IP = 4
    BANNED_ACCOUNT = 5
    VERSION_MISMATCH = 6
    JOIN_FLOOD = 7
    INCORRECT_PASSWORD = 8
    DIFFERENT_BRANCH = 9
    BAD_VERSION = 10
    SERVER_NEWER = 11
    SERVER_OLDER = 12
    NICK_CLASH = 13
    ELEMENT_FAILURE = 14
    GENERAL_REFUSED = 15
    SERIAL_VERIFICATION = 16
    CONNECTION_DESYNC = 17
    BAN = 18
    KICK = 19
    CUSTOM = 20
    SHUTDOWN = 21


LOCAL_SERVER_LIST_ASE_PORT = 34219
MASTER_SERVER_LIST_URL = "http://updatesa.mtasa.com/sa/master/"
LOCAL_SERVER_LIST_ASE_MESSAGE = "MTA-SERVER"

# MTA port tester URL
PORT_TESTER_URL = "http://nightly.mtasa.com/ports/"

# Just For Debug
BITSTREAM_VERSION = 171


class ElementID(object):
    def __init__(self, __id: int) -> None:
        self._id = __id

    def getID(self) -> int:
        return self._id
