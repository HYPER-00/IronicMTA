from ctypes import c_char_p, string_at
from ...network.packets import *
from ...core.packet_ids import PacketID
from ...common import BITSTREAM_VERSION


class PacketHandler(object):
    def __init__(self, server) -> None:
        self._server = server
        self._network = server.getNetwork()
        self._logger = server.getLogger()
        self._packet = None
        self._packet_index = -1

    def onrecive(self, packet: int, player: int, packet_content: c_char_p, packet_index: int):
        if self._packet_index != packet_index:
            self._packet_index = packet_index
            if packet != 0 and player != 0:
                self._server.event.call(
                    "onReceivePacket", self._server, packet, player, packet_content)

                self._logger.debug(f"Received {PacketID(packet)}")
                print('string: ', string_at(packet_content))
                # print('packet_content: ', packet_content)   
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
                        bitstream_version=1,  # TODO
                        data=self._packet.build(),
                        priority=self._packet.get_priority(),
                        reliability=self._packet.get_reliability()
                    )
                    return True
        return False
