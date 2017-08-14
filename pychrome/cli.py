# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import click
import pychrome


click.disable_unicode_literals_warning = True
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


shared_options = [
    click.option("--host", "-t", type=click.STRING, default='127.0.0.1', help="HTTP frontend host"),
    click.option("--port", "-p", type=click.INT, default=9222, help="HTTP frontend port"),
    click.option("--secure", "-s", is_flag=True, help="HTTPS/WSS frontend")
]


def add_shared_options(func):
    for option in shared_options:
        func = option(func)

    return func


class JSONTabEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pychrome.Tab):
            return obj._kwargs

        return super(JSONTabEncoder, self).default(self, obj)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(pychrome.__version__)
def main():
    pass


@main.command(context_settings=CONTEXT_SETTINGS)
@add_shared_options
def list(host, port, secure):
    """list all the available targets/tabs"""
    url = "%s://%s:%s" % ("https" if secure else "http", host, port)
    try:
        browser = pychrome.Browser(url)
        click.echo(json.dumps(browser.list_tab(), cls=JSONTabEncoder, indent=4))
    except Exception as e:
        click.echo(e)


@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument("url", required=False)
@add_shared_options
def new(host, port, secure, url="about:blank"):
    """create a new target/tab"""
    _url = "%s://%s:%s" % ("https" if secure else "http", host, port)

    try:
        browser = pychrome.Browser(_url)
        click.echo(json.dumps(browser.new_tab(url), cls=JSONTabEncoder, indent=4))
    except Exception as e:
        click.echo(e)


@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument("id")
@add_shared_options
def activate(host, port, secure, id):
    """activate a target/tab by id"""
    url = "%s://%s:%s" % ("https" if secure else "http", host, port)

    try:
        browser = pychrome.Browser(url)
        click.echo(browser.activate_tab(id))
    except Exception as e:
        click.echo(e)


@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument("id")
@add_shared_options
def close(host, port, secure, id):
    """close a target/tab by id"""
    url = "%s://%s:%s" % ("https" if secure else "http", host, port)

    try:
        browser = pychrome.Browser(url)
        click.echo(browser.close_tab(id))
    except Exception as e:
        click.echo(e)


@main.command(context_settings=CONTEXT_SETTINGS)
@add_shared_options
def version(host, port, secure):
    """show the browser version"""
    url = "%s://%s:%s" % ("https" if secure else "http", host, port)

    try:
        browser = pychrome.Browser(url)
        click.echo(json.dumps(browser.version(), indent=4))
    except Exception as e:
        click.echo(e)


if __name__ == '__main__':
    main()
