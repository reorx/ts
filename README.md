# ts

![Screen Shot](screenshot.png)

Twitter Search CLI

## Install

    pip install ts


## Usage

Before actual usage, you need to initialize config file first:

    ts --init

The first time you run ts, it will guide you through an OAuth authentication process.
The tokens will be stored at `~/.ts.config.json`, any time you want refresh the tokens, run:

    ts --auth

to make authentication again and update the tokens in config.

The search syntax is the same as [Twitter Web Search](https://twitter.com/search-home) or
[Twitter Search API](https://dev.twitter.com/rest/public/search).
Here are some common search query examples:

1. Find what a person had said:

        ts 'from:NASA Elon Musk'

2. Find what people said to a person in a topic:

        ts '#Hearthstone to:bdbrode'

Run `ts -h` to see complete usage instructions:

```
usage: ts [-c COUNT] [-l LANG] [--link] [-d] QUERY
       ts [--init|--auth|--config CONFIG] [-d]

Twitter Search CLI

Search options:
  QUERY             search query, see:
                    https://dev.twitter.com/rest/public/search
  -c COUNT          set result number, by default it's 50
  -l LANG           set search language (en, zh-cn), see:
                    https://dev.twitter.com/rest/reference/get/help/languages

Display options:
  --link            append link with tweet
  -d                enable debug log
  -dd               debug deeper (more verbose)

Other options:
  --init            init config file
  --auth            make authentication with twitter
  --config {proxy}  config ts, support arguments: `proxy`
  -h, --help        show this help message and exit
```

## Proxy

ts supports proxying, you can set proxy by run ``ts --config proxy``,
a proxy address is something like `http://localhost:1000` or `https://user:pass@fast.proxy.com`.

Note that by default ts only supports HTTP(S) proxying, if you want to use socks5 proxy,
you'll need to install `requests[socks]` before using it. For more information see
[requests document](http://docs.python-requests.org/en/master/user/advanced/#socks).
