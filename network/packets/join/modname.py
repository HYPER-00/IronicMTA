from network.packet_base import Packet

class Packet_PlayerJoinModName(Packet):
    def __init__(self, bitstream_version) -> None:
        super().__init__()
        self.bitstream.write_ushort(bitstream_version)
        self.bitstream.write_string("deathmatch")

    def build(self):
        return self.bitstream.get_bytes()

