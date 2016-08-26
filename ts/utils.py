# coding: utf-8

import sys


PY3 = sys.version_info >= (3,)


def to_unicode(value):
    """Converts a string argument to a unicode string.

    If the argument is already a unicode string or None, it is returned
    unchanged.  Otherwise it must be a byte string and is decoded as utf8.
    """
    if PY3:
        return value
    else:
        if isinstance(value, str):
            return value.decode("utf-8")
        return unicode(value)


def unicode_format(fmt, **kwargs):
    new_kwargs = {}
    for k, v in kwargs.iteritems():
        new_kwargs[k] = to_unicode(v)
    return to_unicode(fmt).format(**new_kwargs)


def quit(s, code=1):
    print s
    sys.exit(code)


class ObjectDict(dict):
    """
    retrieve value of dict in dot style
    """
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError('Has no attribute %s' % key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)

    def __str__(self):
        return '<ObjectDict %s >' % dict(self)
