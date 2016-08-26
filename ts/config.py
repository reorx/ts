# coding: utf-8

import os
import json


default_config_json = """
"""

config_filename = '.ts.config.json'
config_required_keys = ['consumer_key', 'consumer_secret']


class ConfigError(Exception):
    pass


def get_config():
    filepath = os.path.join(
        os.path.expanduser('~/'), config_filename)

    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except IOError as e:
        ConfigError('Could not open config file {}: {}'.format(config_filename, e))

    try:
        config = json.loads(content)
    except Exception as e:
        ConfigError('Could not parse config file {}: {}'.format(config_filename, e))

    for i in config_required_keys:
        if i not in config:
            ConfigError('`{}` is required in config file: {}'.format(i, e))

    return config
