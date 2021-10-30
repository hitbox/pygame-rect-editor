from itertools import tee

def pairwise(iterable):
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def horizontal(rects, padding=0):
    "in-place move rects horizontally"
    for r1, r2 in pairwise(rects):
        r2.left = r1.right + padding

def vertical(rects, padding=0):
    "in-place move rects vertically"
    for r1, r2 in pairwise(rects):
        r2.top = r1.bottom + padding
