from IronicMTA.core.packet_handler.io import BitStream
from IronicMTA.core.packet_ids import PacketID, PacketPriority, PacketReliability


class Packet(object):
    """Packet Base"""

    def __init__(self) -> None:
        self.bitstream = BitStream()

    def build(self):
        """Get packet bytes"""
        return self.bitstream.get_bytes()

    def get_id(self) -> PacketID:
        """Get The Packet ID Will be Sent"""
        return PacketID.name

    def get_priority(self) -> PacketPriority:
        """Get The Packet Priority Will be Sent"""
        return PacketPriority.name

    def get_reliability(self) -> PacketReliability:
        """Get The Packet Reliability Will be Sent"""
        return PacketReliability.name
