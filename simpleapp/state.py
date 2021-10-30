from engine.clock import Clock
from engine.external import pygame
from engine.state import BaseState

class IntroState(BaseState):

    def __init__(self):
        self.clock = Clock()

    def update(self):
        elapsed = self.clock.tick()

        # XXX:
        # 2021-10-30
        # LEFT OFF HERE
        # No idea what I was thinking and this is all very confusing.
