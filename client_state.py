"""
    Client States
"""

class ConnectionState:
    """
        Connection State for client
        * Disconnected
        * Mod name sent
        * Server version sent
        * Joined
        * Timout
        * Quit
    """
    def __init__(self) -> None:
        self.disconnected = 0
        self.mod_name_sent = 7
        self.server_version_sent = 2
        self.joined = 22
        self.timout = 6
        self.quit = 255