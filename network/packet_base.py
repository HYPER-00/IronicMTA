from core.packet_handler.io import builder, reader
from core.packet_handler import io

class PacketBase(object):
    """Packet base"""
    def __init__(self) -> None:
        self.bitstream = io.BitStream()

    def build(self):
        return self.bitstream.get_bytes()
