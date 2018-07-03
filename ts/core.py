# coding: utf-8

import os
import re
import sys
import argparse

from six.moves.urllib.parse import urlparse
from requests_oauthlib import OAuth1

from .httpclient import requests
from .auth import get_oauth_token
from .config import init_config, get_config, ConfigError, update_oauth_token, configure_proxy
from .utils import ObjectDict, unicode_format, quit, format_time, configure_logging, unescape_html
from .log import lg, requests_lg
from . import __version__, color


class ResponseError(Exception):
    pass


class TwitterAPI(object):
    base_url = 'https://api.twitter.com/1.1'
    uris = {
        'search': '/search/universal.json',
        #'status': '/statuses/lookup.json',
        'status': '/statuses/show.json',
    }

    def __init__(self, ckey, csecret, otoken, osecret):
        self.ckey = ckey
        self.csecret = csecret
        self.otoken = otoken
        self.osecret = osecret

        self.auth = OAuth1(self.ckey, self.csecret, self.otoken, self.osecret)

    def request(self, method, *args, **kwargs):
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

        resp = self.request('get', self._get_url('search'), params=params)
        # TODO error handling
        return resp

    def get_status(self, id):
        params = {
            'id': id,
            'include_entities': 'true',
        }
        resp = self.request('get', self._get_url('status'), params=params)
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

    # text may contain carriage returns `\r` which will not display on terminal
    # properly, replace them with `\n` instead
    text = t.text.replace(u'\r\n', u'\n').replace(u'\r', u'\n')

    fmt = u'{created_at} {screen_name}  {text}'
    s = unicode_format(
        fmt,
        created_at=color.fg256('aaa', format_time(t.created_at)),
        screen_name=color.blue(u.screen_name),
        text=unescape_html(text),
    )

    if link:
        url = u'https://twitter.com/{screen_name}/status/{id}'.format(
            screen_name=u.screen_name,
            id=t.id)
        s = u'{} {}'.format(s, color.underline(color.fg256('999', url)))
    print(s.encode('utf8'))


def search_query(api, query, count, lang, link):
    resp = api.search(
        query,
        count=count,
        lang=lang)
    requests_lg.debug('response content: %s', resp.content)

    show_search_result(resp.json(), link=link)


def download_media(api, id, download_dir, auto_name):
    """
    {
        "extended_entities": {
            "media": [
                {
                    "type": "photo",
                    "media_url_https": "https://pbs.twimg.com/media/Dg6xAuuU8AETsx3.jpg",
                    "media_url": "http://pbs.twimg.com/media/Dg6xAuuU8AETsx3.jpg",
                    ...
                },
                {
                    "type": "video",
                    "video_info": {
                        "variants": [
                            {
                                "url": "https://video.twimg.com/ext_tw_video/1013023146964742144/pu/vid/720x720/1e7hwwJp1IJhW-t4.mp4?tag=3",
                                "bitrate": 1280000,
                                "content_type": "video/mp4"
                            },
                            {
                                "url": "https://video.twimg.com/ext_tw_video/1013023146964742144/pu/vid/480x480/yKYIwj-bNd3mZ0Vj.mp4?tag=3",
                                "bitrate": 832000,
                                "content_type": "video/mp4"
                            },
                            {
                                "url": "https://video.twimg.com/ext_tw_video/1013023146964742144/pu/pl/YDxmuX9L6wq3bfd8.m3u8?tag=3",
                                "content_type": "application/x-mpegURL"
                            }
                        ]
                    },
                    ...
                }
            ]
        }
    }
    """
    # NOTE don't know what's wrong, but I cannot find media info for tweets contain gif,
    # it is said that type `animated_gif` should appear in `extended_entities`:
    # https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/extended-entities-object
    # but it just not worked.
    resp = api.get_status(id)
    #print(json.dumps(resp.json(), indent=2))
    data = resp.json()
    if 'extended_entities' not in data:
        print('No media found for tweet {}'.format(id))
        return

    count = 0
    for index, media in enumerate(data['extended_entities']['media']):
        media_type = media['type']
        if media_type == 'photo':
            url = media.get('media_url_https', media.get('media_url'))
            if not url:
                print('Warning: no media_url_https or media_url in photo media')
                continue
            download_file(api, url, download_dir, get_filename(id, index, url, auto_name))
            count += 1
        elif media_type == 'video':
            # get the biggest bitrate one
            vids = [i for i in media['video_info']['variants'] if 'bitrate' in i]
            vids.sort(key=lambda x: x['bitrate'], reverse=True)
            url = vids[0]['url']
            download_file(api, url, download_dir, get_filename(id, index, url, auto_name))
            count += 1
    if not count:
        print('No supported media found for tweet {}'.foramt(id))
    else:
        print('Done')


def download_file(api, url, download_dir, filename):
    #print('Download url: {}'.format(url))
    print('Downloading {} to {}'.format(filename, download_dir))
    resp = api.request('get', url)
    if resp.status_code > 299:
        raise ResponseError('{} failed with {}: {}'.format(resp.status_code, resp.text))

    content_len = resp.headers.get('Content-Length')
    if content_len:
        print('  size: {}'.format(bits_to_readable(float(content_len))))

    filepath = os.path.join(download_dir, filename)
    with open(filepath, 'wb') as f:
        for chunk in resp.iter_content():
            f.write(chunk)


def get_filename(id, index, url, auto_name):
    parts = match_filename(url)
    if not parts:
        return make_filename(id, index)
    name, ext = parts
    if auto_name:
        return make_filename(id, index, ext)
    else:
        return '{}.{}'.format(name, ext)


FILENAME_REGEX = re.compile(r'([^\/]+)\.(\w+)$')


def match_filename(url):
    """
    :return: name, ext
    """
    o = urlparse(url)
    rv = FILENAME_REGEX.search(o.path)
    if not rv:
        return None
    grps = rv.groups()
    if len(grps) != 2:
        print('Warning: match {} result not 2: {}'.format(url, grps))
        return None
    return grps


def make_filename(id, index, ext=None):
    s = id + '-' + str(index)
    if ext:
        s += '.' + ext
    return s


TWEET_ID_REGEX = re.compile(r'^(\d+)$')
TWEET_URL_ID_REGEX = re.compile(r'\/(\d+)$')


def get_tweet_id_from_url(url):
    v = TWEET_URL_ID_REGEX.search(url)
    if not v:
        return None
    return v.groups()[0]


SIZE_UNIT = 1024


def bits_to_readable(n):
    k = n / SIZE_UNIT
    if k > SIZE_UNIT:
        m = k / SIZE_UNIT
        return '{}M'.format(round(m, 1))
    else:
        return '{}K'.format(int(k))


def main():
    # the `formatter_class` can make description & epilog show multiline
    parser = argparse.ArgumentParser(
        description="Twitter Search CLI",
        epilog="",
        add_help=False,
        usage='%(prog)s [-c COUNT] [-l LANG] [--link] [-d] QUERY\n       %(prog)s [--init|--auth|--config CONFIG] [-d]',
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # search option group
    search_group = parser.add_argument_group('Search options')
    search_group.add_argument('query', metavar="QUERY", type=str, nargs='?', help="search query, see: https://dev.twitter.com/rest/public/search")
    search_group.add_argument('-c', dest='count', metavar="COUNT", type=int, default=50, help="set result number, by default it's 50")
    search_group.add_argument('-l', dest='lang', metavar="LANG", type=str, help="set search language (en, zh-cn), see: https://dev.twitter.com/rest/reference/get/help/languages")

    # display group
    display_group = parser.add_argument_group('Display options')
    display_group.add_argument('--link', action='store_true', help="append link with tweet")
    display_group.add_argument('-d', action='store_true', help="enable debug log")
    display_group.add_argument('-dd', action='store_true', help="debug deeper (more verbose)")

    # download images
    img_group = parser.add_argument_group('Image options')
    img_group.add_argument('--download-media', type=str, help="Download media by tweet id or url")
    img_group.add_argument('--auto-name', action='store_true', help="Automatically generates downloaded file names, if not passed, name in the url will be used.")
    img_group.add_argument('--download-dir', type=str, default=".", help="dir path to download media, by default it's current dir")

    # others
    other_group = parser.add_argument_group('Other options')
    other_group.add_argument('--init', action='store_true', help="init config file")
    other_group.add_argument('--auth', action='store_true', help="make authentication with twitter")
    other_group.add_argument('--config', type=str, nargs=1, choices=['proxy'], help="config ts, support arguments: `proxy`")
    other_group.add_argument('--version', action='store_true', help="show version number and exit")
    other_group.add_argument('-h', '--help', action='help', help="show this help message and exit")

    args = parser.parse_args()

    # Debug
    if args.d or args.dd:
        configure_logging(level='DEBUG', verbose=args.dd)

    lg.debug('args:%s', args)

    # Others
    # --version
    if args.version:
        print('ts {}'.format(__version__))
        quit(None, 0)

    # --init
    if args.init:
        init_config()
        quit(None, 0)

    try:
        config = get_config()
    except ConfigError as e:
        quit(str(e))
    lg.debug('config: {}'.format(config))

    def do_auth():
        otoken, osecret = get_oauth_token()
        update_oauth_token(config, otoken, osecret)

    # --auth
    if args.auth:
        do_auth()
        quit(None, 0)

    # --config
    if args.config:
        conf_key = args.config[0]
        if conf_key == 'proxy':
            configure_proxy(config)
        quit(None, 0)

    def get_api():
        if 'oauth_token' not in config or 'oauth_token_secret' not in config:
            do_auth()
        return TwitterAPI(
            config['consumer_key'], config['consumer_secret'],
            config['oauth_token'], config['oauth_token_secret'])

    # Download images
    if args.download_media:
        id_or_url = args.download_media
        if not TWEET_ID_REGEX.search(id_or_url):
            id_or_url = get_tweet_id_from_url(id_or_url)
        if not id_or_url:
            print('Invalid id or url: {}'.format(args.download_media))
            sys.exit(1)
        download_media(get_api(), id_or_url, args.download_dir, args.auto_name)
        return

    # Search
    if not args.query:
        quit('Please enter a QUERY', 1)
    search_query(get_api(), args.query, args.count, args.lang, args.link)
