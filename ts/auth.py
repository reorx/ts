# coding: utf-8

import urlparse
import oauth2 as oauth
from .config import get_config


class OauthError(Exception):
    pass


def cli_oauth():
    config = get_config()

    consumer_key = config['consumer_key']
    consumer_secret = config['consumer_secret']

    request_token_url = 'https://api.twitter.com/oauth/request_token?oauth_callback=oob'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    authorize_url = 'https://api.twitter.com/oauth/authorize'

    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)

    # Step 1: Get a request token
    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise OauthError('Invalid response {}.'.format(resp['status']))

    request_token = dict(urlparse.parse_qsl(content))

    print 'Request Token:'
    print '    - oauth_token        = %s' % request_token['oauth_token']
    print '    - oauth_token_secret = %s' % request_token['oauth_token_secret']
    print

    # Step 2: Redirect to the provider
    print 'Go to the following link in your browser:'
    print '%s?oauth_token=%s' % (authorize_url, request_token['oauth_token'])
    print

    accepted = 'n'
    while accepted.lower() == 'n':
        accepted = raw_input('Have you authorized me? (y/n) ')
    oauth_verifier = raw_input('What is the PIN? ')

    # Step 3: get access token & secret
    token = oauth.Token(
        request_token['oauth_token'],
        request_token['oauth_token_secret'])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urlparse.parse_qsl(content))
    access_key = access_token['oauth_token']
    access_secret = access_token['oauth_token_secret']

    print 'Access Token:'
    print '    - oauth_token        = %s' % access_key
    print '    - oauth_token_secret = %s' % access_secret
    print
    print 'You may now access protected resources using the access tokens above.'
    print

    return access_key, access_secret
