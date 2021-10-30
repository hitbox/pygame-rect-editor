from engine.external import pygame

class Clock:

    impl = pygame.time.Clock

    def __init__(self, framerate=None):
        if framerate is None:
            framerate = 60
        self.framerate = framerate
        self._clock = self.impl()

    def tick(self):
        return self._clock.tick(self.framerate)
