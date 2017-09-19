import pychrome

# create a browser instance
browser = pychrome.Browser(url="http://127.0.0.1:9222")

# create a tab
tab = browser.new_tab()

# register callback if you want
def request_will_be_sent(**kwargs):
    print("loading: %s" % kwargs.get('request').get('url'))

tab.Network.requestWillBeSent = request_will_be_sent

# start the tab
tab.start()

# call method
tab.Network.enable()
# call method with timeout
tab.Page.navigate(url="https://github.com/fate0/pychrome", _timeout=5)

# wait for loading
tab.wait(5)

# stop the tab (stop handle events and stop recv message from chrome)
tab.stop()

# close tab
browser.close_tab(tab)
