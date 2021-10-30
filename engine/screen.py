from abc import ABC
from abc import abstractmethod

from engine.events import Events
from engine.events import listen
from engine.external import pygame

class BaseScreen(ABC):

    @abstractmethod
    def clear(self):
        "Clear the screen ready for drawing"

    @abstractmethod
    def draw(self, objects):
        "Draw objects"


class PygameScreen(BaseScreen):

    def __init__(self, size):
        self.size = size

    # NOTE:
    # this isn't going to work because we pass the function without accessing
    # it as an instance attribute and we lose `self`.
    #@listen(Events.APPRUN.value)
    #def on_apprun(event):
    #    pygame.display.set_mode(self.size)

    def clear(self):
        pass
