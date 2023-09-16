"""
    Join Mod Name packet
"""

from IronicMTA.network.packet_base import Packet


class Packet_PlayerConnectComplete(Packet):
    def __init__(self, net_version: int, message: str) -> None:
        self._netversion = net_version
        self._message = message

    def build(self):
        self.bitstream.write_string(self._message)
        self.bitstream.write_string(str(self._netversion))

        return self.bitstream.get_bytes()
