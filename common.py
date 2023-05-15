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
        self.ELEMENT_RPC  = 1
        self.MAIN_PACKETS = 2
        self.PACKET_ID    = 3
