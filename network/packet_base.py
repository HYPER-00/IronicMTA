from ..core.packet_handler.io import BitStream
from ..core.packet_ids import PacketID, PacketPriority, PacketReliability


class Packet(object):
    """Packet Base"""

    def __init__(self) -> None:
        self.bitstream = BitStream()

    def build(self):
        return self.bitstream.get_bytes()

    def get_id(self) -> PacketID:
        """
            Get The Packet ID Will be Sent
        """
        ...

    def get_priority(self) -> PacketPriority:
        """
            Get The Packet Priority Will be Sent
        """
        ...

    def get_reliability(self) -> PacketReliability:
        """
            Get The Packet Reliability Will be Sent
        """
        ...
