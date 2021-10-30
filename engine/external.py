import contextlib
import os

with open(os.devnull, 'w') as _:
    with contextlib.redirect_stdout(_):
        import pygame
