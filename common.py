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


LOCAL_SERVER_LIST_ASE_PORT = 34219
MASTER_SERVER_LIST_URL = "http://updatesa.mtasa.com/sa/master/"
LOCAL_SERVER_LIST_ASE_MESSAGE = "MTA-SERVER"

# MTA port tester URL
PORT_TESTER_URL = "http://nightly.mtasa.com/ports/"

MAX_ASE_GAME_TYPE_LENGTH = 200
MAX_ASE_MAP_NAME_LENGTH = 200
MAX_RULE_KEY_LENGTH = 200
MAX_RULE_VALUE_LENGTH = 200

# Just For Debug
BITSTREAM_VERSION = 171


class ElementID(object):
    def __init__(self, __id: int) -> None:
        self._id = __id

    def getID(self) -> int:
        return self._id
