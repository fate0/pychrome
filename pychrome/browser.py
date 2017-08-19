#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import requests

from pychrome.tab import Tab

try:
    import Queue as queue
except ImportError:
    import queue


__all__ = ["Browser"]


class Browser(object):
    _all_tabs = {}

    def __init__(self, url="http://127.0.0.1:9222"):
        self.dev_url = url

        if self.dev_url not in self._all_tabs:
            self._tabs = self._all_tabs[self.dev_url] = {}
        else:
            self._tabs = self._all_tabs[self.dev_url]

    def new_tab(self, url=None, timeout=None):
        url = url or ''
        rp = requests.get("%s/json/new?%s" % (self.dev_url, url), json=True, timeout=timeout)
        tab = Tab(**rp.json())
        self._tabs[tab.id] = tab
        return tab

    def list_tab(self, timeout=None):
        rp = requests.get("%s/json" % self.dev_url, json=True, timeout=timeout)
        tabs_map = {}
        for tab_json in rp.json():
            if tab_json['type'] != 'page':
                continue

            if tab_json['id'] in self._tabs and self._tabs[tab_json['id']].status() != Tab.status_stopped:
                tabs_map[tab_json['id']] = self._tabs[tab_json['id']]
            else:
                tabs_map[tab_json['id']] = Tab(**tab_json)

        self._tabs = tabs_map
        return list(self._tabs.values())

    def activate_tab(self, tab_id, timeout=None):
        if isinstance(tab_id, Tab):
            tab_id = tab_id.id

        rp = requests.get("%s/json/activate/%s" % (self.dev_url, tab_id), timeout=timeout)
        return rp.text

    def close_tab(self, tab_id, timeout=None):
        if isinstance(tab_id, Tab):
            tab_id = tab_id.id

        rp = requests.get("%s/json/close/%s" % (self.dev_url, tab_id), timeout=timeout)
        self._tabs.pop(tab_id, None)
        return rp.text

    def version(self, timeout=None):
        rp = requests.get("%s/json/version" % self.dev_url, json=True, timeout=timeout)
        return rp.json()

    def __str__(self):
        return '<Browser %s>' % self.dev_url

    __repr__ = __str__
