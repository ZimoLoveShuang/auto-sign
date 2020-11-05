url = 'http://127.0.0.1:8888'

import requests

res = requests.get(url)

print(res.text)
