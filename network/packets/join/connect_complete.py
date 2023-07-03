"""
    Join Mod Name packet
"""

from network.packet_base import PacketBase

class Packet_PlayerConnectComplete(PacketBase):
    def __init__(self, net_version: int, message: str) -> None:
        self._netversion = net_version
        self._message = message

    def build(self):
        self.bitstream.write_string(self._message)
        self.bitstream.write_string(self._netversion)

        return self.bitstream.get_bytes()
