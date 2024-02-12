#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
import base64
import pychrome

import threading


urls = [
    "http://fatezero.org",
    "http://blog.fatezero.org",
    "http://github.com/fate0",
    "http://github.com/fate0/pychrome"
]


class EventHandler(object):
    pdf_lock = threading.Lock()

    def __init__(self, browser, tab):
        self.browser = browser
        self.tab = tab
        self.start_frame = None

    def frame_started_loading(self, frameId):
        if not self.start_frame:
            self.start_frame = frameId

    def frame_stopped_loading(self, frameId):
        if self.start_frame == frameId:
            self.tab.Page.stopLoading()

            with self.pdf_lock:
                # must activate current tab
                print(self.browser.activate_tab(self.tab.id))

                try:
                    data = self.tab.Page.printToPDF()

                    with open("%s.pdf" % time.time(), "wb") as fd:
                        fd.write(base64.b64decode(data['data']))
                finally:
                    self.tab.stop()


def close_all_tabs(browser):
    if len(browser.list_tab()) <= 1:
        return

    for tab in browser.list_tab()[1:]:
        try:
            tab.stop()
        except pychrome.RuntimeException:
            pass

        browser.close_tab(tab)

    time.sleep(1)
    assert len(browser.list_tab()) == 0


def main():
    browser = pychrome.Browser()

    close_all_tabs(browser)

    tabs = []
    for i in range(len(urls)):
        tabs.append(browser.new_tab())

    for i, tab in enumerate(tabs):
        eh = EventHandler(browser, tab)
        tab.Page.frameStartedLoading = eh.frame_started_loading
        tab.Page.frameStoppedLoading = eh.frame_stopped_loading

        tab.start()
        tab.Page.stopLoading()
        tab.Page.enable()
        tab.Page.navigate(url=urls[i])

    for tab in tabs:
        tab.wait(60)
        tab.stop()
        browser.close_tab(tab.id)

    print('Done')


if __name__ == '__main__':
    main()
