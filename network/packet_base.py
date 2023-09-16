from typing import Union, Any

from IronicMTA.core.packet_handler.io import BitStream
from IronicMTA.core.packet_ids import PacketID, PacketPriority, PacketReliability


class Packet(object):
    """Packet Base"""

    def __init__(self) -> None:
        self.bitstream = BitStream()

    def build(self) -> Union[bytes, bytearray, Any]:
        """Get packet bytes"""

    def get_id(self) -> Union[PacketID, Any]:
        """Get The Packet ID Will be Sent"""

    def get_priority(self) -> Union[PacketPriority, Any]:
        """Get The Packet Priority Will be Sent"""

    def get_reliability(self) -> Union[PacketReliability, Any]:
        """Get The Packet Reliability Will be Sent"""
