"""
    Join complete packet
"""
from network.packet_base import PacketBase

class JoinCompletePacket(PacketBase):
    def __init__(self, message: str, version: str) -> None:
        super().__init__()
        self._message = message
        self._version = version

    def build(self):
        self.bitstream.write_string(self._message)
        self.bitstream.write_string(self._version)
        content = self.bitstream.get_bytes()
        self.bitstream.reset()
        return content
