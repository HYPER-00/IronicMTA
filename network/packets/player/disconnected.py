"""
    Player Disconnected Packet
"""

from typing import Optional
from IronicMTA.core.packet_ids import PacketID, PacketPriority, PacketReliability
from IronicMTA.network.packet_base import Packet
from IronicMTA.logger import Logger
from IronicMTA.common import PlayerDisconnectedTypes


class Packet_PlayerDisconnected(Packet):
    def __init__(self, data: bytearray, logger: Optional[Logger] = None) -> None:
        super().__init__()
        self.bitstream.refresh(data)

        self.disconnected_type = self.bitstream.read_uint32()
        self.reason = self.bitstream.read_string()

        if logger:
            logger.log(
                f"Disconencted Type: {PlayerDisconnectedTypes(self.disconnected_type)}"
            )
            logger.log(f"Disconencted Reason: '{self.reason}'")

    def get_id(self) -> PacketID:
        return PacketID.PACKET_ID_SERVER_DISCONNECTED

    def get_priority(self) -> PacketPriority:
        return PacketPriority.HIGH

    def get_reliability(self) -> PacketReliability:
        return PacketReliability.RELIABLE
