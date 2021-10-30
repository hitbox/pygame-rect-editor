"Create images of things"
import draw

from external import pygame

def get_image(size, flags=None):
    if flags is None:
        flags = pygame.SRCALPHA
    return pygame.Surface(size, flags)

def cross(size, color, linewidth=1, **kwargs):
    imagekwargs = kwargs.get('imagekwargs', {})
    padding = kwargs.get('padding')
    if imagekwargs is None:
        imagekwargs = {}
    image = get_image(size, **imagekwargs)
    draw.cross(image, color, linewidth, padding=padding)
    return image

_button_width_ratio = 5

def minusbutton(size, color):
    """
    Opinionated minus button renderer
    """
    image = get_image(size)
    rect = image.get_rect()
    width = min(rect.size) // _button_width_ratio
    draw.hbar(image, color, width, padding=width)
    draw.border(image, color, width=width//2)
    return image

def plusbutton(size, color):
    """
    Opinionated plus button renderer
    """
    rect = pygame.Rect((0,0), size)
    width = min(rect.size) // _button_width_ratio
    image = cross(rect.size, color, linewidth=width, padding=width)
    draw.border(image, color, width=width//2)
    return image
