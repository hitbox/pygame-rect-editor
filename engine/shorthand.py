from dataclasses import dataclass

from exceptions import RectEditError

@dataclass
class Shorthand:
    top: int
    right: int
    bottom: int
    left: int


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
