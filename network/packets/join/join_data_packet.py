"""
    Join Data packet
"""

from network.packet_base import PacketBase
from limits import MAX_PLAYER_NICK_LENGTH, MAX_SERIAL_LENGTH

class Packet_PlayerJoinData(PacketBase):
    """Join Data Packet"""
    def __init__(self) -> None:
        super().__init__()
        self.net_version = None
        self.mta_version = None
        self.bitstream_version = None
        self.player_version = None
        self.optional_update = None
        self.game_version = None
        self.nickname = None
        self.password = None
        self.serial = None

    def read(self, data: bytes):
        self.bitstream.refresh(data)

        self.net_version = self.bitstream.read_uint16()
        self.mta_version = self.bitstream.read_uint16()
        self.bitstream_version = self.bitstream.read_uint16()
        self.player_version = self.bitstream.read_string()
        self.optional_update = self.bitstream.read_bit()
        self.game_version = self.bitstream.read_bit()
        self.nickname = self.bitstream.read_string_characters(MAX_PLAYER_NICK_LENGTH)
        self.password = self.bitstream.read_bytes(16)
        self.serial = self.bitstream.read_string_characters(MAX_SERIAL_LENGTH)

    def build(self):
        self.bitstream.reset()
        self.bitstream.write_ushort(self.net_version)
        self.bitstream.write_ushort(self.mta_version)
        self.bitstream.write_ushort(self.bitstream_version)
        self.bitstream.write_string(self.player_version)
        self.bitstream.write_bit(self.optional_update)
        self.bitstream.write_bytes(bytes(self.game_version))
        self.bitstream.write_string_without_len(self.nickname[:MAX_PLAYER_NICK_LENGTH])
        self.bitstream.write_bytes(bytearray(self.password))
        self.bitstream.write_string_without_len(self.serial[:MAX_SERIAL_LENGTH])

        return self.bitstream.get_bytes() #   :>
