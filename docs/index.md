# pychrome

[![Build Status](https://travis-ci.org/fate0/pychrome.svg?branch=master)](https://travis-ci.org/fate0/pychrome)
[![Codecov](https://img.shields.io/codecov/c/github/fate0/pychrome.svg)](https://codecov.io/gh/fate0/pychrome)
[![Updates](https://pyup.io/repos/github/fate0/pychrome/shield.svg)](https://pyup.io/repos/github/fate0/pychrome/)
[![PyPI](https://img.shields.io/pypi/v/pychrome.svg)](https://pypi.python.org/pypi/pychrome)
[![PyPI](https://img.shields.io/pypi/pyversions/pychrome.svg)](https://github.com/fate0/pychrome)

A Python Package for the Google Chrome Dev Protocol

## Table of Contents

* [Installation](#installation)
* [Setup Chrome](#setup-chrome)
* [Getting Started](#getting-started)
* [Tab management](#tab-management)
* [Examples](#examples)
* [Ref](#ref)


## Installation

To install pychrome, simply:

```
$ pip install -U git+https://github.com/fate0/pychrome.git
```

or from pypi:

```
$ pip install -U pychrome
```

or from source:

```
$ python setup.py install
```

## Setup Chrome

simply:

```
$ google-chrome --remote-debugging-port=9222
```

or headless mode (chrome version >= 59):

```
$ google-chrome --headless --disable-gpu --remote-debugging-port=9222
```

or use docker:

```
$ docker pull fate0/headless-chrome
$ docker run -it --rm --cap-add=SYS_ADMIN -p9222:9222 fate0/headless-chrome
```

## Getting Started

``` python
# create a browser instance
browser = pychrome.Browser(url="http://127.0.0.1:9222")

# list all tabs (default has a blank tab)
tabs = browser.list_tab()

if not tabs:
    tab = browser.new_tab()
else:
    tab = tabs[0]


# register callback if you want
def request_will_be_sent(**kwargs):
    print("loading: %s" % kwargs.get('request').get('url'))

tab.Network.requestWillBeSent = request_will_be_sent

# call method
tab.Network.enable()
# call method with timeout
tab.Page.navigate(url="https://github.com/fate0/pychrome", _timeout=5)

# wait for loading
tab.wait(5)

# stop tab (stop handle events and stop recv message from chrome)
tab.stop()

# close tab
browser.close_tab(tab)

```

or (alternate syntax)

``` python
browser = pychrome.Browser(url="http://127.0.0.1:9222")

tabs = browser.list_tab()
if not tabs:
    tab = browser.new_tab()
else:
    tab = tabs[0]


def request_will_be_sent(**kwargs):
    print("loading: %s" % kwargs.get('request').get('url'))


tab.set_listener("Network.requestWillBeSent", request_will_be_sent)

tab.call_method("Network.enable")
tab.call_method("Page.navigate", url="https://github.com/fate0/pychrome", _timeout=5)

tab.wait(5)
tab.stop()

browser.close_tab(tab)
```

more methods or events could be found in
[Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/tot/)


## Tab management

run `pychrome -h` for more info

example:
```
$ pychrome new http://www.fatezero.org
{
    "description": "",
    "url": "http://www.fatezero.org/",
    "webSocketDebuggerUrl": "ws://127.0.0.1:9222/devtools/page/557d8315-e909-466c-bf20-f5a6133ebd89",
    "id": "557d8315-e909-466c-bf20-f5a6133ebd89",
    "type": "page",
    "devtoolsFrontendUrl": "/devtools/inspector.html?ws=127.0.0.1:9222/devtools/page/557d8315-e909-466c-bf20-f5a6133ebd89",
    "title": ""
}

$ pychrome close 557d8315-e909-466c-bf20-f5a6133ebd89
Target is closing
```

## Examples

please see the [examples](http://github.com/fate0/pychrome/blob/master/examples) directory for more examples


## Ref

* [chrome-remote-interface](https://github.com/cyrus-and/chrome-remote-interface/)
* [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/tot/)
