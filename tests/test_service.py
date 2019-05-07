# -*- coding: utf-8 -*-

import time
import logging
import pychrome
import os
import pytest

logging.basicConfig(level=logging.INFO)
   
    
def test_wrong_executable():
    with pytest.raises(pychrome.service.ChromeException) as e_info:
        with pychrome.Browser(executable="something_nonexistant") as browser:
            assert False, "Never get here"        

def test_killed_process():
    with pytest.raises(pychrome.service.ChromeException) as e_info:
        with pychrome.Browser(executable="something_nonexistant") as browser:
            browser.service.process.kill()
            tab = browser.new_tab()
            assert False, "Never get here"
        
def test_lost_connection():
    with pytest.raises(pychrome.service.ChromeException) as e_info:
        with pychrome.Browser(executable="something_nonexistant") as browser:
            browser.service.port += 1
            tab = browser.new_tab()
            assert False, "Never get here"
