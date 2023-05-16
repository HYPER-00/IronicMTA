class PacketReliability:
    def __init__(self) -> None:
        self.unreliable = 0
        self.unreliable_sequenced = 1
        self.reliable = 2
        self.reliableS_squenced = 3
        self.reliable_sequenced_can_drop_packets = 4
