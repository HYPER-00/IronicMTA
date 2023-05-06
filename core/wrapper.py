"""
    net.dll wrapper
"""

import sys
import os

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))
print(os.path.join(*_dir))

import os
from platform import architecture
from typing import Literal
from ctypes import cdll, c_char, c_char_p, c_ushort, c_uint, c_uint16, c_ulong, c_bool, CFUNCTYPE

def initcallback():
    print("Calllllllbackkkkkkkkkkk")
    return 1

class NetWrapper:
    def __init__(self, server):
        self._server = server
        self._settings_manager = server.settings_manager
        if not self._settings_manager.isloaded:
            self._settings_manager.load()
        self._settings = self._settings_manager.get()

        self._localdir = __file__.split('\\')[:-1]
        if self._localdir[0].endswith(':'): self._localdir[0] += '\\'
        self._localdir = os.path.join(*self._localdir)

        self._netdll_path = os.path.join(self._localdir, "lib\\release\\net.dll")
        self._architecture = "x" + architecture()[0][0:2]
        self.wrapper_path = os.path.join(self._localdir, f"lib\\wrapper\\{self._architecture}\\wrapper.dll")
        self._dll = cdll.LoadLibrary(self.wrapper_path)

    def init(self) -> Literal[True] | None:
        """
            Init net wrapper for recv/send packet
            `Returns` server id
        """
        if self._dll.initNetWrapper:
            _func = self._dll.initNetWrapper
            _func.restype = c_ushort
            _c_callback_t = CFUNCTYPE(c_char, c_ulong, c_char, c_ulong, c_bool, c_uint)
            _func.argtypes = [c_char_p, c_char_p, c_char_p, c_ushort, c_uint, c_char_p,
                                                _c_callback_t]
            self._c_netdll_path = c_char_p(self._b(self._netdll_path))
            self._c_idfile = c_char_p(self._b(os.path.join(self._localdir, "id")))
            self._c_ip = c_char_p(b"127.0.0.1")
            self._c_port = c_ushort(self._settings_manager.getServerAddr()[1] + 123)
            self._c_player_count = c_uint(self._server.getPlayerCount())
            self._c_servername = c_char_p(b"Default PyMTA Server")

            _result = _func(
                self._c_netdll_path,
                self._c_idfile,
                self._c_ip,
                self._c_port,
                self._c_player_count,
                self._c_servername,
                _c_callback_t(initcallback)
            )
            if _result < 0:
                return print("ERROR Unable to init net wrapper")
            print(f"Net Wrapper Started with {_result}")
            return _result

    def start(self, __id: c_uint16) -> Literal[True] | None:
        if self._dll.startNetWrapper:
            _func_prototype = CFUNCTYPE(None, c_uint16)
            _func = _func_prototype(('startNetWrapper', self._dll))

            _func(__id)

        return True

    def _b(self, __str: str = "", encoding: str = "utf-8") -> bytes:
        return bytes(__str, encoding=encoding)
