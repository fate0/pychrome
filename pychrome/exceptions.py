#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals


class PyChromeException(Exception):
    pass


class UserAbortException(PyChromeException):
    pass


class TabConnectionException(PyChromeException):
    pass


class CallMethodException(PyChromeException):
    pass


class TimeoutException(PyChromeException):
    pass


class RuntimeException(PyChromeException):
    pass
