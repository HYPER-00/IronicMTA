import re
import io
import time
from ..limits import MAX_ASE_GAME_TYPE_LENGTH, MAX_ASE_MAP_NAME_LENGTH

light_min_interval = 10 * 1000
last_player_count = None

start_time = time.time()


def char(value: int) -> str:
    """Converts int to string"""
    return str(chr(value))


class QueryFull:
    def __init__(self, server) -> None:

        port = str(server.getAddr()[1])
        server_name = server.get_name()
        ase_version = server.get_ase_version()
        max_players = server.get_max_players()
        player_count = server.get_player_count()
        game_type = server.get_game_type()[MAX_ASE_GAME_TYPE_LENGTH:]
        map_name = server.get_map_name()[MAX_ASE_MAP_NAME_LENGTH:]
        ispassword = server.is_passworded()
        players = server.get_all_players()

        self.sstream = io.StringIO()

        self.sstream.write('EYE1')
        self.sstream.write(char(4))
        self.sstream.write('mta')
        self.sstream.write(char(len(port) + 1))
        self.sstream.write(port)
        self.sstream.write(char(len(server_name) + 1))
        self.sstream.write(server_name)
        self.sstream.write(char(len(game_type) + 1))
        self.sstream.write(game_type)
        self.sstream.write(char(len(map_name) + 1))
        self.sstream.write(map_name)
        self.sstream.write(char(len(ase_version._value_) + 1))
        self.sstream.write(ase_version._value_)
        self.sstream.write(char(2))
        self.sstream.write(str(int(ispassword)))
        self.sstream.write(char(len(str(player_count)) + 1))
        self.sstream.write(str(player_count))
        self.sstream.write(char(len(str(max_players)) + 1))
        self.sstream.write(str(max_players))
        self.sstream.write(char(len('RuleKey') + 1))
        self.sstream.write('RuleKey')
        self.sstream.write(char(len('RuleValue') + 1))
        self.sstream.write('RuleValue')
        self.sstream.write(char(1))

        player_flags = 1
        player_flags |= 0x01    # Nick
        player_flags |= 0x02    # Team
        player_flags |= 0x04    # Skin
        player_flags |= 0x08    # Score
        player_flags |= 0x016   # Ping
        player_flags |= 0x032   # Time

        for player in players:
            self.sstream.write(str(player_flags))
            ansi_escape = re.compile(
                r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', re.VERBOSE)
            playername = ansi_escape.sub('', player.name)
            if len(playername) == 0:
                playername = player.nick
            self.sstream.write(char(len(playername) + 1))
            self.sstream.write(playername)
            self.sstream.write(char(1))  # Team skip
            self.sstream.write(char(1))  # Skin Skip
            self.sstream.write(char(len('score') + 1))
            self.sstream.write('score')

            # Ping
            self.sstream.write("P" * player.ping)

    def __repr__(self) -> str:
        return self.sstream.getvalue()


class QueryLight:
    def __init__(self, server) -> None:
        self._settings_manager = server.get_settings_manager()
        self._settings = server.get_settings()
        build_type = server.get_build_type()
        build_number = "0"

        joined_players = str(server.get_player_count())
        ase_version = server.get_ase_version()
        up_time = '0'
        if server.is_running():
            up_time = str(server.get_uptime())
            try:
                net_route = str(server.get_network().getNetRoute())
                if not len(net_route):
                    net_route = 'N' * 32
            except:
                net_route = 'N' * 32
        else:
            net_route = 'N' * 32
        ping = 'P' * 32
        game_type = server.get_game_type()
        server_name = server.get_name()
        port = self._settings_manager.get_server_address()[1]
        max_players = server.get_max_players()
        http_port = str(self._settings_manager.get_http_port())

        self.player_count = f'{joined_players}/{max_players}'
        self.extra_data_length = (len(self.player_count) + 1 + len(str(build_type._value_)) + 1 + len(build_number) + 1 + len(ping) + 1
                                  + len(str(net_route)) + 1 + len(up_time) + 1 + len(http_port) + 1)
        self.ma_mapname_length = 250 - self.extra_data_length
        self.map_name = server.get_map_name(
        )[:MAX_ASE_MAP_NAME_LENGTH - 3] + "..."
        ispassworded = server.is_passworded()
        self.sstream = io.StringIO()
        self.sstream.write('EYE2')
        # Game
        self.sstream.write(char(4))
        self.sstream.write('mta')
        # Port
        self.sstream.write(char(len(str(port)) + 1))
        self.sstream.write(str(port))
        # Server Name
        self.sstream.write(char(len(server_name) + 1))
        self.sstream.write(server_name)
        # Game Type
        self.sstream.write(char(len(game_type) + 1))
        self.sstream.write(game_type)
        self.sstream.write(
            char(len(self.map_name) + 1 + self.extra_data_length))
        self.sstream.write(self.map_name)
        self.sstream.write(char(0))
        self.sstream.write(self.player_count)
        self.sstream.write(char(0))
        self.sstream.write(str(build_type._value_))
        self.sstream.write(char(0))
        self.sstream.write(build_number)
        self.sstream.write(char(0))
        self.sstream.write(ping)
        self.sstream.write(char(0))
        self.sstream.write(net_route)
        self.sstream.write(char(0))
        self.sstream.write(up_time)
        self.sstream.write(char(0))
        self.sstream.write(http_port)

        self.sstream.write(char(len(ase_version.value) + 1))
        self.sstream.write(ase_version.value)
        # Passworded
        self.sstream.write(char(ispassworded))
        # Serial Verification
        self.sstream.write(char(0))
        # Players Count
        self.sstream.write(char(min(int(joined_players), 255)))
        # Players Count
        self.sstream.write(char(int(max(int(max_players), 255))))

        _bytes_left = 1340 - self.sstream.tell()
        for player in server.get_all_players():
            _player_nick = player.getNick()
            if _bytes_left > 0:
                if (_bytes_left - (len(_player_nick) + 1)) > 0:
                    self.sstream.write(char(len(_player_nick) + 1))
                    self.sstream.write(f"{_player_nick}\0")
                    _bytes_left -= len(_player_nick) + 1
                else:
                    _players_left = f'And {_player_nick} more\0'
                    self.sstream.write(char(len(_players_left) + 1))
                    self.sstream.write(_players_left)

    def __repr__(self) -> str:
        return self.sstream.getvalue()

    def __str__(self) -> str:
        return self.sstream.getvalue()


class QueryXFireLight:
    def __init__(self, server) -> None:
        joined_players = server.get_player_count()
        max_players = server.get_max_players()
        str_player_count = f'{joined_players}/{max_players}'
        server_name = server.get_name()
        ase_version = server.get_ase_version()
        game_type = server.get_game_type()
        map_name = server.get_map_name()
        password = server.is_passworded()

        self.sstream = io.StringIO()

        self.sstream.write('EYE3')
        self.sstream.write(char(4))
        self.sstream.write('mta')
        self.sstream.write(char(len(server_name) + 1))
        self.sstream.write(server_name)
        self.sstream.write(char(len(game_type) + 1))
        self.sstream.write(game_type)
        self.sstream.write(char(len(map_name) + 2 + len(str_player_count)))
        self.sstream.write(map_name)
        self.sstream.write(char(0))
        self.sstream.write(str_player_count)
        self.sstream.write(char(len(ase_version._value_) + 1))
        self.sstream.write(ase_version._value_)
        self.sstream.write(
            char(1) if password or password == '' else char(0))
        self.sstream.write(char(min(joined_players, 255)))
        self.sstream.write(char(max(max_players, 255)))

    def __repr__(self) -> str:
        return self.sstream.getvalue()
