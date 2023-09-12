"""
    IronicMTA Client
"""

from .core import NetworkWrapper
from .core.packet_ids import PacketID
from .network.packet_base import Packet


class Client(object):
    def __init__(self, binary_address: int, bitstream_version: int, server):
        self._network: NetworkWrapper = server.get_network()
        self._bin_address = binary_address
        self._bitstream_version = bitstream_version
        self._serial = None

    def send(self, packet: Packet) -> bool:
        return self._network.send(
            self._bin_address,
            packet.get_id(),
            self._bitstream_version,
            packet.build(),
            packet.get_reliability(),
            packet.get_priority(),
        )
