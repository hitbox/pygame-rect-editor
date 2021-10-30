import engine.clock

import engine.events

from engine.events import Events
from engine.external import pygame

class App:

    def __init__(self, initial_state=None):
        self.initial_state = initial_state
        self.reset()

    def reset(self):
        self.running = False
        self._state = None

    def switch(self, state):
        self._state = state

    def run(self, state=None):
        self.state = state or self.initial_state
        self.running = True
        self.notify_running()
        while self.running:
            engine.events.update()
            self.step()

    def step(self):
        self.state.update()
        if self._state:
            self.state = self._state
            self._state = None

    def notify_running(self):
        event = pygame.event.Event(Events.APPRUN.value, engine=self)
        self.notify(event)

    @staticmethod
    def listen(*args):
        return engine.events.listen(*args)

    @staticmethod
    def notify(event):
        engine.events.notify(event)
