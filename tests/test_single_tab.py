# -*- coding: utf-8 -*-

import time
import logging
import pychrome
import pytest

logging.basicConfig(level=logging.INFO)


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

def test_normal_callmethod(browser):
    tab = browser.new_tab()

    tab.start()
    result = tab.Page.navigate(url="http://www.fatezero.org")
    assert result['frameId']

    time.sleep(1)
    result = tab.Runtime.evaluate(expression="document.domain")

    assert result['result']['type'] == 'string'
    assert result['result']['value'] == 'www.fatezero.org'
    tab.stop()


def test_invalid_method(browser):
    tab = browser.new_tab()

    tab.start()
    try:
        tab.Page.NotExistMethod()
        assert False, "never get here"
    except pychrome.CallMethodException:
        pass
    tab.stop()


def test_invalid_params(browser):
    tab = browser.new_tab()

    tab.start()
    try:
        tab.Page.navigate()
        assert False, "never get here"
    except pychrome.CallMethodException:
        pass

    try:
        tab.Page.navigate("http://www.fatezero.org")
        assert False, "never get here"
    except pychrome.CallMethodException:
        pass

    try:
        tab.Page.navigate(invalid_params="http://www.fatezero.org")
        assert False, "never get here"
    except pychrome.CallMethodException:
        pass

    try:
        tab.Page.navigate(url="http://www.fatezero.org", invalid_params=123)
    except pychrome.CallMethodException:
        assert False, "never get here"

    tab.stop()


def test_set_event_listener(browser):
    tab = browser.new_tab()

    def request_will_be_sent(**kwargs):
        tab.stop()

    tab.start()
    tab.Network.requestWillBeSent = request_will_be_sent
    tab.Network.enable()

    try:
        tab.Page.navigate(url="chrome://newtab/")
    except pychrome.UserAbortException:
        pass

    if not tab.wait(timeout=5):
        assert False, "never get here"


def test_set_wrong_listener(browser):
    tab = browser.new_tab()

    tab.start()
    try:
        tab.Network.requestWillBeSent = "test"
        assert False, "never get here"
    except pychrome.RuntimeException:
        pass
    tab.stop()


def test_get_event_listener(browser):
    tab = browser.new_tab()

    def request_will_be_sent(**kwargs):
        tab.stop()

    tab.start()
    tab.Network.requestWillBeSent = request_will_be_sent
    tab.Network.enable()
    try:
        tab.Page.navigate(url="chrome://newtab/")
    except pychrome.UserAbortException:
        pass

    if not tab.wait(timeout=5):
        assert False, "never get here"

    assert tab.Network.requestWillBeSent == request_will_be_sent
    tab.Network.requestWillBeSent = None

    assert not tab.get_listener("Network.requestWillBeSent")
    # notice this
    assert tab.Network.requestWillBeSent != tab.get_listener("Network.requestWillBeSent")

    tab.stop()


def test_reuse_tab_error(browser):
    tab = browser.new_tab()

    def request_will_be_sent(**kwargs):
        tab.stop()

    tab.start()
    tab.Network.requestWillBeSent = request_will_be_sent
    tab.Network.enable()
    try:
        tab.Page.navigate(url="chrome://newtab/")
    except pychrome.UserAbortException:
        pass

    if not tab.wait(timeout=5):
        assert False, "never get here"

    try:
        tab.Page.navigate(url="http://www.fatezero.org")
        assert False, "never get here"
    except pychrome.RuntimeException:
        pass
    tab.stop()


def test_del_event_listener(browser):
    tab = browser.new_tab()
    test_list = []

    def request_will_be_sent(**kwargs):
        test_list.append(1)
        tab.Network.requestWillBeSent = None

    tab.start()
    tab.Network.requestWillBeSent = request_will_be_sent
    tab.Network.enable()
    tab.Page.navigate(url="chrome://newtab/")
    tab.Page.navigate(url="http://www.fatezero.org")

    if tab.wait(timeout=5):
        assert False, "never get here"

    assert len(test_list) == 1
    tab.stop()


def test_del_all_event_listener(browser):
    tab = browser.new_tab()
    test_list = []

    def request_will_be_sent(**kwargs):
        test_list.append(1)
        tab.del_all_listeners()

    tab.start()
    tab.Network.requestWillBeSent = request_will_be_sent
    tab.Network.enable()
    tab.Page.navigate(url="chrome://newtab/")

    if tab.wait(timeout=5):
        assert False, "never get here"

    assert len(test_list) == 1
    tab.stop()


class CallableClass(object):
    def __init__(self, tab):
        self.tab = tab

    def __call__(self, *args, **kwargs):
        self.tab.stop()


def test_use_callable_class_event_listener(browser):
    tab = browser.new_tab()

    tab.start()
    tab.Network.requestWillBeSent = CallableClass(tab)
    tab.Network.enable()
    try:
        tab.Page.navigate(url="chrome://newtab/")
    except pychrome.UserAbortException:
        pass

    if not tab.wait(timeout=5):
        assert False, "never get here"

    tab.stop()


def test_status(browser):
    tab = browser.new_tab()

    assert tab.status == pychrome.Tab.status_initial

    def request_will_be_sent(**kwargs):
        tab.stop()

    tab.Network.requestWillBeSent = request_will_be_sent

    assert tab.status == pychrome.Tab.status_initial

    tab.start()
    tab.Network.enable()
    assert tab.status == pychrome.Tab.status_started

    try:
        tab.Page.navigate(url="chrome://newtab/")
    except pychrome.UserAbortException:
        pass

    if not tab.wait(timeout=5):
        assert False, "never get here"

    tab.stop()
    assert tab.status == pychrome.Tab.status_stopped


def test_call_method_timeout(browser):
    tab = browser.new_tab()

    tab.start()
    tab.Page.navigate(url="chrome://newtab/", _timeout=5)

    try:
        tab.Page.navigate(url="http://www.fatezero.org", _timeout=0.8)
    except pychrome.TimeoutException:
        pass

    try:
        tab.Page.navigate(url="http://www.fatezero.org", _timeout=0.005)
    except pychrome.TimeoutException:
        pass

    tab.stop()


def test_callback_exception(browser):
    tab = browser.new_tab()

    def request_will_be_sent(**kwargs):
        raise Exception("test callback exception")

    tab.start()
    tab.Network.requestWillBeSent = request_will_be_sent
    tab.Network.enable()
    tab.Page.navigate(url="chrome://newtab/")

    if tab.wait(timeout=3):
        assert False, "never get here"

    tab.stop()
