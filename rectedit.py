# quickly sketching a rect editor
import argparse
import os

from abc import ABC
from abc import abstractmethod
from collections import OrderedDict
from collections import defaultdict
from contextlib import redirect_stdout
from dataclasses import dataclass
from itertools import tee

with redirect_stdout(open(os.devnull, 'w')):
    import pygame

# divide minimum side of rect by...
_button_width_denominator = 5
# ...to get an appealing, *thick* line width for something inside the rect.

_listeners = defaultdict(list)

COMMANDSWITCH = pygame.USEREVENT
COMMANDBEGIN = pygame.USEREVENT + 1

RECTPOINTS = OrderedDict([
    ('topleft', 'bottomright'),
    ('midtop', 'midbottom'),
    ('topright', 'bottomleft'),
    ('midright', 'midleft'),
    ('bottomright', 'topleft'),
    ('midbottom', 'midtop'),
    ('bottomleft', 'bottomright'),
    ('midleft', 'midright'),
])

class RectEditError(Exception):
    pass


@dataclass
class Shorthand:
    top: int
    right: int
    bottom: int
    left: int


@dataclass
class Sprite:
    image: pygame.Surface
    rect: pygame.Rect
    props: dict


class HandleRect:

    def __init__(self, parent, handle):
        self.parent = parent
        self.handle = handle


class EditRect:

    minimum_corner_handle_size = 10

    def _popopt(self, options, key):
        "pop key from options, defaulting to attribute of same name"
        return options.pop(key, getattr(self, key))

    def __init__(self, rect, **options):
        self.rect = rect
        self.minimum_corner_handle_size = self._popopt(options, 'minimum_corner_handle_size')
        if options:
            raise RectEditError(f'Unknown options {", ".join(options)}.')
        self.reset_handles()

    def reset_handles(self):
        self.handles = []
        for attrname, rect in iter_rect_handles(self.rect):
            setattr(self, f'handle_{attrname}', rect)
            self.handles.append(rect)


class DrawRect:

    def __init__(self, color, rect, width):
        self.color = color
        self.rect = rect
        self.width = width

    def __iter__(self):
        return iter((self.color, self.rect, self.width))


class Command(ABC):

    @abstractmethod
    def begin(self, event):
        pass

    @abstractmethod
    def end(self):
        pass


class HighlightCommand(Command):

    def __init__(self, parent):
        self.editor = parent
        self.current = None
        self.handle2drawrect = {}

    def begin(self, event):
        listen(pygame.MOUSEMOTION, self.on_mousemotion)
        listen(pygame.MOUSEBUTTONDOWN, self.on_mousebuttondown)

    def on_mousemotion(self, event):
        # XXX: SMELLY
        # put DrawRect objects in drawing queue when mouse over
        for editrect in self.editor.editrects:
            for handle in editrect.handles:
                handleid = id(handle)
                if handle.collidepoint(event.pos):
                    if handleid not in self.handle2drawrect:
                        self.current = None
                        drawrect = DrawRect((200,200,10), handle, 1)
                        self.handle2drawrect[handleid] = drawrect
                        self.editor.draw_rects.append(drawrect)
                        self.current = handle
                # once a collision has been found, can't we delete all other handles?
                else:
                    if handleid in self.handle2drawrect:
                        drawrect = self.handle2drawrect[handleid]
                        if drawrect in self.editor.draw_rects:
                            self.editor.draw_rects.remove(drawrect)
                            del self.handle2drawrect[handleid]

    def on_mousebuttondown(self, event):
        if self.current:
            # begin dragging but how?
            print(self.current)

    def end(self):
        unsubscribe(pygame.MOUSEMOTION, self.on_mousemotion)
        unsubscribe(pygame.MOUSEBUTTONDOWN, self.on_mousebuttondown)


class AddEditRectCommand(Command):
    """
    Add new EditRect to world.
    """

    def begin(self, event):
        parent = event.parent
        world = parent.world
        editrect = parent.editrects
        rect = pygame.Rect(0,0,world.width // 4,world.height // 4)
        rect.center = world.center
        editrect = EditRect(rect)
        parent.editrects.append(editrect)

    def end(self):
        pass


class MoveRectCommand(Command):

    def begin(self, event):
        self.rect = event.target
        listen(pygame.MOUSEBUTTONUP, self.on_mousebuttonup)
        listen(pygame.MOUSEMOTION, self.on_mousemotion)

    def on_mousemotion(self, event):
        dx, dy = event.rel
        self.rect.x += dx
        self.rect.y += dy

    def on_mousebuttonup(self, event):
        self.end()

    def end(self):
        self.rect = None
        unsubscribe(pygame.MOUSEBUTTONUP, self.on_mousebuttonup)
        unsubscribe(pygame.MOUSEMOTION, self.on_mousemotion)


class CommandManager:

    def __init__(self):
        self.current = None
        listen(COMMANDSWITCH, self.on_commandswitch)

    def switch(self, command):
        event = pygame.event.Event(COMMANDSWITCH, command=command)
        pygame.event.post(event)

    def on_commandswitch(self, event):
        if self.current:
            self.current.end()
        self.current = event.command
        event = pygame.event.Event(COMMANDBEGIN)
        self.current.begin(event)


class RectEditor:

    def __init__(self):
        self.reset()

    def reset(self):
        self.running = False
        self.editrects = []
        self.buttons = []
        self.draw_rects = []
        self.world = None
        self.screen = None
        #
        self.command_manager = CommandManager()
        self.command_manager.switch(HighlightCommand(parent=self))
        #
        listen(pygame.QUIT, self.on_quit)
        listen(pygame.KEYDOWN, self.on_keydown)
        listen(pygame.MOUSEMOTION, self.on_mousemotion)
        listen(pygame.MOUSEBUTTONDOWN, self.on_mousebuttondown)
        listen(pygame.MOUSEBUTTONUP, self.on_mousebuttonup)

    def on_quit(self, event):
        self.running = False

    def on_keydown(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_q):
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def on_mousemotion(self, event):
        pass

    def on_mousebuttondown(self, event):
        for button in self.buttons:
            if button.rect.collidepoint(event.pos):
                event.parent = self
                button.command.begin(event)

    def on_mousebuttonup(self, event):
        pass

    def init(self):
        self.screen = pygame.display.set_mode((800,600))
        self.background = self.screen.copy()
        self.world = self.screen.get_rect()
        self.clock = pygame.time.Clock()

    def loop(self):
        self.running = True
        while self.running:
            elapsed = self.clock.tick(60)
            for event in pygame.event.get():
                notify(event)
            # clear
            self.screen.blit(self.background, (0,0))
            # draw rects and buttons
            for sprite in self.editrects + self.buttons:
                if hasattr(sprite, 'image'):
                    self.screen.blit(sprite.image, sprite.rect)
                else:
                    pygame.draw.rect(self.screen, (200,200,200), sprite.rect, 1)
            # draw rects
            for drawrect in self.draw_rects:
                pygame.draw.rect(self.screen, *drawrect)

            pygame.display.flip()


# events

def listen(event_type, callback):
    """
    Append listener, `callback` for event type `event_type`.
    """
    _listeners[event_type].append(callback)

def notify(event):
    """
    Notify all callback of `event`.
    """
    for callback in _listeners[event.type]:
        callback(event)

def unsubscribe(event_type, callback):
    _listeners[event_type].remove(callback)

def shorthand(*args):
    # https://developer.mozilla.org/en-US/docs/Web/CSS/Shorthand_properties
    keys = 'top right bottom left'.split()
    # XXX: will have to do heavy argument lifting here until we think of a
    #      better solution.
    nargs = len(args)
    if nargs == 1:
        if isinstance(args[0], tuple):
            args = args[0]
            nargs = len(args)
        elif args[0] is None:
            args = None
            nargs = 1
    if nargs > 4:
        raise RectEditError('Invalid number of arguments')
    #
    if args is None:
        args = (0,) * 4
    elif nargs == 1:
        # 1 1 1 1
        args = args * 4
    elif nargs == 2:
        # 1 2 1 2
        args = args + args
    elif nargs == 3:
        # 1 2 3 2
        args = args + (args[1],)
    kwargs = dict(zip(keys, args))
    shorthand = Shorthand(**kwargs)
    return shorthand

def pairwise(iterable):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def setthisthat(toobj, toattr, fromobj, fromattr):
    setattr(toobj, toattr, getattr(fromobj, fromattr))

def iter_rect_points(rect):
    for attrname in RECTPOINTS:
        point = getattr(rect, attrname)
        yield (attrname, point)

def iter_rect_handles(rect, denom=4, minsize=10):
    size = min(rect.size) // 4
    if size < minsize:
        size = minsize
    for attrname, point in iter_rect_points(rect):
        if 'mid' in attrname:
            pass
        else:
            corner_rect = pygame.Rect((0,0),(size,)*2)
            setthisthat(corner_rect, attrname, rect, attrname)
            yield (attrname, corner_rect)

def layout_horizontal(rects, padding=0):
    "in-place move rects horizontally"
    for r1, r2 in pairwise(rects):
        r2.left = r1.right + padding

def vertical(rects, padding=0):
    "in-place move rects vertically"
    for r1, r2 in pairwise(rects):
        r2.top = r1.bottom + padding

def get_image(size, flags=None):
    if flags is None:
        flags = pygame.SRCALPHA
    return pygame.Surface(size, flags)

def draw_border(image, color, width):
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

def draw_hbar(image, color, width=1, **kwargs):
    "Horizontal bar"
    padding = shorthand(kwargs.get('padding'))
    rect = image.get_rect()
    rect.width -= padding.right + padding.left
    rect.height -= padding.bottom + padding.top
    rect.top += padding.top
    rect.left += padding.left
    pygame.draw.line(image, color, rect.midleft, rect.midright, width)

def draw_vbar(image, color, width=1, **kwargs):
    "Vertical bar"
    padding = shorthand(kwargs.get('padding'))
    rect = image.get_rect()
    rect.width -= padding.right + padding.left
    rect.height -= padding.bottom + padding.top
    rect.top += padding.top
    rect.left += padding.left
    pygame.draw.line(image, color, rect.midtop, rect.midbottom, width)

def draw_cross(image, color, width=1, **kwargs):
    "Cross shape"
    draw_hbar(image, color, width, **kwargs)
    draw_vbar(image, color, width, **kwargs)

def render_cross(size, color, linewidth=1, **kwargs):
    "create image and render a cross"
    imagekwargs = kwargs.get('imagekwargs', {})
    padding = kwargs.get('padding')
    if imagekwargs is None:
        imagekwargs = {}
    image = get_image(size, **imagekwargs)
    draw_cross(image, color, linewidth, padding=padding)
    return image

def render_minusbutton(size, color):
    """
    Opinionated minus button renderer
    """
    image = get_image(size)
    rect = image.get_rect()
    width = min(rect.size) // _button_width_denominator
    draw_hbar(image, color, width, padding=width)
    draw_border(image, color, width=width//2)
    return image

def render_plusbutton(size, color):
    """
    Opinionated plus button renderer
    """
    rect = pygame.Rect((0,0), size)
    width = min(rect.size) // _button_width_denominator
    image = render_cross(rect.size, color, linewidth=width, padding=width)
    draw_border(image, color, width=width//2)
    return image

def main(argv=None):
    parser = argparse.ArgumentParser()
    args = parser.parse_args(argv)
    #
    pygame.display.init()
    # XXX: LEFT OFF HERE
    # * unsure about the event system
    # * things need to know about each other. the command needs to modify
    #   RectEditor instance. OR another event? "add-rect" event?
    rectedit = RectEditor()
    rectedit.init()
    # add buttons
    size = (50,) * 2
    buttons = []
    # remove rect button
    image = render_minusbutton(size, (200,10,10))
    sprite = Sprite(image, image.get_rect(), props=dict(type='remove rect'))
    sprite.command = AddEditRectCommand()
    buttons.append(sprite)
    #
    image = render_plusbutton(size, (10,200,10))
    sprite = Sprite(image, image.get_rect(), props=dict(type='add rect'))
    sprite.command = AddEditRectCommand()
    buttons.append(sprite)
    for button in buttons:
        button.rect.left = rectedit.world.left + 10
        button.rect.bottom = rectedit.world.bottom - 10
        layout_horizontal((sprite.rect for sprite in buttons), 0)
    #
    rectedit.buttons.extend(buttons)
    #
    rectedit.loop()

if __name__ == '__main__':
    main()
