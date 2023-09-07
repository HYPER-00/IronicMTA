from typing import TypedDict


class ServerSettings(TypedDict):
    name: str
    ip: str
    port: int
    debug_port: int
    map_name: str
    game_type: str
    password: str
    max_players: int
