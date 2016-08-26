# coding: utf-8

from fabulous import color


def test_named_colors():
    for i in ['red', 'green', 'blue', 'yellow', 'magenta']:
        print getattr(color, i)(i)


def test_256_colors():
    for i in (range(10) + ['a', 'b', 'c', 'd', 'e', 'f']):
        hex = '#' + str(i) * 3
        print color.fg256(hex, hex)


def test_decorations():
    for i in ['underline', 'underline2', 'strike']:
        print getattr(color, i)(i)
