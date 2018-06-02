# -*- coding: utf-8 -*-

import time
import logging
import pychrome
import functools
import pytest


logging.basicConfig(level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)

@pytest.fixture(scope='session')  # one server to rule'em all
def browser():  
    # A bug in Travis-CI's testing environment requires that chrome requires
    # sudo access to set up the sandbox. Hence we turn it off.
    # A regular environment  does not need these service args
    service_args = ['--no-sandbox', '--disable-gpu']
    
    with pychrome.Browser(service_args=service_args) as browser:
        yield browser
        
@pytest.fixture(autouse=True)
def run_around_tests(browser):
    # Code that will run before each test:
    close_all_tabs(browser)
    # Run test
    yield
	
def close_all_tabs(browser):
    if len(browser.list_tab()) == 0:
        return

    for tab in browser.list_tab():
        browser.close_tab(tab)

    time.sleep(1)
    assert len(browser.list_tab()) == 0


def new_multi_tabs(b, n):
    tabs = []
    for i in range(n):
        tabs.append(b.new_tab())

    return tabs


def test_normal_callmethod(browser):
    tabs = new_multi_tabs(browser, 10)

    for tab in tabs:
        tab.start()
        result = tab.Page.navigate(url="http://www.fatezero.org")
        assert result['frameId']

    time.sleep(3)

    for tab in tabs:
        result = tab.Runtime.evaluate(expression="document.domain")
        assert result['result']['type'] == 'string'
        assert result['result']['value'] == 'www.fatezero.org'
        tab.stop()


def test_set_event_listener(browser):
    tabs = new_multi_tabs(browser, 10)

    def request_will_be_sent(tab, **kwargs):
        tab.stop()

    for tab in tabs:
        tab.start()
        tab.Network.requestWillBeSent = functools.partial(request_will_be_sent, tab)
        tab.Network.enable()
        try:
            tab.Page.navigate(url="chrome://newtab/")
        except pychrome.UserAbortException:
            pass

    for tab in tabs:
        if not tab.wait(timeout=5):
            assert False, "never get here"
        tab.stop()
