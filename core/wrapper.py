"""
    MTASA net.dll wrapper
"""

import os
from threading import Thread
import sys
from platform import architecture
from typing import Literal, Any
from ctypes import (
    cdll,
    c_char_p,
    c_ushort,
    c_short,
    c_int,
    c_uint,
    c_ulong,
    c_bool,
    CFUNCTYPE,
    windll,
    WinError,
    POINTER,
    c_ubyte,
)
import colorama

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'): _dir[0] += '\\'
_basedir = os.path.join(*_dir)

from core.packet_ids import PacketID, PacketPriority, PacketReliability
from errors import (
    NetWrapperInitError,
    NetWrapperInterfaceError,
    NetWrapperLoadingError,
    NetWrapperStartError,
    NetWrapperVersionError
)

from core.packet_handler import PacketHandler

T = Literal[True] | None

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

class WrapperCodes:
    """
        Wrapper Codes for net wrapper initialization
        * Sucess
        * Loading Error
        * Version Error
        * Interface Error
        * Initialization Error
        * Start Error
    """
    def __init__(self):
        self.sucess = 0
        self.loading_error = -1001
        self.version_error = -1003
        self.interface_error = -1004
        self.init_error = -1005
        self.start_error = -1006

version_type = MTAVersionType()

MTA_DM_SERVER_NET_MODULE_VERSION = 0x0AB
MTA_DM_SERVER_VERSION_TYPE = version_type.REALEASE

class NetWrapper(object):
    """
        MTA net.dll wrapper (closed source)
    """
    def __init__(self, server) -> None:
        self._port = server.getAddress()[1]
        self._server = server

        self._codes = WrapperCodes()
        self.__id = c_ushort(0)

        self._listening_thread = Thread(target=self._listener_thread_handler,
                                        args=())

        if MTA_DM_SERVER_VERSION_TYPE != version_type.REALEASE:
            _log_err("SafeMTA Server does not support network debug dlls")
            sys.exit(-1)

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

    def init(self) -> T:
        """
            Init net wrapper for sending packet
            `Returns` server id
        """
        if self._wrapperdll.Setup:
            _func = self._wrapperdll.Setup
            _func.restype = c_short
            _func.argtypes = [c_char_p, c_char_p, c_char_p, c_ushort, c_uint, c_char_p, POINTER(c_ulong)]
            _c_netdll_path = c_char_p(self._b(self.netpath))
            _c_idfile = c_char_p(self._b(self._server.getServerFileIDPath()))
            _c_ip = c_char_p(b"0.0.0.0")
            _c_port = c_ushort(self._port)  
            _c_player_count = c_uint(self._server.getPlayerCount() + 1)
            _c_servername = c_char_p(self._b(self._server.getName()))

            _result = _func(
                _c_idfile,
                _c_netdll_path,
                _c_ip,
                _c_port,
                _c_player_count,
                _c_servername, c_ulong(0x09)
            )

            if _result < 0:
                return _log_err(f"ERROR Unable to init net wrapper. ({_result})")
            self._initialized = True
            self.__id = c_ushort(_result)
            return True

    def startListening(self):
        self._listening_thread.start()
        return True
        
    def _listener_thread_handler(self):
        if self._wrapperdll.StartListening:
            packet_handler = PacketHandler(self._server)
            while True:
                try:
                    FunctionPointer = CFUNCTYPE(c_ushort, c_ubyte, c_ulong, c_char_p)
                    callback_func = FunctionPointer(packet_handler.onrecive)
                    self._wrapperdll.StartListening(self.__id, callback_func)
                except Exception as err:
                    print(f"An ERROR Occured: {err}")
        else:
            _log_err("StartListening() Function Not Found")

    def destroy(self) -> T:
        """Destroy net wrapper"""
        self._wrapperdll.Destroy(self.__id)
        return True

    def start(self) -> T:
        """
            Start net wrapper with id
        """
        if not self._initialized:
            raise NetWrapperInitError("net wrapper is not initialized. try to init()")

        if self._wrapperdll.Start:
            try:
                self._wrapperdll.Start(self.__id)
            except Exception:
                _log_err("Coudldn't Start Net Wrapper")
                _log_err(WinError(kernel32.GetLastError()).strerror)
        return True

    def stop(self) -> T:
        """Stop net wrapper"""
        self._wrapperdll.Stop(self.__id)
        return True

    def send(
        self,
        player_binaddr: int,
        packet_id: int,
        bitstream_version: int,
        payload: bytes,
        reliability: PacketReliability = PacketReliability.RELIABLE,
        priority: PacketPriority = PacketPriority.HIGH,
    ) -> T:
        _func = self._wrapperdll.Send
        #                   id      player  packetId  BS Version     data dataSize Priority  Reliability
        _func.argtypes = [c_ushort, c_ulong, c_uint, c_ushort, c_char_p, c_ulong, c_ubyte, c_ubyte]
        _func(
            self.__id,
            c_ulong(player_binaddr),
            c_uint(packet_id),
            c_ushort(bitstream_version),
            payload,
            c_ulong(len(payload)),
            c_ubyte(priority),
            c_ubyte(reliability),
        )
        return True

    def setNetworkVersion(self, addr: int, version: int) -> T:
        """Set client bitstream version"""
        self._wrapperdll.SetNetworkVersion(self.__id, addr, version)

    def getClientData(self, addr: int, serial: str, extra: str, version: str) -> Any:
        """Get client serial and version"""
        return self._wrapperdll.GetClientData(
            self.__id,
            c_ulong(addr),
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
    ) -> T:
        """Set Anticheat checks"""
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

    def getModPackets(self, addr: int) -> T:
        """Resend mod packets"""
        self._wrapperdll.GetModPackets(self.__id, c_ulong(addr))
        return True

    def getAntiCheatInfo(self, addr: int) -> T:
        """Resend player anticheat info"""
        self._wrapperdll.GetAntiCheatInfo(self.__id, c_ulong(addr))

    def _b(self, __str: str = "", encoding: str = "utf-8") -> bytes:
        return bytes(__str, encoding=encoding)
