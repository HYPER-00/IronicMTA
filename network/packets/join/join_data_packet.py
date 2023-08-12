"""
    Join Data packet
"""

from ....core.packet_ids import PacketID, PacketPriority, PacketReliability
from ....network.packet_base import Packet
from ....limits import MAX_PLAYER_NICK_LENGTH, MAX_SERIAL_LENGTH


class Packet_PlayerJoinData(Packet):
    """Join Data Packet"""

    def __init__(self, data: bytearray) -> None:
        super().__init__()
        self.bitstream.refresh(data)
        print(f"Data: {bytes(data)}")
        self.net_version = self.bitstream.read_ushort()
        print(f"NetVersion: {self.net_version}")
        self.mta_version = self.bitstream.read_ushort()
        print(f"MTAVersion: {self.mta_version}")
        self.bitstream_version = self.bitstream.read_ushort()
        print(f"BitStream Version: {self.bitstream_version}")
        self.player_version = self.bitstream.read_string()
        print(f"Player Version: {self.player_version}")

        self.optional_update = self.bitstream.read_bit()
        print(f"Optional Update: {self.optional_update}")
        self.game_version = self.bitstream.read_byte()
        print(f"Game Version: {self.game_version}")
        self.nickname = self.bitstream.read_string_characters(
            MAX_PLAYER_NICK_LENGTH)
        print(f"Nick Version: {self.nickname}")
        self.password = self.bitstream.read_bytes(16)
        self.serial = self.bitstream.read_string_characters(MAX_SERIAL_LENGTH)


    def get_id(self) -> PacketID:
        return PacketID.PACKET_ID_PLAYER_JOINDATA
    
    def get_priority(self) -> PacketPriority:
        return PacketPriority.HIGH
    
    def get_reliability(self) -> PacketReliability:
        return PacketReliability.RELIABLE_SEQUENCED

    def build(self):
        return self.bitstream.get_bytes()
