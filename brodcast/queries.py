import re
import io
import time
from common import (
    MAX_ASE_GAME_TYPE_LENGTH,
    MAX_ASE_MAP_NAME_LENGTH,
)

light_min_interval = 10 * 1000
last_player_count = None

start_time = time.time()

def uchar(value: int) -> str:
    """Converts int to string"""
    return str(chr(value))

class QueryFull:
    def __init__(self, server) -> None:

        port = str(server.getAddr()[1])
        server_name = server.getName()
        ase_version = server.getAseVersion()
        max_players = server.getMaxPlayers()
        player_count = server.getPlayerCount()
        game_type = server.getGameType()[MAX_ASE_GAME_TYPE_LENGTH:]
        map_name = server.getMapName()[MAX_ASE_MAP_NAME_LENGTH:]
        ispassword = server.isPassworded()
        players = server.getAllPlayers()

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
        self.sstream.write(str(int(ispassword)))
        self.sstream.write(uchar(len(str(player_count)) + 1))
        self.sstream.write(str(player_count))
        self.sstream.write(uchar(len(str(max_players)) + 1))
        self.sstream.write(str(max_players))
        self.sstream.write(uchar(len('RuleKey') + 1))
        self.sstream.write('RuleKey')
        self.sstream.write(uchar(len('RuleValue') + 1))
        self.sstream.write('RuleValue')
        self.sstream.write(uchar(1))

        player_flags = 1
        player_flags |= 0x01    # Nick
        player_flags |= 0x02    # Team
        player_flags |= 0x04    # Skin
        player_flags |= 0x08    # Score
        player_flags |= 0x016   # Ping
        player_flags |= 0x032   # Time

        for player in players:
            self.sstream.write(player_flags)
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
    def __init__(self, server) -> None:
        self._settings_manager = server.getSettingsManager()
        self._settings_manager.try2load()
        self._settings = self._settings_manager.get()
        build_type = server.getBuildType()
        build_number = "1"

        joined_players = str(server.getPlayerCount())
        ase_version = server.getAseVersion()
        net_route = 'N' * 32
        ping = 'P' * 32
        game_type = self._settings['gametype'][MAX_ASE_GAME_TYPE_LENGTH:]
        password = self._settings['password']
        server_name = self._settings['servername']
        port = self._settings_manager.getServerAddr()[1]
        max_players = server.getMaxPlayers()
        http_port = str(self._settings['httpport'])

        up_time = str(server.getUptime())

        self.strPlayerCount = f'{joined_players}/{max_players}'
        self.extraDataLen = (len(self.strPlayerCount) + 1 + len(build_type) + 1 + len(build_number) + 1 + len(ping) + 1
                                                          + len(str(net_route)) + 1 + len(up_time) + 1 + len(http_port) + 1)
        self.maxMapNameLen = 250 - self.extraDataLen
        self.strMapName = server.getMapName()[:MAX_ASE_MAP_NAME_LENGTH - 3] + "..."
        ispassworded = server.isPassworded()
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
        self.sstream.write(uchar(ispassworded))
        # Serial Verification
        self.sstream.write(uchar(0))
        # Players Count
        self.sstream.write(uchar(min(int(joined_players), 255)))
        # Players Count
        self.sstream.write(uchar(int(max(int(max_players), 255))))

        _bytes_left = 1340 - self.sstream.tell()
        for player in server.getAllPlayers():
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
    def __init__(self, server) -> None:
        joined_players = server.getPlayerCount()
        max_players = server.getMaxPlayers()
        str_player_count = f'{joined_players}/{max_players}'
        server_name = server.getName()
        ase_version = server.getAseVersion()
        game_type = server.getGameType()
        map_name = server.getMapName()
        password = server.isPassworded()

        self.sstream = io.StringIO()

        self.sstream.write('EYE3')
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
        self.sstream.write(uchar(1) if password or password == '' else uchar(0))
        self.sstream.write(uchar(min(joined_players, 255)))
        self.sstream.write(uchar(max(max_players, 255)))

    def __repr__(self) -> str:
        return self.sstream.getvalue()
