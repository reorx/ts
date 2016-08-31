# coding: utf-8

import sys
import logging.config
from dateutil import tz, parser
from HTMLParser import HTMLParser


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


html_parser = HTMLParser()


def unescape_html(s):
    return html_parser.unescape(s)


def configure_logging(level='INFO', verbose=False):
    dep_logger = {
        'level': level,
    }
    if not verbose:
        dep_logger['level'] = 'CRITICAL'

    logconf = {
        'version': 1,
        'disable_existing_loggers': False,
        'loggers': {
            '': {
                'handlers': ['stream'],
                'level': level,
            },
            'requests_oauthlib': dep_logger,
            'oauthlib': dep_logger,
            'requests': dep_logger,
        },
        'handlers': {
            'stream': {
                'class': 'logging.StreamHandler',
                'formatter': 'common',
            },
        },
        'formatters': {
            'common': {
                'format': '[%(name)s] [%(levelname)s %(asctime)s] %(message)s',
                'datefmt': '%H:%M:%S'
            },
        },
    }
    logging.config.dictConfig(logconf)


def unicode_format(fmt, **kwargs):
    new_kwargs = {}
    for k, v in kwargs.iteritems():
        new_kwargs[k] = to_unicode(v)
    return to_unicode(fmt).format(**new_kwargs)


def quit(s, code=1):
    if s is not None:
        print s
    sys.exit(code)


def format_time(s, fmt='%Y/%m/%d %H:%M', timezone=None):
    dt = parser.parse(s)
    if timezone:
        tzo = tz.gettz()
    else:
        tzo = tz.gettz(timezone)
    localdt = dt.astimezone(tzo)
    return localdt.strftime(fmt)


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
