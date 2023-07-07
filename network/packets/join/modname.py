from core.packet_ids import PacketID, PacketPriority, PacketReliability
from network.packet_base import Packet

class Packet_PlayerJoinModName(Packet):
    def __init__(self, bitstream_version) -> None:
        super().__init__()
        self.bitstream.write_ushort(bitstream_version)
        self.bitstream.write_string("deathmatch")

    def get_id(self) -> PacketID:
        return PacketID.PACKET_ID_MOD_NAME
    
    def get_priority(self) -> PacketPriority:
        return PacketPriority.HIGH
    
    def get_reliability(self) -> PacketReliability:
        return PacketReliability.RELIABLE

    def build(self):
        return self.bitstream.get_bytes()

