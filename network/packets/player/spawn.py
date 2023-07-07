"""
    Player Spawn Packet
"""

from network.packet_base import Packet
from player_manager import Player
from vectors import Vector3

class Packet_PlayerSpawn(Packet):
    def __init__(self, player: Player) -> None:
        super().__init__()

