from typing import Any
from errors import EventHandlerError

class EventHandlerBase(object):
    """Event Handler Base"""    
    def __init__(self) -> None:
        self._global_events = {}

    def call(self, event_name: str, *args) -> Any:
        """Call event from name

        Args:
            event_name (str): The event name to call

        Raises:
            EventHandler: If event name not found
        """        
        if not event_name in self._global_events.keys():
            raise EventHandlerError(f"{event_name} is not registred!")
        if self._global_events[event_name]:
            for _iter_func in self._global_events[event_name]:
                _iter_func(*args[:_iter_func.__code__.co_argcount])
