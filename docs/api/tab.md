## class: Tab

#### attribute: id

tab id

#### attribute: type

tab type

#### attribute: status

tab status, could be `initial`, `started`, `stopped`

#### attribute: debug

example:
```python
import pychrome

browser = pychrome.Browser()
tab = browser.new_tab("http://www.fatezero.org")

tab.debug = True

tab.start()
tab.call_method("Network.enable")
tab.call_method("Page.navigate", url="https://github.com/fate0/pychrome", _timeout=5)
tab.stop()

browser.close_tab(tab)
```

output:
```
SEND ► {"method": "Network.enable", "id": 1001, "params": {}}
◀ RECV {"id":1001,"result":{}}
SEND ► {"method": "Page.navigate", "id": 1002, "params": {"url": "https://github.com/fate0/pychrome"}}
◀ RECV {"method":"Network.loadingFailed","params":{"requestId":"34905.1","timestamp":87792.94521,"type":"Other","errorText":"net::ERR_ABORTED","canceled":true}}
◀ RECV {"method":"Network.requestWillBeSent","params":{"requestId":"34905.2","loaderId":"34905.1","documentURL":"https://github.com/fate0/pychrome","request":{"url":"https://github.com/fate0/pychrome","method":"GET","headers":{"Upgrade-Insecure-Requests":"1","User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/62.0.3197.0 Safari/537.36"},"mixedContentType":"none","initialPriority":"VeryHigh","referrerPolicy":"no-referrer-when-downgrade"},"timestamp":87792.945539,"wallTime":1503817729.18642,"initiator":{"type":"other"},"type":"Document","frameId":"34905.1"}}
◀ RECV {"id":1002,"result":{"frameId":"34905.1"}}
```


#### start()
- return: bool

Start the tab's activity

#### stop()
- return: bool

#### wait([timeout])
- timeout: int
- return: bool

Wait until the tab stop or timeout

#### call_method()
- return: 

```python
import pychrome

browser = pychrome.Browser()
tab = browser.new_tab()

tab.call_method("Page.navigate", url="https://github.com/fate0/pychrome", _timeout=5)
tab.stop()
```

#### set_listener()
- return: bool

#### get_listener()
- return: bool

#### del_all_listeners()
- return: bool

delete all listeners
