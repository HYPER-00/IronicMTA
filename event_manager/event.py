from typing import Any
from errors import EventHandlerError

class EventHandler(object):
    def __init__(self):
        self._global_events = {
            "onServerInitalize": [],
            "onServerStart": [],
            "onServerNetworkStart": [],
            "onMasterServerAnnounce": [],
            "onServerPortsCheck": [],
            "onHTTPServerStart": [],
            "onServerSettingsLoad": [],
            "onReceivePacket": []
        }

    def onServerInitalize(self, _func):
        """onServerInitialize

        Args:
            arg_1 (server): Server Instance
        """
        self._global_events["onServerInitalize"].append(_func)

    def onServerStart(self, _func):
        """onServerStart

        Args:
            arg_1 (server): Server Instance
        """        
        self._global_events["onServerStart"].append(_func)
    
    def onServerNetworkStart(self, _func):
        """onServerNetworkStart

        Args:
            arg_1 (NetworkWrapper): Server Network Instance
        """        
        self._global_events["onServerNetworkStart"].append(_func)
    
    def onMasterServerAnnounce(self, _func):
        """onMasterServerAnnounce

        Args:
            arg_1 (server): Server Instance
        """        
        self._global_events["onMasterServerAnnounce"].append(_func)

    def onHTTPServerStart(self, _func):
        """onHTTPServerStart

        Args:
            arg_1 (HTTPServer): Server Instance
            arg_2 (HTTPServer): HTTP Server Instance
        """        
        self._global_events["onHTTPServerStart"].append(_func)

    def onServerSettingsLoad(self, _func):
        """onServerSettingsLoad

        Args:
            arg_1 (dict): Server Settings
        """        
        self._global_events["onServerSettingsLoad"].append(_func)

    def onReceivePacket(self, _func):
        """onReceivePacket

        Args:
            arg_1 (Server): Server Instance
            arg_2 (PacketID): Packet Id
            arg_3 (int): Player Binary Address
            arg_4 (bytes): Packet Content
        """        
        self._global_events["onReceivePacket"].append(_func)

    def onServerPortsCheck(self, _func):
        """onServerPortsCheck

        Args:
            arg_1 (Server): Server Instance
            arg_2 (bool): Game Port
            arg_3 (bool): HTTP Port
        """        
        self._global_events["onServerPortsCheck"].append(_func)

    def call(self, event_name: str, *args) -> Any:
        if not event_name in self._global_events.keys():
            raise EventHandler(f"{event_name} is not registred!")
        if self._global_events[event_name]:
            for _iter_func in self._global_events[event_name]:
                _iter_func(*args)
