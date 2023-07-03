from core.packet_handler.io import BitStream


class PacketBase(object):
    """Packet base"""

    def __init__(self) -> None:
        self.bitstream = BitStream()

    def build(self):
        return self.bitstream.get_bytes()
