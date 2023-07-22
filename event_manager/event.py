from typing import Any
from errors import EventHandlerError

class EventHandler(object):
    def __init__(self):
        self._global_events = {
            "onServerInitalize": None,
            "onServerStart": None,
            "onServerNetworkStart": None,
            "onMasterServerAnnounce": None,
            "onHTTPServerStart": None,
            "onServerSettingsLoad": None
        }

    def onServerInitalize(self, _func):
        """onServerInitialize

        Args:
            arg_1 (server): Server Instance
        """
        self._global_events["onServerInitalize"] = _func

    def onServerStart(self, _func):
        """onServerStart

        Args:
            arg_1 (server): Server Instance
        """        
        self._global_events["onServerStart"] = _func
    
    def onServerNetworkStart(self, _func):
        """onServerNetworkStart

        Args:
            arg_1 (NetworkWrapper): Server Network Instance
        """        
        self._global_events["onServerNetworkStart"] = _func
    
    def onMasterServerAnnounce(self, _func):
        """onMasterServerAnnounce

        Args:
            arg_1 (server): Server Instance
        """        
        self._global_events["onMasterServerAnnounce"] = _func

    def onHTTPServerStart(self, _func):
        """onHTTPServerStart

        Args:
            arg_1 (HTTPServer): Server Instance
            arg_2 (HTTPServer): HTTP Server Instance
        """        
        self._global_events["onHTTPServerStart"] = _func

    def onServerSettingsLoad(self, _func):
        """onServerSettingsLoad

        Args:
            arg_1 (dict): Server Settings
        """        
        self._global_events["onServerSettingsLoad"] = _func

    def call(self, event_name: str, *args) -> Any:
        if not event_name in self._global_events.keys():
            raise EventHandler(f"{event_name} is not registred!")
        if self._global_events[event_name]:
            return self._global_events[event_name](*args)
