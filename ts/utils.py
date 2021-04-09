# coding: utf-8

import sys
import logging.config
from dateutil import tz, parser
from html.parser import HTMLParser


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


def quit(s, code=1):
    if s is not None:
        print(s)
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
