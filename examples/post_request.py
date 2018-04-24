import pychrome
import time
import urllib



class ChromiumClient(object):
    """ Client to interact with Chromium """

    def __init__(self):
        self.browser = pychrome.Browser(url="http://127.0.0.1:9222")

    def do_post(self):
        self.tab = self.browser.new_tab()

        event_handler = EventHandler()

        event_handler.set_token('asdkflj497564dsklf')
        event_handler.set_post_data({
            'param1': 'value1',
            'param2': 'value2'
        })

        url_pattern_object = {'urlPattern': '*fate0*'}
        self.tab.Network.setRequestInterception(patterns=[url_pattern_object])

        self.tab.Network.requestIntercepted = event_handler.on_request_intercepted

        self.tab.start()

        self.tab.Network.enable()
        self.tab.Page.enable()

        self.tab.Page.navigate(url='https://github.com/fate0/pychrome')

        self.tab.wait(5)
        self.tab.stop()

        self.browser.close_tab(self.tab.id)


class EventHandler(object):
    def __init__(self):
        self.tab = None
        self.token = None
        self.is_first_request = False
        self.post_data = {}

    def set_tab(self, t):
        self.tab = t

    def set_token(self, t):
        self.token = t

    def set_post_data(self, pd):
        self.post_data = pd

    def on_request_intercepted(self, **kwargs):
        new_args = {'interceptionId': kwargs['interceptionId']}

        if self.is_first_request:
            # Modify first request only, following are media/static
            # requests...
            self.is_first_request = False

            extra_headers = {
                'Requested-by': 'Chromium',
                'Authorization': 'Token ' + self.token
            }

            request = kwargs.get('request')
            request['headers'].update(extra_headers)

            new_args.update({
                'url': request['url'],
                'method': 'POST',
                'headers': request['headers'],
                'postData': urllib.urlencode(self.post_data)
            })

        self.tab.Network.continueInterceptedRequest(**new_args)


if __name__ == '__main__':
    client = ChromiumClient()

    client.do_post()