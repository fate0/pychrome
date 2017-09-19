import pychrome

browser = pychrome.Browser(url="http://127.0.0.1:9222")
tab = browser.new_tab()

def request_will_be_sent(**kwargs):
    print("loading: %s" % kwargs.get('request').get('url'))


tab.set_listener("Network.requestWillBeSent", request_will_be_sent)

tab.start()
tab.call_method("Network.enable")
tab.call_method("Page.navigate", url="https://github.com/fate0/pychrome", _timeout=5)

tab.wait(5)
tab.stop()

browser.close_tab(tab)
