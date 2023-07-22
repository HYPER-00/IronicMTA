from typing import Any
from errors import EventHandlerError

class EventHandler(object):
    def __init__(self):
        self._global_events = {
            "onServerStart": None
        }

    def onServerStart(self, _func):
        self._global_events["onServerStart"] = _func

    def call(self, event_name: str, *args) -> Any:
        if not event_name in self._global_events.keys():
            raise EventHandler(f"{event_name} is not registred!")
        if self._global_events[event_name]:
            return self._global_events[event_name](*args)
