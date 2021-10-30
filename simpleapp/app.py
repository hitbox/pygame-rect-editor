from engine.app import App
from engine.events import Events
from engine.external import pygame
from engine.screen import PygameScreen

from simpleapp.state import IntroState

def create_app():
    initial_state = IntroState()
    app = App(initial_state=initial_state)

    @app.listen(Events.APPRUN.value)
    def on_apprun(event):
        pygame.display.set_mode((500,500))
        app.switch(IntroState())

    @app.listen(pygame.QUIT)
    def on_quit(event):
        print(event)

    return app
