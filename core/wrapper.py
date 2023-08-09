"""
    MTASA net.dll wrapper
"""

import os
from threading import Thread
import sys
from platform import architecture
from typing import Literal, Any, Tuple
from ctypes import (
    cdll,
    c_char_p,
    c_ushort,
    c_short,
    c_int,
    c_float,
    c_uint,
    c_ulong,
    c_bool,
    c_longlong,
    windll,
    Structure,
    WinError,
    POINTER,
    c_ubyte,
)
import colorama

from core.packet_ids import PacketID, PacketPriority, PacketReliability
from errors import NetworkWrapperInitError, NetworkWrapperError
from core.packet_handler import PacketHandler


kernel32 = windll.kernel32

colorama.init(autoreset=True)


def _log_err(err: str) -> None:
    print(f"{colorama.Fore.RED}[Net-Wrapper ERROR] {err}.")


class MTAVersionType:
    """
        MTA Version types
        * Custom
        * Experimental
        * Unstable
        * Untested
        * Release
    """

    def __init__(self):
        self.CUSTOM = 0x01
        self.EXPERIMENTAL = 0x03
        self.UNSTABLE = 0x05
        self.UNTESTED = 0x07
        self.REALEASE = 0x09


class ThreadCPUTimes(Structure):
    _fields_ = [("uiProcessorNumber", c_uint),
                ("fUserPercent", c_float),
                ("fKernelPercent", c_float),
                ("fTotalCPUPercent", c_float),
                ("fUserPercentAvg", c_float),
                ("fKernelPercentAvg", c_float),
                ("fTotalCPUPercentAvg", c_float)]


class BandwidthStatistics(Structure):
    _fields_ = [("llOutgoingUDPByteCount", c_longlong),
                ("llIncomingUDPByteCount", c_longlong),
                ("llIncomingUDPByteCountBlocked", c_longlong),
                ("llOutgoingUDPPacketCount", c_longlong),
                ("llIncomingUDPPacketCount", c_longlong),
                ("llIncomingUDPPacketCountBlocked", c_longlong),
                ("llOutgoingUDPByteResentCount", c_longlong),
                ("llOutgoingUDPMessageResentCount", c_longlong),
                ("threadCPUTimes", ThreadCPUTimes)]


class PyPacket(Structure):
    _fields_ = [("uiPacketIndex", c_uint),
                ("uiPacketID", c_uint),
                ("ulPlayerBinaryAddress", c_ulong),
                ("szPacketBuffer", c_char_p)]


class SPacketStat(Structure):
    _fields_ = [("iCount", c_int),
                ("iTotalBytes", c_int),
                ("totalTime", c_ulong)]


class PlayerAddress(Structure):
    _fields_ = [("szIP", c_char_p),
                ("usPort", c_ushort)]

version_type = MTAVersionType()
MTA_DM_SERVER_NET_MODULE_VERSION = 0x0AB
MTA_DM_SERVER_VERSION_TYPE = version_type.REALEASE


class NetworkWrapper(object):
    """MTA:SA net.dll wrapper

    Args:
        server (Server): IronicMTA Server
    """

    def __init__(self, server) -> None:
        self._ip, self._port = server.getAddress()
        self._server = server

        self.__id = c_ushort(0)

        if MTA_DM_SERVER_VERSION_TYPE != version_type.REALEASE:
            _log_err("IronicMTA Server does not support network debug dlls")
            sys.exit(-1)

        _dir = __file__.split('\\')[:-2]
        if _dir[0].endswith(':'):
            _dir[0] += '\\'
        _basedir = os.path.join(*_dir)

        self.netpath = f"{_basedir}\\core\\lib\\{'release' if MTA_DM_SERVER_VERSION_TYPE == version_type.REALEASE else 'debug'}\\net{'' if MTA_DM_SERVER_VERSION_TYPE == version_type.REALEASE else '_d'}.dll"
        self.wrapperpath = f"{_basedir}\\core\\lib\\wrapper\\wrapper.x{architecture()[0][:2]}.dll"

        self._initialized = False

        try:
            self._netlib = cdll.LoadLibrary(self.netpath)
        except OSError as err:
            _log_err("Cannot Open network dll:")
            _log_err(err)

        iscompatible = self._netlib.CheckCompatibility(
            MTA_DM_SERVER_NET_MODULE_VERSION, c_ulong(version_type.UNSTABLE))

        if not self._netlib.CheckCompatibility and iscompatible:
            _log_err("""
            Network module not compatible!
            If this is a custom build, try to:
                1. Update net.dll
                3. Check MTASA_VERSION_TYPE
            """)
            sys.exit(-1)

        try:
            self._wrapperdll = cdll.LoadLibrary(self.wrapperpath)
        except OSError as err:
            _log_err("Cannot open wrapper dll:")
            _log_err(err)

    def init(self) -> Literal[True] | None:
        """Init Network wrapper

        Returns:
            Literal[True] | None: True If the server has been started successfuly
        """
        if self._wrapperdll.Setup:
            _func = self._wrapperdll.Setup
            _func.restype = c_short
            _func.argtypes = [c_char_p, c_char_p, c_char_p,
                              c_ushort, c_uint, c_char_p, POINTER(c_ulong)]

            _result = _func(
                c_char_p(self._b(self._server.getServerFileIDPath())),
                c_char_p(self._b(self.netpath)),
                c_char_p(bytes(self._ip, encoding="utf-8")),
                c_ushort(self._port),
                c_uint(self._server.getPlayerCount() + 1),
                c_char_p(self._b(self._server.getName())),
                c_ulong(self._server.getBuildType().value)
            )

            if _result < 0:
                return _log_err(f"ERROR Unable to init net wrapper. ({_result})")
            self._initialized = True
            self.__id = c_ushort(_result)
            return True

    def _thread_listener(self):
        _packet_handler = PacketHandler(self._server)
        _func = self._wrapperdll.GetLastPackets
        _func.argtypes = [c_ushort]
        _func.restype = PyPacket
        if _func:
            while True:
                try:
                    _packet = _func(self.__id)
                except Exception as err:
                    _log_err(WinError(kernel32.GetLastError()).strerror)

                _packet_handler.onrecive(_packet.uiPacketID, _packet.ulPlayerBinaryAddress,
                                         _packet.szPacketBuffer, _packet.uiPacketIndex)
        else:
            _log_err("Couldn't find GetLastPackets function")

    def startListening(self) -> Literal[True] | None:
        """Start Server packet listening

        Returns:
            Literal[True] | None: True if all succeded
        """
        Thread(target=self._thread_listener, args=(), name="Packet Receiver").start()
        return True

    def destroy(self) -> Literal[True] | None:
        """Destroy network

        Returns:
            Literal[True] | None: True if network has been destroyed successfuly
        """
        self._wrapperdll.Destroy(self.__id)
        return True

    def start(self) -> Literal[True] | None:
        """Start Network Wrapper

        Raises:
            NetWrapperInitError: If network wrapper not initialized

        Returns:
            Literal[True] | None: True if network has been started successfuly
        """
        if not self._initialized:
            raise NetworkWrapperInitError(
                "Network wrapper is not initialized. try to init()")

        if self._wrapperdll.Start:
            try:
                self._wrapperdll.Start(self.__id)
            except Exception:
                _log_err("Coudldn't Start Net Wrapper")
                _log_err(WinError(kernel32.GetLastError()).strerror)
        return True

    def stop(self) -> Literal[True] | None:
        """Stop network wrapper

        Returns:
            Literal[True] | None: True if network has benn stoped successfuly
        """
        self._wrapperdll.Stop(self.__id)
        return True

    def send(
        self,
        player_binaddr: int,
        packet_id: int,
        bitstream_version: int,
        data: bytes,
        reliability: PacketReliability = PacketReliability.RELIABLE,
        priority: PacketPriority = PacketPriority.HIGH,
    ) -> Literal[True] | None:
        """Send Client packet

        Args:
            player_binaddr (int): Client Player Binary Address
            packet_id (int): Packet ID
            bitstream_version (int): BitStream Version
            data (bytes): Sequence of bytes represents the data to send
            reliability (PacketReliability, optional): Packet reliability. Defaults to PacketReliability.RELIABLE.
            priority (PacketPriority, optional): Packet Priority. Defaults to PacketPriority.HIGH.

        Returns:
            Literal[True] | None: if packet has been sent successfuly (without errors)
        """
        _func = self._wrapperdll.Send
        _func.argtypes = [c_ushort, c_ulong, c_uint,
                          c_ushort, c_char_p, c_ulong, c_ubyte, c_ubyte]
        _func(
            self.__id,
            c_ulong(player_binaddr),
            c_uint(packet_id),
            c_ushort(bitstream_version),
            data,
            c_ulong(len(data)),
            c_ubyte(priority),
            c_ubyte(reliability),
        )
        return True
    
    def isValidSocket(self, player_binaddr: int) -> bool:
        """Check if socket is valid

        Args:
            player_binaddr (int): The Client Player Binary Address

        Returns:
            bool: True if is valid socket else False
        """
        _func = self._wrapperdll.IsValidSocket
        _func.argtypes = [c_ushort, c_ulong]
        _func.restype = c_bool
        return _func(self.__id, c_ulong(player_binaddr))

    def setClientBitStreamVersion(self, client_binaddr: int, version: int) -> Literal[True] | None:
        """Set BitStream Version

        Args:
            client_binaddr (int): Client player binary address
            version (int): bitstream version

        Returns:
            Literal[True] | None: _description_
        """
        self._wrapperdll.SetClientBitStreamVersion(self.__id, client_binaddr, version)
        
    def getPlayerAddress(self, player_binaddr: int) -> Tuple[str, int]:
        """Get Player Address (Ip, Port)

        Args:
            player_binaddr (int): Client player binary Address

        Raises:
            NetworkWrapperError: Invalid Client player binary address

        Returns:
            Tuple[str, int]: Tuple of Client Player address (IP, Port)
        """  
        _func = self._wrapperdll.GetPlayerAddress
        _func.argtypes = [c_ushort, c_ulong]
        _func.restype = PlayerAddress
        _address = _func(self.__id, c_ulong(player_binaddr))
        if _address.usPort == 0:
            raise NetworkWrapperError("Invalid Player Binary Address")
        return _address.strIP, _address.usPort

    def getClientData(self, player_binaddr: int, serial: str, extra: str, version: str) -> Any:
        """Get Client Data (Serial, Extra, Version)

        Args:
            player_binaddr (int): Client player binary address
            serial (str): Serial variable to store-in serial
            extra (str): Extra Variable to store-in extra
            version (str): Version Variable to store-in version

        Returns:
            Any
        """
        return self._wrapperdll.GetClientData(
            self.__id,
            c_ulong(player_binaddr),
            c_char_p(self._b(serial)),
            c_char_p(self._b(extra)),
            c_char_p(self._b(version)),
        )

    def setAntiCheatChecks(
        self,
        disable_combo_ac_map: str,
        disable_ac_map: str,
        enable_sd_map: str,
        enable_client_checks: int,
        hide_ac: bool,
        img_mods: str,
    ) -> Literal[True] | None:
        """Set anticheat Checks/Configurations

        Args:
            disable_combo_ac_map (str): combo ac map
            disable_ac_map (str): ac map
            enable_sd_map (str): sd map
            enable_client_checks (int): client checks
            hide_ac (bool): Hide anticheat
            img_mods (str): img mods

        Returns:
            Literal[True] | None: True if anticheat settings applied successfuly
        """
        self._wrapperdll.SetAntiCheatChecks(
            self.__id,
            c_char_p(disable_combo_ac_map),
            c_char_p(disable_ac_map),
            c_char_p(enable_sd_map),
            c_int(enable_client_checks),
            c_bool(hide_ac),
            c_char_p(img_mods),
        )
        return True

    def getModPackets(self, player_binaddr: int) -> Literal[True] | None:
        """Get Mod packets

        Args:
            addr (int): Client player binary address

        Returns:
            Literal[True] | None: True if mod packets has been resent
        """
        self._wrapperdll.GetModPackets(self.__id, c_ulong(player_binaddr))
        return True

    def resendAntiCheatInfo(self, player_binaddr: int) -> Literal[True] | None:
        """Resend anticheat info to specefic player

        Args:
            player_binaddr (int): Client player binary address

        Returns:
            Literal[True] | None: _description_
        """
        self._wrapperdll.GetAntiCheatInfo(self.__id, c_ulong(player_binaddr))

    def getNetRoute(self) -> bytes:
        """Get Network Reoute

        Returns:
            bytes: Network route
        """
        _func = self._wrapperdll.GetNetRoute
        if self._server.isRunning():
            if _func:
                _func.argtypes = [c_ushort]
                _func.restype = c_char_p
                return _func(self.__id)
        return False

    def getBandwidthStatistics(self) -> BandwidthStatistics:
        """Get Bandwidth statistics

        Returns:
            BandwidthStatistics: Bandwidth statistics
        """
        _func = self._wrapperdll.GetBandwidthStatistics
        if _func:
            if self._server.isRunning():
                _func.argtypes = [c_ushort]
                _func.restype = BandwidthStatistics
                return _func(self.__id)
        return False

    def getPacketStat(self) -> SPacketStat:
        """Get Packets stats

        Returns:
            SPacketStat: Packets stats
        """
        _func = self._wrapperdll.GetPacketStat
        if _func:
            if self._server.isRunning():
                _func.argtypes = [c_ushort]
                _func.restype = SPacketStat
                return _func(self.__id)
        return False

    def getPingStatus(self) -> bytes:
        """Get Ping status

        Returns:
            bytes: Ping status
        """
        _func = self._wrapperdll.GetPingStatus
        if _func:
            if self._server.isRunning():
                _func.argtypes = [c_ushort]
                _func.restype = c_char_p
                return _func(self.__id)
        return False

    def _b(self, __str: str = "", encoding: str = "utf-8") -> bytes:
        return bytes(__str, encoding=encoding)
