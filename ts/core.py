# coding: utf-8

import logging
import argparse
import requests
from requests_oauthlib import OAuth1
from .auth import get_oauth_token
from .config import init_config, get_config, ConfigError, update_oauth_token
from .utils import ObjectDict, unicode_format, quit, format_time
from .log import lg
from . import color


class TwitterAPI(object):
    base_url = 'https://api.twitter.com/1.1'
    uris = {
        'search': '/search/universal.json',
    }

    def __init__(self, ckey, csecret, otoken, osecret):
        self.ckey = ckey
        self.csecret = csecret
        self.otoken = otoken
        self.osecret = osecret

        self.auth = OAuth1(self.ckey, self.csecret, self.otoken, self.osecret)

    def _request(self, method, *args, **kwargs):
        kwargs['auth'] = self.auth
        return getattr(requests, method)(*args, **kwargs)

    def _get_url(self, name):
        return self.base_url + self.uris[name]

    def search(self, query, count=None, lang=None):
        # See twitter docs for query parameters:
        # https://dev.twitter.com/rest/public/search
        # https://dev.twitter.com/rest/public/timelines
        params = {
            'q': query,
        }
        if count is not None:
            params['count'] = count
        if lang is not None:
            params['lang'] = lang

        resp = self._request('get', self._get_url('search'), params=params)
        # TODO error handling
        return resp


def show_search_result(data, link=False):
    """
    {
        "modules": [
            {
                "status": "..."
            },
            ...
            {
                "suggestion": {"...": "..."}
            }
        ],
        "metadata": {
            "cursor": "TWEET-142630064025112576-686560615410737153-BD1UO2FFu9QAAAAAAAAETAAAAA...",
            "refresh_interval_in_sec": 30
        }
    }
    """
    # print json.dumps(data)
    for i in data['modules']:
        if 'status' in i:
            show_tweet(i['status'], link=link)


def show_tweet(d, link=False):
    """
    {
        "data": {
            "text": "Hello my little workbench😚 https://t.co/2SE7FSst2B",
            "is_quote_status": false,
            "id": 686560615410737200,
            "favorite_count": 0,
            "retweeted": false,
            "source": "<a href=\"http://instagram.com\" rel=\"nofollow\">Instagram</a>",
            "retweet_count": 0,
            "favorited": false,
            "user": {
                "id": 132736859,
                "media_count": 400,
                "profile_text_color": "333333",
                "profile_image_url_https": "https://pbs.twimg.com/profile_images/579924232685010944/obcxKbEE_normal.png",
                "profile_sidebar_fill_color": "DDEEF6",
                "followers_count": 327,
                "normal_followers_count": 327,
                "utc_offset": 28800,
                "statuses_count": 3370,
                "description": "An enthusiastic web developer. Love Python, and everything creative & life-changing.",
                "friends_count": 470,
                "location": "Shenzhen China",
                "followed_by": false,
                "following": false,
                "blocking": false,
                "screen_name": "novoreorx",
                "lang": "en",
                "favourites_count": 1233,
                "name": "mengxiao",
                "url": "https://t.co/IWOz07fGWU",
                "created_at": "Wed Apr 14 01:51:25 +0000 2010",
                "time_zone": "Beijing"
            },
            "geo": null,
            "lang": "en",
            "created_at": "Mon Jan 11 14:49:41 +0000 2016",
            "place": null
        },
        "metadata": {
            "...": "..."
        }
    }
    """
    t = ObjectDict(d['data'])
    u = ObjectDict(t['user'])
    fmt = u'{created_at} {screen_name}  {text}'
    s = unicode_format(
        fmt,
        created_at=color.fg256('aaa', format_time(t.created_at)),
        screen_name=color.blue(u.screen_name),
        text=t.text,
    )

    if link:
        url = u'https://twitter.com/{screen_name}/status/{id}'.format(
            screen_name=u.screen_name,
            id=t.id)
        s = u'{} {}'.format(s, color.underline(color.fg256('999', url)))
    print s.encode('utf8')


def main():
    # the `formatter_class` can make description & epilog show multiline
    parser = argparse.ArgumentParser(description="Twitter Search CLI", epilog="", formatter_class=argparse.RawDescriptionHelpFormatter)

    # arguments
    parser.add_argument('query', metavar="QUERY", type=str, nargs='?', help="search query, see: https://dev.twitter.com/rest/public/search")

    # options
    parser.add_argument('--init', action='store_true', help="init config file")
    parser.add_argument('-a', '--auth', action='store_true', help="make authentication with twitter")
    parser.add_argument('-c', '--count', type=int, default=50, help="result count")
    parser.add_argument('-l', '--lang', type=str, help="filter tweet language")
    parser.add_argument('--link', action='store_true', help="append link with tweet")
    parser.add_argument('-d', '--debug', action='store_true', help="enable debug log")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    if args.init:
        init_config()
        quit('', 0)

    try:
        config = get_config()
    except ConfigError as e:
        quit(str(e))

    lg.debug('config: {}'.format(config))

    if args.auth or ('oauth_token' not in config or 'oauth_token_secret' not in config):
        otoken, osecret = get_oauth_token()
        update_oauth_token(config, otoken, osecret)

    if not args.query:
        quit('', 0)

    api = TwitterAPI(
        config['consumer_key'], config['consumer_secret'],
        config['oauth_token'], config['oauth_token_secret'])

    resp = api.search(
        args.query,
        count=args.count,
        lang=args.lang)
    show_search_result(resp.json(), link=args.link)
