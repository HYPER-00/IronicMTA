from ..errors import EventHandlerError
from typing import List, Dict, Callable, Any


class EventHandlerBase(object):
    """Event Handler Base"""

    def __init__(self) -> None:
        self._global_events: Dict[str, List[Callable[..., Any]]]  = {}

    def call(self, event_name: str, *args) -> None:
        """Call event handmer

        Args:
            event_name (str): The event name to call it

        Raises:
            EventHandlerError: If the event name not found
        """
        if not event_name in self._global_events.keys():
            raise EventHandlerError(f"{event_name} is not registred!")
        if self._global_events[event_name]:
            for _iter_func in self._global_events[event_name]:
                _iter_func(*args[:_iter_func.__code__.co_argcount])
