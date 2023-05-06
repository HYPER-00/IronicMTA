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

MAX_ASE_GAME_TYPE_LENGTH     = 200
MAX_ASE_MAP_NAME_LENGTH      = 200
MAX_RULE_KEY_LENGTH          = 200
MAX_RULE_VALUE_LENGTH        = 200
MAX_ANNOUNCE_VALUE_LENGTH    = 200

light_min_interval = 10 * 1000
last_player_count = None

start_time = time.time()

def uc(value: int) -> str: return str(chr(value))

class StringStream(io.StringIO):
    def __init__(self, initial_value: str = "", newline: str  = None) -> None:
        super().__init__(initial_value, newline)
    @overload
    def writeWithLen(self, value: str):
        self.write(uc(str(len(value) + 1)))
        self.write(value)
    @overload
    def writeWithLen(self, value: int):
        self.write(str(value))
    @overload
    def writeWithLen(self, value: bool):
        self.write(1 if value else 0)
    @overload
    def writeWithLen(self, value: Any):
        self.writeWithLen(value)

class AseVersion:
    def __init__(self) -> None: ...
    @property
    def v1_5(self): return '1.5' 
    @property
    def v1_5n(self): return '1.5n' 

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
        ase_version: AseVersion, 
        joined_players: int | str, 
        max_players: int | str,
        player_count: int,
        build_type: str,
        build_number: str,
        game_type: str,
        ping: int | str,
        net_route: int,
        up_time: str,
        http_port: int | str,
        map_name: str,
        password: str | int,
        players: List[Player]
    ) -> None: 

        port = str(port)

        self.string_stream = StringStream()

        self.string_stream.write('EYE1')
        self.string_stream.write(uc(4))
        self.string_stream.write('mta')
        self.string_stream.write(uc(len(port) + 1))
        self.string_stream.write(port)
        self.string_stream.write(uc(len(server_name) + 1))
        self.string_stream.write(server_name)
        self.string_stream.write(uc(len(game_type) + 1))
        self.string_stream.write(game_type)
        self.string_stream.write(uc(len(map_name) + 1))
        self.string_stream.write(map_name)
        self.string_stream.write(uc(len(ase_version) + 1))
        self.string_stream.write(ase_version)
        self.string_stream.write(uc(2))
        self.string_stream.write("1" if password or password == '' else "0")
        self.string_stream.write(uc(len(str(player_count)) + 1))
        self.string_stream.write(str(player_count))
        self.string_stream.write(uc(len(str(max_players)) + 1))
        self.string_stream.write(str(max_players))
        self.string_stream.write(uc(len('RuleKey') + 1))
        self.string_stream.write('RuleKey')
        self.string_stream.write(uc(len('RuleValue') + 1))
        self.string_stream.write('RuleValue')
        self.string_stream.write(uc(1))

        uc_flags = 1
        uc_flags |= 0x01    # Nick
        uc_flags |= 0x02    # Team
        uc_flags |= 0x04    # Skin
        uc_flags |= 0x08    # Score
        uc_flags |= 0x016   # Ping
        uc_flags |= 0x032   # Time

        for player in players:
            self.string_stream.write(uc_flags)
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
            self.string_stream.write(uc(len(playername) + 1))
            self.string_stream.write(playername)
            self.string_stream.write(uc(1)) # Team skip
            self.string_stream.write(uc(1)) # Skin Skip
            self.string_stream.write(uc(len('score') + 1))
            self.string_stream.write('score')

            # Ping
            self.string_stream.write("P" * player.ping)

    def __repr__(self) -> str:
        return self.string_stream.getvalue()


class QueryLight:
    def __init__(self, 
        players: List[Player],
        ase_version: AseVersion, 
        settings_manager: SettingsManager,
        build_type: str,
        build_number: str,
        ping: int | str,
        net_route: int,
        up_time: str | int,
    ) -> None: 
        self.settings_manager = settings_manager

        if not self.settings_manager.isloaded:
            self.settings_manager.load()
        self._settings = self.settings_manager.get()

        joined_players = str(len(players))
        last_player_count = int(joined_players)
        net_route = 'N' * 32
        ping = 'P' * 32
        game_type = self._settings['gametype']
        password = self._settings['password']
        server_name = self._settings['servername']
        port = self.settings_manager.getServerAddr()[1]
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
        self.stream = StringStream()
        self.stream.write('EYE2')
        # Game
        self.stream.write(uc(4))
        self.stream.write('mta')
        # Port
        self.stream.write(uc(len(str(port)) + 1))
        self.stream.write(str(port))
        # Server Name
        self.stream.write(uc(len(server_name) + 1))
        self.stream.write(server_name)
        # Game Type
        self.stream.write(uc(len(game_type) + 1))
        self.stream.write(game_type)
        self.stream.write(uc(len(self.strMapName) + 1 + self.extraDataLen))
        self.stream.write(self.strMapName)
        self.stream.write(uc(0))
        self.stream.write(self.strPlayerCount)
        self.stream.write(uc(0))
        self.stream.write(build_type)
        self.stream.write(uc(0))
        self.stream.write(build_number)
        self.stream.write(uc(0))
        self.stream.write(ping)
        self.stream.write(uc(0))
        self.stream.write(net_route)
        self.stream.write(uc(0))
        self.stream.write(up_time)
        self.stream.write(uc(0))
        self.stream.write(http_port)

        self.stream.write(uc(len(ase_version) + 1))
        self.stream.write(ase_version)
        # Passworded
        self.stream.write(uc(has_password))
        # Serial Verification
        self.stream.write(uc(0))
        # Players Count
        self.stream.write(uc(min(int(joined_players), 255)))
        # Players Count
        self.stream.write(uc(int(max(int(max_players), 255))))

        _bytes_left = 1340 - self.stream.tell()
        for player in players:
            _player_nick = player.getPlayerNick()
            if _bytes_left > 0:
                if (_bytes_left - (len(_player_nick) + 2)) > 0:
                    self.stream.write(uc(len(_player_nick) + 1))
                    self.stream.write(_player_nick)
                    _bytes_left -= len(_player_nick) + 2
                else:
                    _players_left = f'And {_player_nick} more'
                    self.stream.write(uc(len(_players_left) + 1))
                    self.stream.write(_players_left)

    def getLastPlayerCount(self) -> int:
        return int()

    def __repr__(self) -> str:
        return self.stream.getvalue()

class QueryXFireLight:
    def __init__(self, 
        port: int | str, 
        server_name: str,
        ase_version: AseVersion, 
        joined_players: int | str, 
        max_players: int | str,
        player_count: int,
        build_type: str,
        build_number: str,
        game_type: str,
        ping: int | str,
        net_route: int,
        up_time: str,
        http_port: int | str,
        map_name: str,
        password: str | int,
        players: List[Player]
    ) -> None: 

        port = str(port)
        str_player_count = f'{joined_players}/{max_players}'

        self.string_stream = StringStream()

        self.string_stream.write('EYE1')
        self.string_stream.write(uc(4))
        self.string_stream.write('mta')
        self.string_stream.write(uc(len(server_name) + 1))
        self.string_stream.write(server_name)
        self.string_stream.write(uc(len(game_type) + 1))
        self.string_stream.write(game_type)
        self.string_stream.write(uc(len(map_name) + 2 + len(str_player_count)))
        self.string_stream.write(map_name)
        self.string_stream.write(uc(0))
        self.string_stream.write(str_player_count)
        self.string_stream.write(uc(len(ase_version) + 1))
        self.string_stream.write(ase_version)
        self.string_stream.write("1" if password or password == '' else "0")
        self.string_stream.write(uc(min(joined_players, 255)))
        self.string_stream.write(uc(max(max_players, 255)))

    def __repr__(self) -> str:
        return self.string_stream.getvalue()

class QueryLightCached:
    def __init__(
        self, 
        players: List[Player], 
        ase_version: AseVersion, 
        settings: SettingsManager,
        build_type: str,
        build_number: str,
        ping: int | str,
        net_route: int,
        up_time: str | int, #8
    ) -> None:
        self._query = None
        if last_player_count or time.time() - start_time > light_min_interval:
            if len(players) != last_player_count:
                self._query = QueryLight(
                    ase_version, 
                    settings,
                    build_type,
                    build_number,
                    ping,
                    net_route,
                    up_time,
                    players=players,
                )

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
