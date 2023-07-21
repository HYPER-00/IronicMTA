"""
    IronicMTA Client
"""

from core import NetworkWrapper
from core.packet_ids import PacketID
from core.packet_ids.priority import PacketPriority
from core.packet_ids.reliability import PacketReliability
from client_state import ConnectionState

from typing import Literal

from ctypes import (c_ushort)

class Client:
    def __init__(self, server, addr: int, bitstream_version: int) -> None:
        self._netwrapper = NetworkWrapper(server)
        self._addr = addr
        self._bitstream_version = bitstream_version

        self._serial = None
        self._extra = None
        self._version = None
        self._connected = True
        self._ip = None
        self._connection_state = None
        self._ping = None

        self._conn_states = ConnectionState()

    def sendPacket(
        self,
        packet: PacketID,
        data: bytearray,
        priority: int = PacketPriority().MEDIUM,
        reliability: int = PacketReliability().UNRELIABLE
    ):
        """Send packet to the client from net wrapper"""
        if self._packet_access():
            self._netwrapper.send(
                playerbin_addr=self._addr,
                bitstream_version=self._bitstream_version,
                packet_id=packet,
                content=data,
                reliability=reliability,
                priority=priority,
            )
            self._handle_state(packet)

    def _packet_access(self) -> Literal[True] | None:
        return (self._connected and self._connection_state == self._conn_states.joined)

    def _handle_state(self, packet: int):
        """Change client connection state"""
        if packet in [
            self._conn_states.disconnected,
            self._conn_states.joined,
            self._conn_states.mod_name_sent,
            self._conn_states.server_version_sent,
            self._conn_states.timout,
            self._conn_states.quit,
        ]:
            self._connection_state = packet

    def quit(self):
        """Exit client from connection"""
        self._connection_state = self._conn_states.quit

    def resetConnectionState(self):
        """Reset client connection state to disconnected"""
        self._connection_state = self._conn_states.disconnected

    def setVersion(self, version: int):
        """Set client bitstream version"""
        if self._connected:
            self._netwrapper.setNetworkVersion(self._addr, version)

    def resendModPackets(self):
        """Resend client mod packets"""
        if self._connected:
            self._netwrapper.resendModPackets(self._addr)

    def resendPlayerACInfo(self):
        """Resend player anticheat info"""
        if self._connected:
            self._netwrapper.resendPlayerACInfo(self._addr)

    def loadSerial(self):
        """Get client serial, version and extra data"""
        if self._connected:
            self._netwrapper.getClientSerialAndVersion(self._addr, self._serial, self._extra, self._version)
