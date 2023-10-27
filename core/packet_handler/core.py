"""Packet Handler Core"""
from typing import Any, Tuple
from IronicMTA.network.packets import Packet_PlayerJoinModName
from IronicMTA.core.packet_ids import PacketID
from IronicMTA.common import BITSTREAM_VERSION


class PacketHandler(object):
    """Packet Handler

    Args:
    -----
        server (Server): IronicMTA server
    """

    def __init__(self, server) -> None:
        self._server = server
        self._network = server.get_network()
        self._logger = server.get_logger()
        self._packet: Any
        self._packet_index = -1

    def onrecive(
        self, packet: int, player: int, packet_index: int, packet_content: Tuple[Any]
    ) -> bool:
        """On Receive Packet

        Args:
        -----
            packet (int): Packet id
            player (int): Player binary address
            packet_index (int): Packet index from all packets

        Returns:
        --------
            bool: True if the packet was handled successfuly
        """
        if self._packet_index != packet_index:
            self._packet_index = packet_index
            if packet != 0 and player != 0:
                self._server.event.call(
                    "onReceivePacket", self._server, packet, player, bytes()
                )

                self._logger.debug(f"Received {PacketID(packet)}")
                print("====================\n")

                if packet == PacketID.PACKET_ID_PLAYER_JOIN.value:
                    self._packet = Packet_PlayerJoinModName(BITSTREAM_VERSION)

                elif packet == PacketID.PACKET_ID_SERVER_DISCONNECTED.value:
                    # self._packet = Packet_PlayerDisconnected(packet_content)
                    ...

                elif packet == PacketID.PACKET_ID_PLAYER_TRANSGRESSION.value:
                    # self._packet = Packet_AntiCheatTransgression(packet_content)
                    ...

                elif packet == PacketID.PACKET_ID_PLAYER_JOINDATA.value:
                    # self._packet = Packet_PlayerJoinData(packet_content)
                    ...

                else:
                    return False
                if self._packet:
                    self._network.send(
                        player_binaddr=player,
                        packet_id=self._packet.get_id().value,
                        bitstream_version=BITSTREAM_VERSION,
                        data=self._packet.build(),
                        priority=self._packet.get_priority(),
                        reliability=self._packet.get_reliability(),
                    )
                    return True
        return False
