## class: Browser

#### browser.new_tab([url][, timeout])
- `url` <[string]>
- `timeout` <[int]>
- return: <[Tab]>

example:
```python
import pychrome

browser = pychrome.Browser()
print(browser.new_tab("http://www.fatezero.org"))
```

output:
```
<Tab [0261adad-1b83-4d87-946f-08f0b50ca175]>
```

#### browser.list_tab([timeout])
- `timeout`
- return: list

example:
```python
import pychrome

browser = pychrome.Browser()
print(browser.list_tab())
```

output:
```
[<Tab [0261adad-1b83-4d87-946f-08f0b50ca175]>, <Tab [b0348512-d6da-45ed-b8d4-2849998c7f3e]>]
```

#### browser.activate_tab(tab_id[, timeout])
- `tab_id`
- return: string

example:
```python
import pychrome

browser = pychrome.Browser()
print(browser.activate_tab('0261adad-1b83-4d87-946f-08f0b50ca175'))
```

output:
```
Target activated
```

#### browser.close_tab(tab_id[, timeout])
- `tab_id`
- `timeout`

example:
```python
import pychrome

browser = pychrome.Browser()
print(browser.close_tab('0261adad-1b83-4d87-946f-08f0b50ca175'))
```

output:
```
Target is closing
```

#### browser.version([timeout])
- `timeout`
- return: string

example:
```python
import pychrome

browser = pychrome.Browser()
print(browser.version())
```

output:
```
{'webSocketDebuggerUrl': 'ws://127.0.0.1:9222/devtools/browser/36d5044d-4ef2-421b-b105-35c79edf7fea', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/62.0.3197.0 Safari/537.36', 'Protocol-Version': '1.2', 'Browser': 'HeadlessChrome/62.0.3197.0', 'WebKit-Version': '537.36 (@a19b1504d1a1f40e6c5358ec9880eb06b506b007)', 'V8-Version': '6.2.369'}
```
