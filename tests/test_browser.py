# -*- coding: utf-8 -*-

import time
import logging
import pychrome
import os
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
    
    
def test_chome_version(browser):
    browser_version = browser.version()
    assert isinstance(browser_version, dict)


def test_browser_list(browser):
    tabs = browser.list_tab()
    assert len(tabs) == 0


def test_browser_new(browser):
    browser.new_tab()
    tabs = browser.list_tab()
    assert len(tabs) == 1


def test_browser_activate_tab(browser):
    tabs = []
    for i in range(10):
        tabs.append(browser.new_tab())

    for tab in tabs:
        browser.activate_tab(tab)


def test_browser_tabs_map(browser):
    tab = browser.new_tab()
    assert tab in browser.list_tab()
    assert tab in browser.list_tab()

    browser.close_tab(tab)
    assert tab not in browser.list_tab()


def test_browser_new_10_tabs(browser):
    tabs = []
    for i in range(10):
        tabs.append(browser.new_tab())

    time.sleep(1)
    assert len(browser.list_tab()) == 10

    for tab in tabs:
        browser.close_tab(tab.id)

    time.sleep(1)
    assert len(browser.list_tab()) == 0


def test_browser_new_100_tabs(browser):
    tabs = []
    for i in range(100):
        tabs.append(browser.new_tab())

    time.sleep(1)
    assert len(browser.list_tab()) == 100

    for tab in tabs:
        browser.close_tab(tab)

    time.sleep(1)
    assert len(browser.list_tab()) == 0
