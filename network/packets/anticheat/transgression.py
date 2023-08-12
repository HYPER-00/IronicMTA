"""
    Anticheat checks Packet
"""

from ....core.packet_ids import PacketID, PacketPriority, PacketReliability
from ....network.packet_base import Packet

class Packet_AntiCheatTransgression(Packet):
    def __init__(self, data) -> None:
        super().__init__()
        self.bitstream.refresh(data)
        self._level = self.bitstream.read_uint32()
        self._message = self.bitstream.read_string()

        print("AntiCheat Message: ", self._message)

    def get_id(self) -> PacketID:
        return PacketID.PACKET_ID_PLAYER_TRANSGRESSION
    
    def get_priority(self) -> PacketPriority:
        return PacketPriority.HIGH
    
    def get_reliability(self) -> PacketReliability:
        return PacketReliability.RELIABLE
