"""IronicMTA Network core"""


from .wrapper import NetworkWrapper
from .packet_ids import PacketID, PacketPriority, PacketReliability
from .packet_handler.io import BitStream
