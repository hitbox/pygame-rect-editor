"Draw things on images"
from external import pygame
from shorthand import shorthand

def border(image, color, width):
    """
    Draw border around image
    """
    widthshorthand = shorthand(width)
    rect = image.get_rect()
    # create four sides as rects
    rects = list(image.get_rect() for _ in range(4))
    top, right, bottom, left = rects
    # resize
    top.height = widthshorthand.top
    right.width = widthshorthand.right
    bottom.height = widthshorthand.bottom
    left.width = widthshorthand.left
    # realign
    right.right = rect.right
    bottom.bottom = rect.bottom
    for rect in rects:
        pygame.draw.rect(image, color, rect)

def hbar(image, color, width=1, **kwargs):
    "Horizontal bar"
    padding = shorthand(kwargs.get('padding'))
    rect = image.get_rect()
    rect.width -= padding.right + padding.left
    rect.height -= padding.bottom + padding.top
    rect.top += padding.top
    rect.left += padding.left
    pygame.draw.line(image, color, rect.midleft, rect.midright, width)

def vbar(image, color, width=1, **kwargs):
    "Vertical bar"
    padding = shorthand(kwargs.get('padding'))
    rect = image.get_rect()
    rect.width -= padding.right + padding.left
    rect.height -= padding.bottom + padding.top
    rect.top += padding.top
    rect.left += padding.left
    pygame.draw.line(image, color, rect.midtop, rect.midbottom, width)

def cross(image, color, width=1, **kwargs):
    "Cross shape"
    hbar(image, color, width, **kwargs)
    vbar(image, color, width, **kwargs)
