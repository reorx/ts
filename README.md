# ts

Twitter Search CLI

## Install

    pip install ts


## Usage

Before actual usage, you need to initialize config file first:

    ts --init

The first time you run ts, it will guide you through an OAuth authentication process.
The tokens will be stored at `~/.ts.config.json`, any time you want to, run:

    ts -a

to make authentication again and update the tokens.

The search syntax is the same as [Twitter Web Search](https://twitter.com/search-home) or
[Twitter Search API](https://dev.twitter.com/rest/public/search).
Here are some common search query examples:

1. Find what a person had said:

        ts 'from:NASA Elon Musk'

2. Find what people said to a person in a topic:

        ts '#Hearthstone to:bdbrode'
