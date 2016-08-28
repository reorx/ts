# coding: utf-8

import os
import json
from . import color


default_config_json = """
"""

config_filename = '.ts.config.json'
config_required_keys = ['consumer_key', 'consumer_secret']

# global single config object
_config_object = None


class ConfigError(Exception):
    pass


def get_config_path():
    return os.path.join(
        os.path.expanduser('~/'), config_filename)


def get_config():
    global _config_object

    if _config_object is None:
        try:
            with open(get_config_path(), 'r') as f:
                content = f.read()
        except IOError as e:
            msg = (
                'Could not open config file {}: {}\n'
                'You can run `ts --init` to initialize a config file'
            )
            raise ConfigError(
                msg.format(config_filename, e))

        try:
            config = json.loads(content)
        except Exception as e:
            raise ConfigError('Could not parse config file {}: {}'.format(config_filename, e))

        for i in config_required_keys:
            if i not in config:
                ConfigError('`{}` is required in config file: {}'.format(i, e))

        _config_object = config

    return _config_object


def init_config():
    print 'Get the {} consumer key pairs at {} (or use any other one if you are confident)'.format(
        color.blue_hl('TweetDeck'),
        color.blue(color.underline('https://gist.github.com/mariotaku/5465786')))
    ckey = raw_input('Enter consumer_key: ')
    csecret = raw_input('Enter consumer_secret: ')
    d = {
        'consumer_key': ckey,
        'consumer_secret': csecret,
    }

    filepath = write_config(d)
    print 'Config was wrote to {}'.format(filepath)


def write_config(d):
    filepath = get_config_path()
    with open(filepath, 'w') as f:
        f.write(json.dumps(d, indent=4))
    return filepath


def update_oauth_token(config, otoken, osecret):
    config['oauth_token'] = otoken
    config['oauth_token_secret'] = osecret
    write_config(config)
    print 'Config oauth token updated'


def configure_proxy(config):
    print 'Set proxy address, format: ' + color.underline(color.blue('http[s]://[user][:pass]<address>:<port>'))
    print color.fg256(
        '888',
        'If you want to use socks proxy, see: '
        'http://docs.python-requests.org/en/master/user/advanced/#socks for detail.')
    proxy = raw_input('Enter proxy address (leave empty to remove): ').strip()
    if proxy:
        config['proxy'] = proxy
    else:
        print 'Remove proxy in config'
        if 'proxy' in config:
            del config['proxy']
    write_config(config)
    print 'Config proxy updated'
