"""
    Player Disconnected Packet
"""

from network.packet_base import Packet

class Packet_PlayerDisconnected(Packet):
    def __init__(self, data: bytearray) -> None:
        super().__init__()
        self.bitstream.refresh(data)

        self.disconnected_type = self.bitstream.read_bits(5)
        print(f"Disconencted Type: {self.disconnected_type}")

        self.reason = self.bitstream.read_string()
        print(f"Disconnected Reason: {self.reason}")