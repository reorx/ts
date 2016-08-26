# coding: utf-8

import json
import arrow
import logging
import argparse
import requests
from requests_oauthlib import OAuth1
from .auth import cli_oauth
from .config import get_config
from .utils import ObjectDict, unicode_format


lg = logging.getLogger('ts')


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

    def search(self, query, count=None):
        params = {
            'q': query,
        }
        if count is not None:
            params['count'] = count
        resp = self._request('get', self._get_url('search'), params=params)
        # TODO error handling
        return resp


def show_search_result(data):
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
            show_tweet(i['status'])


def show_tweet(d):
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
    fmt = u'{screen_name} {created_at}  {text}'
    s = unicode_format(
        fmt,
        screen_name=u.screen_name,
        created_at=format_time(t.created_at),
        text=t.text,
    )
    print s.encode('utf8')


def format_time(s, timezone='Asia/Shanghai'):
    dt = arrow.get(s, 'ddd MMM DD HH:mm:ss Z YYYY')
    dt.to(timezone)
    return dt.format('YYYY/MM/DD HH:mm')


def main():
    # the `formatter_class` can make description & epilog show multiline
    parser = argparse.ArgumentParser(description="", epilog="", formatter_class=argparse.RawDescriptionHelpFormatter)

    # arguments
    parser.add_argument('query', metavar="QUERY", type=str, help="")

    # options
    parser.add_argument('-a', '--auth', action='store_true', help="")
    parser.add_argument('-c', '--count', type=int, default=50, help="")
    parser.add_argument('-l', '--link', action='store_true', help="")
    parser.add_argument('-d', '--debug', action='store_true', help="")

    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    # cli_oauth()
    config = get_config()
    lg.debug('config: {}'.format(config))

    api = TwitterAPI(
        config['consumer_key'], config['consumer_secret'],
        config['oauth_token'], config['oauth_token_secret'])

    resp = api.search(args.query, args.count)
    show_search_result(resp.json())
