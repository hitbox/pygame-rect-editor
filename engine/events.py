import collections

from enum import Enum
from enum import EnumMeta
from enum import auto

from engine.external import pygame

class EventError(Exception):
    pass


class Events(Enum):

    def _generate_next_value_(name, start, count, last_values):
        """
        generate integers compatible with pygame's event system, USEREVENT integers.
        """
        if last_values:
            return last_values[-1] + 1
        else:
            return pygame.USEREVENT

    APPRUN = auto()


_listeners = collections.defaultdict(list)

def listen(*args):
    if len(args) not in (1, 2):
        raise EventError('invalid number of arguments.')

    if len(args) == 2:
        event_type, func = args
        _listeners[event_type].append(func)

    elif len(args) == 1:
        # called as decorator
        event_type = args[0]
        def wrapper(func):
            _listeners[event_type].append(func)
        return wrapper


def notify(event):
    for callback in _listeners[event.type]:
        callback(event)

def update():
    for event in pygame.event.get():
        notfiy(event)
