import sys
import os

_dir = __file__.split('\\')[:-2]
if _dir[0].endswith(':'): _dir[0] += '\\'
sys.path.insert(0, os.path.join(*_dir))


import re
import io
import time
from player_manager import Player
from settings_manager import SettingsManager

from typing import overload, List, Any
from enum import Enum

MAX_ASE_GAME_TYPE_LENGTH     = 200
MAX_ASE_MAP_NAME_LENGTH      = 200
MAX_RULE_KEY_LENGTH          = 200
MAX_RULE_VALUE_LENGTH        = 200
MAX_ANNOUNCE_VALUE_LENGTH    = 200

light_min_interval = 10 * 1000
last_player_count = None

start_time = time.time()

def uchar(value: int) -> str:
    return str(chr(value))

class AseVersions(Enum):
    """
        Ase Queries Versions
        * 1.5  => Normal
        * 1.5n => For mta developers & other versions
    """
    v1_5  = "1.5"
    v1_5n = "1.5n"

class QueryTypes:
    def __init__(self) -> None:
        self.Full = 'x'
        self.Light = 'b'
        self.LightRelease = 'r'
        self.XFire = 'x'
        self.Version = 'v'

class QueryFull:
    def __init__(self, 
        port: int | str, 
        server_name: str,
        ase_version: AseVersions,
        max_players: int | str,
        player_count: int,
        game_type: str,
        map_name: str,
        password: str | int,
        players: List[Player]
    ) -> None:

        port = str(port)

        self.sstream = io.StringIO()

        self.sstream.write('EYE1')
        self.sstream.write(uchar(4))
        self.sstream.write('mta')
        self.sstream.write(uchar(len(port) + 1))
        self.sstream.write(port)
        self.sstream.write(uchar(len(server_name) + 1))
        self.sstream.write(server_name)
        self.sstream.write(uchar(len(game_type) + 1))
        self.sstream.write(game_type)
        self.sstream.write(uchar(len(map_name) + 1))
        self.sstream.write(map_name)
        self.sstream.write(uchar(len(ase_version._value_) + 1))
        self.sstream.write(ase_version._value_)
        self.sstream.write(uchar(2))
        self.sstream.write("1" if password or password == '' else "0")
        self.sstream.write(uchar(len(str(player_count)) + 1))
        self.sstream.write(str(player_count))
        self.sstream.write(uchar(len(str(max_players)) + 1))
        self.sstream.write(str(max_players))
        self.sstream.write(uchar(len('RuleKey') + 1))
        self.sstream.write('RuleKey')
        self.sstream.write(uchar(len('RuleValue') + 1))
        self.sstream.write('RuleValue')
        self.sstream.write(uchar(1))

        uc_flags = 1
        uc_flags |= 0x01    # Nick
        uc_flags |= 0x02    # Team
        uc_flags |= 0x04    # Skin
        uc_flags |= 0x08    # Score
        uc_flags |= 0x016   # Ping
        uc_flags |= 0x032   # Time

        for player in players:
            self.sstream.write(uc_flags)
            ansi_escape = re.compile(r'''
                \x1B  
                (?:   
                    [@-Z\\-_]
                |     
                    \[
                    [0-?]*  
                    [ -/]*  
                    [@-~]   
                )
            ''', re.VERBOSE)       
            playername = ansi_escape.sub('', player.name)
            if len(playername) == 0:
                playername = player.nick
            self.sstream.write(uchar(len(playername) + 1))
            self.sstream.write(playername)
            self.sstream.write(uchar(1)) # Team skip
            self.sstream.write(uchar(1)) # Skin Skip
            self.sstream.write(uchar(len('score') + 1))
            self.sstream.write('score')

            # Ping
            self.sstream.write("P" * player.ping)

    def __repr__(self) -> str:
        return self.sstream.getvalue()


class QueryLight:
    def __init__(self, 
        players: List[Player],
        ase_version: AseVersions,
        settings_manager: SettingsManager,
        build_type: str,
        build_number: str,
        ping: int | str,
        net_route: int,
        up_time: str | int,
    ) -> None:
        self._settings_manager = settings_manager

        if not self._settings_manager.isloaded:
            self._settings_manager.load()
        self._settings = self._settings_manager.get()

        joined_players = str(len(players))
        net_route = 'N' * 32
        ping = 'P' * 32
        game_type = self._settings['gametype']
        password = self._settings['password']
        server_name = self._settings['servername']
        port = self._settings_manager.getServerAddr()[1]
        max_players = str(self._settings['maxplayers'])
        http_port = str(self._settings['httpport'])

        up_time = str(up_time)

        self.strPlayerCount = f'{joined_players}/{max_players}'
        self.extraDataLen = (len(self.strPlayerCount) + 1 + len(build_type) + 1 + len(build_number) + 1 + len(ping) + 1
                                                          + len(str(net_route)) + 1 + len(up_time) + 1 + len(http_port) + 1)
        self.maxMapNameLen = 250 - self.extraDataLen
        self.strMapName = self._settings['mapname'][:MAX_ASE_MAP_NAME_LENGTH - 3] + "..."
        has_password = 0
        if password or password != "":
            has_password = 1
        self.sstream = io.StringIO()
        self.sstream.write('EYE2')
        # Game
        self.sstream.write(uchar(4))
        self.sstream.write('mta')
        # Port
        self.sstream.write(uchar(len(str(port)) + 1))
        self.sstream.write(str(port))
        # Server Name
        self.sstream.write(uchar(len(server_name) + 1))
        self.sstream.write(server_name)
        # Game Type
        self.sstream.write(uchar(len(game_type) + 1))
        self.sstream.write(game_type)
        self.sstream.write(uchar(len(self.strMapName) + 1 + self.extraDataLen))
        self.sstream.write(self.strMapName)
        self.sstream.write(uchar(0))
        self.sstream.write(self.strPlayerCount)
        self.sstream.write(uchar(0))
        self.sstream.write(build_type)
        self.sstream.write(uchar(0))
        self.sstream.write(build_number)
        self.sstream.write(uchar(0))
        self.sstream.write(ping)
        self.sstream.write(uchar(0))
        self.sstream.write(net_route)
        self.sstream.write(uchar(0))
        self.sstream.write(up_time)
        self.sstream.write(uchar(0))
        self.sstream.write(http_port)

        self.sstream.write(uchar(len(ase_version.value) + 1))
        self.sstream.write(ase_version.value)
        # Passworded
        self.sstream.write(uchar(has_password))
        # Serial Verification
        self.sstream.write(uchar(0))
        # Players Count
        self.sstream.write(uchar(min(int(joined_players), 255)))
        # Players Count
        self.sstream.write(uchar(int(max(int(max_players), 255))))

        _bytes_left = 1340 - self.sstream.tell()
        for player in players:
            _player_nick = player.getPlayerNick()
            if _bytes_left > 0:
                if (_bytes_left - (len(_player_nick) + 2)) > 0:
                    self.sstream.write(uchar(len(_player_nick) + 1))
                    self.sstream.write(_player_nick)
                    _bytes_left -= len(_player_nick) + 2
                else:
                    _players_left = f'And {_player_nick} more'
                    self.sstream.write(uchar(len(_players_left) + 1))
                    self.sstream.write(_players_left)

    def __repr__(self) -> str:
        return self.sstream.getvalue()

class QueryXFireLight:
    def __init__(self, 
        port: int | str, 
        server_name: str,
        ase_version: AseVersions,
        joined_players: int | str,
        max_players: int | str,
        game_type: str,
        map_name: str,
        password: str | int,
    ) -> None:

        port = str(port)
        str_player_count = f'{joined_players}/{max_players}'

        self.sstream = io.StringIO()

        self.sstream.write('EYE1')
        self.sstream.write(uchar(4))
        self.sstream.write('mta')
        self.sstream.write(uchar(len(server_name) + 1))
        self.sstream.write(server_name)
        self.sstream.write(uchar(len(game_type) + 1))
        self.sstream.write(game_type)
        self.sstream.write(uchar(len(map_name) + 2 + len(str_player_count)))
        self.sstream.write(map_name)
        self.sstream.write(uchar(0))
        self.sstream.write(str_player_count)
        self.sstream.write(uchar(len(ase_version._value_) + 1))
        self.sstream.write(ase_version._value_)
        self.sstream.write("1" if password or password == '' else "0")
        self.sstream.write(uchar(min(joined_players, 255)))
        self.sstream.write(uchar(max(max_players, 255)))

    def __repr__(self) -> str:
        return self.sstream.getvalue()

class QueryLightCached:
    def __init__(
        self,
        players: List[Player],
        ase_version: AseVersions,
        settings: SettingsManager,
        build_type: str,
        build_number: str,
        ping: int | str,
        net_route: int,
        up_time: str | int,
    ) -> None:
        self._query = None
        if last_player_count or time.time() - start_time > light_min_interval:
            if len(players) != last_player_count:
                self._query = ...

    def __repr__(self) -> str:
        if self._query:
            return self._query
        else:
            return ''

    def __str__(self) -> str:
        if self._query:
            return self._query
        else:
            return ''
