from typing import Literal
from threading import Thread

from IronicMTA.brodcast.local_announcer import LocalServerListAnnouncer
from IronicMTA.brodcast.local_ase import LocalServerListASE
from IronicMTA.brodcast.master_serverlist import MasterServerListAnnouncement


class BrodcastManager(object):
    """
        Manages Local Server List Ase, 
        Local Server List Announcement and Master Server List Announcement
    """

    def __init__(self, server) -> None:
        self._lcl_serverlist = LocalServerListASE(server)
        self._lcl_announcer = LocalServerListAnnouncer(server)
        self._mstr_serverlist = MasterServerListAnnouncement(server)

    def start_local_server_list_ase(self) -> Literal[True] | None:
        """Tells MTA Client local server list port"""
        Thread(
            target=self._lcl_serverlist.start,
            name="Local Server List ASE",
            args=(),
        ).start()
        return True

    def start_local_server_list_announces(self) -> Literal[True] | None:
        """Shows server in local game server list."""
        Thread(
            target=self._lcl_announcer.start,
            name="Local Server List Announcer",
            args=(),
        ).start()
        return True

    def start_master_server_announces(self) -> Literal[True] | None:
        """Shows server in game server list"""
        Thread(
            target=self._mstr_serverlist.start,
            name="Master Server List Announcer",
            args=(),
        ).start()
        return True
