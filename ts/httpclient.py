import functools
import requests as _requests
from .config import get_config
from .log import lg


class LazyRequests(object):
    allow_methods = ['get', 'post']
    user_agent = (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36')

    def __init__(self):
        self.configured = False
        self.config = None
        pass

    def _configure(self):
        if not self.configured:
            self.config = get_config()
            self.configured = True

    def __getattr__(self, key):
        if key not in self.allow_methods:
            raise AttributeError('{} is not an allowed method'.format(key, self.allow_methods))
        self._configure()

        kwargs = {
            'headers': {
                'User-Agent': self.user_agent,
            },
        }

        proxy = self.config.get('proxy')
        if proxy:
            kwargs['proxies'] = {
                'http': self.config['proxy'],
                'https': self.config['proxy'],
            }
            lg.debug('request use proxy: %s', proxy)

        request_func = getattr(_requests, key)
        return functools.partial(request_func, **kwargs)

requests = LazyRequests()
