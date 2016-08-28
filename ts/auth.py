# coding: utf-8

import urlparse
from requests_oauthlib import OAuth1
from .httpclient import requests
from .config import get_config
from .log import lg
from . import color


class OauthError(Exception):
    pass


def get_oauth_token():
    config = get_config()

    consumer_key = config['consumer_key']
    consumer_secret = config['consumer_secret']

    request_token_url = 'https://api.twitter.com/oauth/request_token?oauth_callback=oob'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    authorize_url = 'https://api.twitter.com/oauth/authorize'

    # consumer = oauth.Consumer(consumer_key, consumer_secret)
    # client = oauth.Client(consumer)
    oauth = OAuth1(consumer_key, client_secret=consumer_secret)

    # Step 1: Get a request token

    resp = requests.post(request_token_url, auth=oauth)
    if resp.status_code != 200:
        raise OauthError(
            'Invalid response on request token {} {}.'.format(resp.status_code, resp.content))
    request_token = dict(urlparse.parse_qsl(resp.content))
    lg.debug('Request token (oauth_token, oauth_token_secret): %s, %s',
             request_token['oauth_token'], request_token['oauth_token_secret'])

    # Step 2: Redirect to the provider
    print 'Go to the following link in your browser:'
    print color.blue(color.underline('%s?oauth_token=%s' % (authorize_url, request_token['oauth_token'])))
    print

    verifier = raw_input('Enter PIN: ')
    print

    # Step 3: get access token & secret
    oauth = OAuth1(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=request_token['oauth_token'],
        resource_owner_secret=request_token['oauth_token_secret'],
        verifier=verifier)

    resp = requests.post(access_token_url, auth=oauth)
    if resp.status_code != 200:
        raise OauthError(
            'Invalid response on access token {} {}.'.format(resp.status_code, resp.content))

    access_token = dict(urlparse.parse_qsl(resp.content))
    access_key = access_token['oauth_token']
    access_secret = access_token['oauth_token_secret']

    print 'Access Token:'
    print '  - oauth_token        = %s' % access_key
    print '  - oauth_token_secret = %s' % access_secret
    print

    return access_key, access_secret
