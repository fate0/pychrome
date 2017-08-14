#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import logging
import warnings
import functools
import threading

import websocket

from pychrome.exceptions import *

try:
    import Queue as queue
except ImportError:
    import queue


__all__ = ["Tab"]


logger = logging.getLogger(__name__)


class GenericAttr(object):
    def __init__(self, name, tab):
        self.__dict__['name'] = name
        self.__dict__['tab'] = tab

    def __getattr__(self, item):
        method_name = "%s.%s" % (self.name, item)
        event_listener = self.tab.get_listener(method_name)

        if event_listener:
            return event_listener

        return functools.partial(self.tab.call_method, method_name)

    def __setattr__(self, key, value):
        self.tab.set_listener("%s.%s" % (self.name, key), value)


class Tab(object):
    status_initial = 'initial'
    status_started = 'started'
    status_stopped = 'stopped'

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.url = kwargs.get("url")
        self.title = kwargs.get("title")
        self.type = kwargs.get("type")
        self.websocket_url = kwargs.get("webSocketDebuggerUrl")
        self.desc = kwargs.get("description")

        self.origin_json = kwargs

        self.cur_id = 1000
        self.event_handlers = {}
        self.method_results = {}
        self.event_queue = queue.Queue()

        self.ws = None
        self.ws_send_lock = threading.Lock()

        self.recv_th = threading.Thread(target=self._recv_loop)
        self.recv_th.daemon = True
        self.handle_event_th = threading.Thread(target=self._handle_event_loop)
        self.handle_event_th.daemon = True

        self._stopped = threading.Event()
        self._started = threading.Event()

    def _init(self):
        if self._started.is_set():
            return

        if not self.websocket_url:
            raise RuntimeException("Already has another client connect to this tab")

        self._started.set()
        self._stopped.clear()
        self.ws = websocket.create_connection(self.websocket_url)
        self.recv_th.start()
        self.handle_event_th.start()

    def _send(self, message, timeout=None):
        if 'id' not in message:
            self.cur_id += 1
            message['id'] = self.cur_id

        logger.debug("[*] send message: %s %s" % (message["id"], message['method']))
        self.method_results[message['id']] = queue.Queue()

        with self.ws_send_lock:
            self.ws.send(json.dumps(message))

        if not isinstance(timeout, (int, float)) or timeout > 1:
            q_timeout = 1
        else:
            q_timeout = timeout / 2.0

        try:
            while not self._stopped.is_set():
                try:
                    if isinstance(timeout, (int, float)):
                        if timeout < q_timeout:
                            q_timeout = timeout

                        timeout -= q_timeout

                    return self.method_results[message['id']].get(timeout=q_timeout)
                except queue.Empty:
                    if isinstance(timeout, (int, float)) and timeout <= 0:
                        raise TimeoutException("Calling %s timeout" % message['method'])

                    continue

            raise UserAbortException("User abort, call stop() when calling %s" % message['method'])
        finally:
            self.method_results.pop(message['id'], None)

    def _recv_loop(self):
        while not self._stopped.is_set():
            try:
                self.ws.settimeout(1)
                message = json.loads(self.ws.recv())
            except websocket.WebSocketTimeoutException:
                continue
            except (websocket.WebSocketConnectionClosedException, OSError):
                return

            if "method" in message:
                logger.debug("[*] recv event: %s" % message["method"])
                self.event_queue.put(message)

            elif "id" in message:
                logger.debug("[*] recv message: %s" % message["id"])
                if message["id"] in self.method_results:
                    self.method_results[message['id']].put(message)
            else:
                logger.warning("[-] unknown message: %s" % message)

    def _handle_event_loop(self):
        while not self._stopped.is_set():
            try:
                event = self.event_queue.get(timeout=1)
            except queue.Empty:
                continue

            if event['method'] in self.event_handlers:
                try:
                    self.event_handlers[event['method']](**event['params'])
                except Exception as e:
                    logger.error("[-] callback %s error: %s" % (event['method'], str(e)))
                    warnings.warn("callback %s error: %s" % (event['method'], str(e)))

    def __getattr__(self, item):
        attr = GenericAttr(item, self)
        setattr(self, item, attr)
        return attr

    def call_method(self, _method, *args, **kwargs):
        if args:
            raise CallMethodException("the params should be key=value format")

        if self._stopped.is_set():
            raise RuntimeException("Tab has been stopped")

        self._init()
        timeout = kwargs.pop("_timeout", None)
        result = self._send({"method": _method, "params": kwargs}, timeout=timeout)
        if 'result' not in result and 'error' in result:
            logger.error("[-] %s error: %s" % (_method, result['error']['message']))
            raise CallMethodException("calling method: %s error: %s" % (_method, result['error']['message']))

        return result['result']

    def set_listener(self, event, callback):
        if not callback:
            return self.event_handlers.pop(event, None)

        if not callable(callback):
            raise RuntimeException("callback should be callable")

        self.event_handlers[event] = callback
        return True

    def get_listener(self, event):
        return self.event_handlers.get(event, None)

    def del_all_listeners(self):
        self.event_handlers = {}
        return True

    def status(self):
        if not self._started.is_set() and not self._stopped.is_set():
            return Tab.status_initial
        if self._started.is_set() and not self._stopped.is_set():
            return Tab.status_started
        if self._started.is_set() and self._stopped.is_set():
            return Tab.status_stopped
        else:
            raise RuntimeException("Tab Unknown status")

    def stop(self):
        if self._stopped.is_set():
            raise RuntimeException("Tab has been stopped")

        if not self._started.is_set():
            raise RuntimeException("Tab is not running")

        logger.debug("[*] stop tab %s" % self.id)

        self._stopped.set()
        self.ws.close()

    def wait(self, timeout=None):
        self._init()
        return self._stopped.wait(timeout)

    def __str__(self):
        return "<Tab [%s] %s>" % (self.id, self.url)

    __repr__ = __str__
