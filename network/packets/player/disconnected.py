"""
    Player Disconnected Packet
"""
from core.packet_ids import PacketID, PacketPriority, PacketReliability
from network.packet_base import Packet
from logger import Logger
from common import PlayerDisconnectedTypes

class Packet_PlayerDisconnected(Packet):
    def __init__(self, data: bytearray, logger: Logger = None) -> None:
        super().__init__()
        self.bitstream.refresh(data)

        self.disconnected_type = self.bitstream.read_uint32()
        print(f"Disconencted Type: {self.disconnected_type}")

        self.reason = self.bitstream.read_string()
        print(f"Disconencted Reason: '{self.reason}'")


    def get_id(self) -> PacketID:
        return PacketID.PACKET_ID_SERVER_DISCONNECTED

    def get_priority(self) -> PacketPriority:
        return PacketPriority.HIGH
    
    def get_reliability(self) -> PacketReliability:
        return PacketReliability.RELIABLE
